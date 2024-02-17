import traceback
from concurrent.futures import ThreadPoolExecutor
from minio import Minio
from minio.lifecycleconfig import LifecycleConfig, Rule, Expiration
from minio.commonconfig import ENABLED, DISABLED, Filter


class MinioAgent:
    def __init__(self, endpoint, acs_key, secret_key, secure=True, location='default'):
        self.client = Minio(endpoint, access_key=acs_key,
                            secret_key=secret_key, secure=secure, region=location)
        self.location = location
        self.upload_pool = ThreadPoolExecutor(max_workers=10)
        self.download_pool = ThreadPoolExecutor(max_workers=10)

    def create_bucket_if_not_exists(self, bucket_name, location, lifecycle=None):
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name, location=location)

                if lifecycle is not None:
                    self.client.set_bucket_lifecycle(bucket_name, LifecycleConfig([
                        Rule(ENABLED, expiration=Expiration(days=lifecycle), rule_filter=Filter(prefix=''))
                    ]))

            return True
        except Exception as e:
            if 'Bucket name contains invalid characters' in str(e):
                return False
            traceback.print_exc()
            return True

    def _upload_file(self, path, bucket, bucket_filename, tries=0, max_tries=5):
        try:
            if self.create_bucket_if_not_exists(bucket, self.location):
                self.client.fput_object(bucket, bucket_filename, path)
                return True, 'minio://{}/{}'.format(bucket, bucket_filename)
            else:
                print('創建bucket失敗: {}'.format(bucket))
                return False, '創建bucket失敗'
        except Exception as e:
            if tries > max_tries:
                return False, e
            else:
                return self._upload_file(path, bucket, bucket_filename, tries+1)
            
    def upload_file(self, path, bucket, bucket_filename, max_tries=5):
        # future = self.upload_pool.submit(self._upload_file, path, bucket, bucket_filename)
        # return future.result(timeout=10)
        return self._upload_file(path, bucket, bucket_filename, max_tries=max_tries)

    def _upload_file_by_buffer(self, buffer, bucket, bucket_filename, tries=0):
        try:
            if self.create_bucket_if_not_exists(bucket, self.location):
                self.client.put_object(
                    bucket, bucket_filename, buffer, len(buffer.getvalue()))
                return True, 'minio://{}/{}'.format(bucket, bucket_filename)
            else:
                return False, '創建bucket失敗'
        except Exception as e:
            if tries > 3:
                return False, e
            else:
                return self._upload_file_by_buffer(buffer, bucket, bucket_filename, tries+1)
            
    def upload_file_by_buffer(self, buffer, bucket, bucket_filename):
        # future = self.upload_pool.submit(self._upload_file_by_buffer, buffer, bucket, bucket_filename)
        # return future.result(timeout=10)
        return self._upload_file_by_buffer(buffer, bucket, bucket_filename)

    def _download_file(self, path, bucket, bucket_filename, tries=0, max_tries=5):
        try:
            self.client.fget_object(bucket, bucket_filename, path)
            return True, path
        except Exception as e:
            if tries > max_tries:
                return False, e
            else:
                return self._download_file(path, bucket, bucket_filename, tries+1)
            
    def download_file(self, path, bucket, bucket_filename, max_tries=5):
        # future = self.download_pool.submit(self._download_file, path, bucket, bucket_filename)
        # return future.result(timeout=10)
        return self._download_file(path, bucket, bucket_filename, max_tries=max_tries)

    def delete(self, bucket, bucket_name, tries):
        try:
            self.client.remove_object(bucket, bucket_name)
            return True, None
        except Exception as e:
            if tries > 5:
                return False, e
            else:
                return self.delete(bucket, bucket_name, tries + 1)

    def exists(self, bucket, bucket_name):
        meta = self.client.stat_object(bucket, bucket_name)

        return meta is not None
