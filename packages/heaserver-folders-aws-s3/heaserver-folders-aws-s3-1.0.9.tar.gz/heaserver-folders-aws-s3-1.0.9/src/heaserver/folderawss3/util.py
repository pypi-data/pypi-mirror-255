

from collections.abc import Mapping, Callable, Awaitable
from datetime import datetime, timezone
import logging
from typing import Any
from uuid import uuid4
from aiohttp import hdrs, web
from heaobject.aws import S3StorageClass
from heaobject.awss3key import display_name, is_folder, replace_parent_folder
from heaobject.root import DesktopObject
from heaserver.service.aiohttp import StreamResponseFileLikeWrapper
from heaserver.service.db import awsservicelib
from heaserver.service import response
from humanize import naturaldelta
from mypy_boto3_s3 import S3Client
import asyncio
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
from functools import partial
from heaserver.service.util import queued_processing
from botocore.exceptions import ClientError as BotoClientError



async def response_folder_as_zip(s3_client: S3Client, request: web.Request, bucket_name: str, folder_key: str) -> web.Response:
    """
    Creates a HTTP streaming response with the contents of all S3 objects with the given prefix packaged into a ZIP
    file. S3 allows folders to have no name (just a slash), and for maximum compatibility with operating systems like
    Windows that do not, such folders are replaced in the zip file with "No name <random string>". The resulting ZIP
    files are uncompressed, but this may change in the future. Files that cannot be downloaded are returned as zero
    byte files. Objects in an incompatible storage class are skipped.

    :param s3_client: the S3Client (required).
    :param request: the HTTP request (required).
    :param bucket_name: the bucket name (required).
    :param folder_key: the folder key (required).
    :return: the HTTP response.
    """
    logger = logging.getLogger(__name__)
    folder_display_name = display_name(folder_key)
    if not folder_display_name:
        folder_display_name = 'archive'

    response_ = web.StreamResponse(status=200, reason='OK',
                                               headers={hdrs.CONTENT_DISPOSITION: f'attachment; filename={folder_display_name}.zip'})
    response_.content_type = 'application/zip'
    await response_.prepare(request)

    loop = asyncio.get_running_loop()

    async with StreamResponseFileLikeWrapper(response_) as fileobj:
        with ZipFile(fileobj, mode='w', compression=ZIP_DEFLATED) as zf:
            async for obj in awsservicelib.list_objects(s3_client, bucket_name, folder_key, include_restore_status=True):
                try:
                    folder = obj['Key'].removeprefix(folder_key)
                    if not folder:
                        continue
                    if obj['StorageClass'] in (S3StorageClass.STANDARD.name, S3StorageClass.GLACIER_IR.name)\
                        or ((restore:= obj.get('RestoreStatus')) and restore.get('RestoreExpiryDate')):
                        filename = _fill_in_folders_with_no_name(folder)
                        zinfo = ZipInfo(filename=filename, date_time=obj['LastModified'].timetuple()[:6])
                        #zinfo.compress_type = ZIP_DEFLATED  # Causes downloads to hang, possibly because something gets confused about file size.
                        if zinfo.is_dir():  # Zip also denotes a folders as names ending with a slash.
                            await loop.run_in_executor(None, zf.writestr, zinfo, '')
                        else:
                            with zf.open(zinfo, mode='w') as dest:
                                await loop.run_in_executor(None, s3_client.download_fileobj, bucket_name, obj['Key'], dest)
                except BotoClientError as e:
                    logger.warning('Error downloading %s in bucket %s: %s', obj['Key'], bucket_name, e)
    return response_


def _fill_in_folders_with_no_name(filename: str) -> str:
    """
    S3 allows folders to have no name (just a slash). This function replaces those "empty" names with a randomly
    generated name.

    :param filename: the filename.
    :return: the filename with empty names replaced.
    """
    logger = logging.getLogger(__name__)
    def split_and_rejoin(fname_: str) -> str:
        return '/'.join(part if part else f'No name {str(uuid4())}' for part in fname_.split('/'))
    if is_folder(filename):
        filename = split_and_rejoin(filename.rstrip('/')) + '/'
    else:
        filename = split_and_rejoin(filename)
    logger.debug('filename to download %s', filename)
    return filename


def set_file_source(obj: Mapping[str, Any], item: DesktopObject):
    item.source = None
    item.source_detail = None
    retrieval = obj.get('RestoreStatus')
    if retrieval is not None:
        if (retrieval.get("IsRestoreInProgress")):
            item.source = "AWS S3 (Unarchiving...)"
            item.source_detail = "Typically completes within 12 hours"
        if (retrieval.get("RestoreExpiryDate") is not None):
            item.source = "AWS S3 (Unarchived)"
            temporarily_available_until = retrieval.get("RestoreExpiryDate")
            item.source_detail = f"Available for {naturaldelta(temporarily_available_until - datetime.now(timezone.utc))}"
    if item.source is None:
        s = f'AWS S3 ({S3StorageClass[obj["StorageClass"]].display_name})'
        item.source = s
        item.source_detail = s


async def move(s3_client: S3Client, source_bucket_id: str, source_key: str, target_bucket_id: str, target_key: str,
               move_completed_cb: Callable[[str, str, str, str], Awaitable[None]] | None = None):
    """
    Moves object with source_key and in source_bucket_id to target_bucket_id and target_key. A preflight process
    checks whether the object (or for a folder, every object in the folder) is movable.

    :param s3_client: the S3 client (required).
    :param source_bucket_id: the source bucket name (required).
    :param source_key: the key of the object to move (required).
    :param target_bucket_id: the name of the target bucket (required).
    :param target_key: the key of the target folder (required).
    :param move_completed_cb: a callback that is invoked upon successfully moving an object (optional). For folders,
    this function is invoked separately for every object within the folder.
    :raises HTTPBadRequest: if preflight fails.
    :raises BotoClientError: if an error occurs while attempting to move the object (or for folders, the folder's
    contents).
    """
    logger = logging.getLogger(__name__)
    loop = asyncio.get_running_loop()
    def copy_and_delete(source_key, target_key):
        s3_client.copy(CopySource={'Bucket': source_bucket_id, 'Key': source_key}, Bucket=target_bucket_id, Key=target_key)
        s3_client.delete_object(Bucket=source_bucket_id, Key=source_key)
    async def gen():
        # Preflight
        cached_values = []
        async for obj in awsservicelib.list_objects(s3_client, source_bucket_id, source_key, max_keys=1000, loop=loop, include_restore_status=True):
            if obj['StorageClass'] in (S3StorageClass.DEEP_ARCHIVE.name, S3StorageClass.GLACIER.name) and not ((restore := obj.get('RestoreStatus')) and restore.get('RestoreExpiryDate')):
                raise response.status_bad_request(f'{awsservicelib._activity_object_display_name(source_bucket_id, source_key)} contains archived objects')
            elif len(cached_values) < 1000:
                cached_values.append(obj)
        if len(cached_values) <= 1000:
            for val in cached_values:
                yield val
        else:
            async for obj in awsservicelib.list_objects(s3_client, source_bucket_id, source_key, max_keys=1000, loop=loop):
                yield obj
    async def obj_processor(obj):
        source_key_ = obj['Key']
        target_key_ = replace_parent_folder(source_key=source_key_, target_key=target_key, source_key_folder=source_key)
        logger.debug('Moving %s/%s to %s/%s', source_bucket_id, source_key_, target_bucket_id, target_key_)
        await loop.run_in_executor(None, partial(copy_and_delete, source_key_, target_key_))
        if move_completed_cb:
            await move_completed_cb(source_bucket_id, source_key_, target_bucket_id, target_key_)
    await queued_processing(gen, obj_processor)
