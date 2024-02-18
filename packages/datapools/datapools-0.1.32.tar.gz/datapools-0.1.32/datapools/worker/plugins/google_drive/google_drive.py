# import os
# import asyncio
# import io
import traceback

from google.auth.api_key import Credentials

# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseDownload

from ....common.logger import logger
from ....common.storage import BaseStorage
from ....common.types import CrawlerContent, DatapoolContentType
from ..base_plugin import BasePlugin, BasePluginException, WorkerTask

# from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


class GoogleDrivePlugin(BasePlugin):
    def __init__(self, ctx, api_key):
        super().__init__(ctx)
        self.creds = Credentials(api_key)

    # https://drive.google.com/drive/folders/1CPDmula2V83KWOocJR9jVvsTk6tVSpKd?usp=sharing

    @staticmethod
    def is_supported(url):
        u = BasePlugin.parse_url(url)
        if u.netloc == "drive.google.com":
            if u.path[0:15] == "/drive/folders/":
                return True

        return False

    async def process(self, task: WorkerTask):
        u = self.parse_url(task.url)
        folder_id = u.path.split("/")[3]

        try:
            with build("drive", "v3", credentials=self.creds) as drive:
                self.tag_id = await self.find_license(folder_id, drive)
                if self.tag_id and self.tag_id.is_crawling_allowed():
                    async for msg in self.scan_folder(folder_id, drive):
                        yield msg
        except Exception as e:
            logger.error(f"GoogleDrivePlugin exception {e}")
            logger.error(traceback.format_exc())

    def _get_download_url(self, file_id):
        # this url can be placed on site for preview
        return f"https://drive.google.com/uc?id={file_id}"

        # return f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={self.creds.token}"

    async def find_license(self, folder_id, drive):
        try:
            license = (
                drive.files().list(
                    q=f"name='{BasePlugin.license_filename}' and '{folder_id}' in parents",
                    pageSize=1, fields="files(id)",).execute())
            file_id = license.get("files")[0]["id"]

            url = self._get_download_url(file_id)
            # headers = { "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            #             "Accept-Encoding":"gzip, deflate, br",
            #             "Accept-Language":"en-US,en;q=0.5",
            #             "Connection":"keep-alive",
            #             "Sec-Fetch-Dest":"document",
            #             "Sec-Fetch-Mode":"navigate",
            #             "Sec-Fetch-Site":"none",
            #             "Sec-Fetch-User":"?1",
            #             "TE":"trailers",
            #             "Upgrade-Insecure-Requests":"1",
            #             "User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0"
            # }
            headers = {}
            tag_id = await self.download(url, headers)
            logger.info(f"download {tag_id=}")
            tag_id = await BasePlugin.parse_tag_in(tag_id.decode())
            logger.info(f"{tag_id=}")
            return tag_id

            # file = drive.files().get( fileId=file_id ).execute()

            # logger.info( f'downloading file {file_id} {file["name"]}')
            # fileRequest = drive.files().get_media(fileId=file_id)
            # fh = io.BytesIO()
            # downloader = MediaIoBaseDownload(fh, fileRequest)
            # done = False
            # while done is False:
            #     status, done = downloader.next_chunk()
            # fh.seek(0)
            # tag_id = fh.read().strip()
            # tag_id = await BasePlugin.parse_tag_in(tag_id)

            # logger.info( f'{tag_id=}')

            # return tag_id
        except Exception:
            pass

    async def scan_folder(self, folder_id, drive):
        logger.info(f"scanning folder {folder_id}")
        # print(folder_id)
        # this gives us a list of all folders with that name
        # folder = drive.files().get( fileId=folder_id ).execute()
        # print(type(folder))

        page_token = None
        while True:
            results = (
                drive.files()
                .list(
                    q="'" + folder_id + "' in parents",
                    pageSize=10,
                    pageToken=page_token,
                    fields="nextPageToken, files(id, name)",
                )
                .execute()
            )
            items = results.get("files", [])
            page_token = results.get("nextPageToken", None)

            # Now we can loop through each file in that folder, and do whatever (in this case, download them and open them as images in OpenCV)
            for f in range(0, len(items)):
                # print( items[f])

                file_id = items[f].get("id")
                logger.info(f"{file_id=}")

                file = drive.files().get(fileId=file_id).execute()
                logger.info(f"{file['mimeType']=}")

                if file["mimeType"] == "application/vnd.google-apps.folder":
                    async for yielded in self.scan_folder(file_id, drive):
                        yield yielded
                else:
                    try:
                        datapool_content_type = (
                            BasePlugin.get_content_type_by_mime_type(
                                file["mimeType"]
                            )
                        )
                    except BasePluginException:
                        logger.error(
                            f'Not supported mime type {file["mimeType"]}'
                        )

                    logger.info(f'downloading file {file_id} {file["name"]}')
                    # TODO: this works too, but is getting blocked  when running from lsrv2
                    # fileRequest = drive.files().get_media(fileId=file_id)
                    # fh = io.BytesIO()
                    # downloader = MediaIoBaseDownload(fh, fileRequest)
                    # done = False
                    # while done is False:
                    #     status, done = downloader.next_chunk()
                    # fh.seek(0)
                    # content = fh.read()
                    # direct url seems to work better than API access
                    url = self._get_download_url(file_id)
                    content = await self.download(url)
                    if content is not None:
                        logger.info(f"file size={len(content)}")

                        image_tag = None
                        if datapool_content_type == DatapoolContentType.Image:
                            image_tag = BasePlugin.parse_image_tag(content)
                            if image_tag is not None and image_tag.is_crawling_allowed() is False:
                                logger.info(
                                    f'crawling is disabled by image tag: {str(image_tag)}')
                                continue

                        # obj_url = f'https://drive.google.com/file/d/{file_id}/view'
                        obj_url = url
                        storage_id = BaseStorage.gen_id(obj_url)
                        await self.ctx.storage.put(storage_id, content)

                        yield CrawlerContent(
                            tag_id=str(image_tag) if image_tag is not None else None,
                            copyright_tag_id=str(self.tag_id),
                            type=datapool_content_type,
                            storage_id=storage_id,
                            url=obj_url,
                        )

                # baseImage = cv2.imdecode(np.fromstring(fhContents, dtype=np.uint8), cv2.IMREAD_COLOR)
            if page_token is None:
                break
