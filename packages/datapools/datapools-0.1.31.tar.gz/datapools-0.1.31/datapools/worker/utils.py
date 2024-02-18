from ..common.queues import (
    QueueMessageType,
)
from urllib.parse import urlparse, urljoin


def get_storage_invalidation_topic(worker_id):
    return (
        f"worker.id_{worker_id}.type_{QueueMessageType.StorageInvalidation.value}"
    )


def canonicalize_url(url):
    # Normalize the URL to a standard form
    parsed = urlparse(url)
    return urljoin(url, parsed.path)
