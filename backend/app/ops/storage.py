from .. import config
import os
import logging

logger = logging.getLogger(__name__)

if config.STORAGE_TYPE == "gcloud":
    from google.cloud import storage

    class CloudStorage:
        def __init__(self, *, project):
            self.client = storage.Client(project=project)
            self.bucket = self.client.get_bucket(config.STORAGE_BUCKET)

        def upload_filename(self, source, target):
            blob = self.bucket.blob(target)
            blob.upload_from_filename(source)

        def delete(self, filename):
            blob = self.bucket.blob(filename)
            blob.delete()

        def open(self, filename):
            blob = self.bucket.blob(filename)
            return blob.open("rb")

    instance = CloudStorage(project="vffproject")
else:
    import shutil

    def configure_filestore(path: str):
        global instance
        instance = FileSystemStorage(path)

    class FileSystemStorage:
        def __init__(self, path):
            self.path = path
            pass

        def _target(self, filename):
            return os.path.join(self.path, filename)

        def open(self, filename):
            logger.info("Reading file %s", filename)
            target = self._target(filename)
            if not os.path.isfile(target):
                return None
            return open(target, "rb")

        def upload_filename(self, source, target):
            logger.info("Uploading file %s", target)
            target = self._target(target)
            shutil.copy(source, target)

        def delete(self, filename):
            logger.info("Removing file %s", filename)
            target = self._target(filename)
            if os.path.isfile(target):
                os.unlink(target)

    instance = FileSystemStorage("/workspace/backend/data")
