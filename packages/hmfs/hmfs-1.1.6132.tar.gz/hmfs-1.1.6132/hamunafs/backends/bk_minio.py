import os
import traceback
from aiohttp_retry import ExponentialRetry, RetryClient

from hamunafs.utils.minio import MinioAgent

from hamunafs.backends.base import BackendBase
from aiofile import AIOFile, Writer, async_open

class MinioBackend(BackendBase):
    def __init__(self, cfg):
        key, secret, domain, default_bucket = cfg['key'], cfg['secret'], cfg['domain'], cfg['default_bucket']
        self.client = MinioAgent(domain, key, secret, secure=False)
        self.domain = domain
        self.default_bucket = default_bucket
    
    def geturl(self, entrypoint):
        bucket, bucket_name = entrypoint.split('/')
        return 'http://{}/{}/{}_{}'.format(self.domain, self.default_bucket, bucket, bucket_name)

    def put(self, file, bucket, bucket_name, tmp=True):
        try:
            if tmp:
                _bucket = 'tmp_file_' + bucket
            else:
                _bucket = bucket
            b_name = '{}_{}'.format(_bucket, bucket_name)
            print('uploading to {}...'.format(self.domain))
            ret, e = self.client.upload_file(file, self.default_bucket, b_name)
            if ret:
                print('upload success.')
                return True, '{}/{}'.format(_bucket, bucket_name)
            print('upload failed: {}'.format(e))
            return False, e
        except Exception as e:
            return False, traceback.format_exc()
    
    async def put_async(self, file, bucket, bucket_name, tmp=True):
        return self.put(file, bucket, bucket_name, tmp)

    def put_buffer(self, buffer, bucket, bucket_name):
        try:
            b_name = '{}_{}'.format(bucket, bucket_name)
            ret, e = self.client.upload_file_by_buffer(buffer, self.default_bucket, b_name)
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
                # url = 'http://{}/{}/{}'.format(self.domain, self.default_bucket, '{}_{}'.format(bucket, bucket_name))
                # print('downloading {} -> {}'.format(url, download_path))

                # if os.path.isfile(download_path):
                #     os.remove(download_path)

                # self.create_dir_if_not_exists(download_path)
                # path = self.download_file(url, download_path)
                # if path:
                #     return True, download_path
                ret, e = self.client.download_file(download_path, self.default_bucket, '{}_{}'.format(bucket, bucket_name))
                if ret:
                    return True, e
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
                # url = 'http://{}/{}/{}'.format(self.domain, self.default_bucket, '{}_{}'.format(bucket, bucket_name))
                # print('downloading {} -> {}'.format(url, download_path))

                # if os.path.isfile(download_path):
                #     os.remove(download_path)

                # self.create_dir_if_not_exists(download_path)
                # path = await self.download_file_async(url, download_path)
                # if path:
                #     return True, download_path

                ret, e = self.client.download_file(download_path, self.default_bucket, '{}_{}'.format(bucket, bucket_name))
                if ret:
                    return True, e
                return await self.get_async(download_path, bucket, bucket_name, tries+1)
        except Exception as e:
            traceback.print_exc()
            if tries >= 3:
                return False, str(e)
            else:
                return await self.get_async(download_path, bucket, bucket_name, tries+1)


            
