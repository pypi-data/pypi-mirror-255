import os
import asyncio
import traceback
from aiohttp_retry import ExponentialRetry, RetryClient

from nos import Client
from nos.transport import Transport

from hamunafs.backends.base import BackendBase

class WYSF(BackendBase):
    def __init__(self, cfg):
        key, secret, domain, default_bucket = cfg['key'], cfg['secret'], cfg['domain'], cfg['default_bucket']
        self.client = Client(key, secret, Transport, timeout=30)
        self.domain = domain
        self.default_bucket = default_bucket

    def get_token(self, filename):
        return ''
    
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
            with open(file, 'rb') as f:
                resp = self.client.put_object(self.default_bucket, b_name, f)
            if resp.get('etag', None):
                print('upload success.')
                return True, '{}/{}'.format(_bucket, bucket_name)
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
        try:
            b_name = '{}_{}'.format(bucket, bucket_name)
            bucket = await self.cow.get_bucket(self.default_bucket)
            ret, info = await bucket.put_data(key=b_name, data=buffer)
            if ret is not None:
                return True, '{}/{}'.format(bucket, bucket_name)
            return False, '上传失败'
        except Exception as e:
            return False, str(e)

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

    async def cleanup_old_files(self):
        objects = self.client.list_objects(self.default_bucket, prefix='tmp_file', limit=1000)
        keys = [object_list.find("Key").text for object_list in objects["response"].findall("Contents")]
        try:
            self.client.delete_objects(self.default_bucket, keys, quiet=False)
        except:
            pass

        while len(keys) == 1000:
            print('listing objects...')
            objects = self.client.list_objects(self.default_bucket, prefix='tmp_file', limit=1000)
            keys = [object_list.find("Key").text for object_list in objects["response"].findall("Contents")]

            print('deleting objects...')
            try:
                self.client.delete_objects(self.default_bucket, keys, quiet=False)
            except:
                pass
        
        if len(keys) > 0:
            print('deleting objects...')
            try:
                self.client.delete_objects(self.default_bucket, keys, quiet=True)
            except:
                pass

        print('all deleting process done')



if __name__ == '__main__':
    client = WYSF({
        'key': '46b5e0508a9641a485c6d3f62078e7ab',
        'secret': 'fd187963fb8943febc2624e1241081ed',
        'domain': 'hamuna-images.nos-eastchina1.126.net',
        'default_bucket': 'hamuna-images'
    })
    # asyncio.get_event_loop().run_until_complete(client.cleanup_old_files())


            
