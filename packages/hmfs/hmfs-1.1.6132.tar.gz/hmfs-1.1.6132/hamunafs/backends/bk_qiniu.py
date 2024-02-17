import os
import traceback
from aiohttp_retry import ExponentialRetry, RetryClient
from aiofile import async_open

from qiniu import put_file, put_data, Auth, etag
from qiniu import BucketManager, build_batch_delete
from qiniu import Zone, set_default

from hamunafs.backends.base import BackendBase

class Qiniu(BackendBase):
    def __init__(self, cfg):
        key, secret, domain, default_bucket = cfg['key'], cfg['secret'], cfg['domain'], cfg['default_bucket']
        self.auth = Auth(key, secret)
        self.domain = domain
        self.default_bucket = default_bucket
        self.bucket = BucketManager(self.auth)
    
    def get_token(self, filename):
        return self.auth.upload_token(self.default_bucket, filename)
    
    def geturl(self, entrypoint):
        bucket, bucket_name = entrypoint.split('/')
        return 'http://{}/{}_{}'.format(self.domain, bucket, bucket_name)

    def put(self, file, bucket, bucket_name, tmp=True):
        try:
            if tmp:
                _bucket = 'tmp_file_' + bucket
            else:
                _bucket = bucket
            b_name = '{}_{}'.format(_bucket, bucket_name)
            print('acquiring upload token....')
            token = self.auth.upload_token(self.default_bucket, b_name)
            print('upload token acquired -> {}'.format(token))
            print('uploading...')
            ret, info = put_file(token, b_name, file)
            if ret is not None:
                print('upload success.')
                return True, '{}/{}'.format(_bucket, bucket_name)
            print('upload failed.')
            return False, '上传失败'
        except Exception as e:
            return False, traceback.format_exc()
    
    async def put_async(self, file, bucket, bucket_name, tmp=True):
        return self.put(file, bucket, bucket_name, tmp)

    def put_buffer(self, buffer, bucket, bucket_name):
        try:
            b_name = '{}_{}'.format(bucket, bucket_name)
            token = self.auth.upload_token(self.default_bucket, b_name)
            ret, info = put_data(token, b_name, buffer)
            if ret is not None:
                return True, '{}/{}'.format(bucket, bucket_name)
            return False, '上传失败'
        except Exception as e:
            return False, str(e)

    async def put_buffer_async(self, buffer, bucket, bucket_name):
        return self.put_buffer(buffer, bucket, bucket_name)

    def get(self, download_path, bucket, bucket_name, tries=0):
        try:
            if tries >= 3:
                return False, '下载出错'
            else:
                url = 'http://{}/{}'.format(self.domain, '{}_{}'.format(bucket, bucket_name))
                print('downloading {} -> {}'.format(url, download_path))
                
                if os.path.isfile(download_path):
                    os.remove(download_path)
                self.create_dir_if_not_exists(download_path)
                path = self.download_file(url, download_path)
                if path:
                    return True, download_path
                return self.get(download_path, bucket, bucket_name, tries+1)
        except Exception as e:
            traceback.print_exc()
            if tries >= 3:
                return False, str(e)
            else:
                return self.get(download_path, bucket, bucket_name, tries+1)

    async def get_async(self, download_path, bucket, bucket_name, tries=0):
        try:
            if tries >= 3:
                return False, '下载出错'
            else:
                url = 'http://{}/{}'.format(self.domain, '{}_{}'.format(bucket, bucket_name))
                print('downloading {} -> {}'.format(url, download_path))
                
                if os.path.isfile(download_path):
                    os.remove(download_path)
                self.create_dir_if_not_exists(download_path)
                path = await self.download_file_async(url, download_path)
                if path:
                    return True, download_path
                return await self.get_async(download_path, bucket, bucket_name, tries+1)
        except Exception as e:
            traceback.print_exc()
            if tries >= 3:
                return False, str(e)
            else:
                return await self.get_async(download_path, bucket, bucket_name, tries+1)


            
