import logging
import uuid
from os import path
from typing import Tuple, Dict

from aiohttp import web

logger = logging.getLogger(__name__)


def has_uploaded_file(request) -> bool:
    """
    Check if a HTTP request comes with a file uploaded
    :param request: A HTTP POST request data received
    :return:
    """
    content_type = request.headers.get('Content-Type', '')
    return 'multipart/form-data' in content_type


async def retrieve_uploaded_file(request: web.Request) -> Tuple[str, str, Dict[str, str]]:
    """
    Handle file uploading from the given HTTP request
    :param request: A HTTP POST request data with a file uploaded
    :return: A tuple of (original file name, full path saved on the host, other_data)
    """
    original_filename, filename_on_host = None, None
    other_data = {}
    reader = await request.multipart()
    while True:
        field = await reader.next()
        if field is None:
            break
        if field.name == 'file':
            original_filename = field.filename
            _, ext = path.splitext(original_filename)
            # You cannot rely on Content-Length if transfer is chunked.
            filename_on_host = path.join('/tmp', str(uuid.uuid4()) + ext)
            with open(filename_on_host, 'wb') as f:
                while True:
                    chunk = await field.read_chunk()  # 8192 bytes by default.
                    if not chunk:
                        break
                    f.write(chunk)
            logger.debug('Uploaded file to: {}'.format(filename_on_host))
        else:
            other_data[field.name] = (await field.read(decode=True)).decode()

    return original_filename, filename_on_host, other_data

