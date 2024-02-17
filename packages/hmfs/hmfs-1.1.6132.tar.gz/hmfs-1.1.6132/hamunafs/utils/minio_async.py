import traceback
import time
import asyncio
from miniopy_async import Minio
from miniopy_async.lifecycleconfig import LifecycleConfig, Rule, Expiration
from miniopy_async.commonconfig import ENABLED, DISABLED, Filter
from telnetlib import Telnet
from threading import Thread, Lock

from concurrent.futures.thread import ThreadPoolExecutor

class MinioClient(Minio):
    def __init__(self, endpoint, access_key=None, secret_key=None, session_token=None, secure=True, region=None, credentials=None):
        super().__init__(endpoint, access_key, secret_key, session_token, secure, region, credentials)
        self.location = region

    async def create_bucket(self, bucket_name, object_lock=False):
        return await super().make_bucket(bucket_name, self.location, object_lock)

class MinioAgentAsync:
    def __init__(self, endpoints, weights, check_awailable_ts=1, timeout=10):
        self.client_pool = []

        for endpoint in endpoints:
            self.client_pool.append(MinioClient(**endpoint))
        self.endpoints = endpoints
        self.availability = [True] * len(endpoints)
        self.weights = weights
        self.check_availability_ts = check_awailable_ts
        self.timeout = timeout

        self.availability_locker = Lock()

        self.availability_check_thread = Thread(target=self.check_availability, daemon=True)
        self.availability_check_thread.start()

    def check(self, endpoint):
        try:
            host, port = endpoint['endpoint'].split(':')
            with Telnet(host, int(port), timeout=3) as tn:
                return True
        except Exception as e:
            print(e)
            return False

    def check_availability(self):
        while True:
            print('checking endpoints availability...')
            self.availability_locker.acquire(blocking=True, timeout=30)
            try:
                with ThreadPoolExecutor(max_workers=2) as pool:
                    results = pool.map(self.check, self.endpoints)
                    for i, r in enumerate(results):
                        print('endpoint {} -> {}'.format(i, r))
                        self.availability[i] = r

                        if not r:
                            self.client_pool[i] = None
                        else:
                            self.client_pool[i] = MinioClient(**self.endpoints[i])
            except Exception as e:
                print(e)
            finally:
                self.availability_locker.release()
                time.sleep(self.check_availability_ts)

    def get_client(self) -> MinioClient:
        self.availability_locker.acquire(blocking=True, timeout=30)

        fused_weights = [(i, w) for i, (a, w) in enumerate(zip(self.availability, self.weights)) if a]
        fused_weights = sorted(fused_weights, key=lambda x:x[1], reverse=True)        
        self.availability_locker.release()
        print('using endpoint -> {}'.format(self.endpoints[fused_weights[0][0]]['endpoint']))
        return self.client_pool[fused_weights[0][0]]

    async def create_bucket_if_not_exists(self, bucket_name, lifecycle=None):
        try:
            if not await self.get_client().bucket_exists(bucket_name):
                await self.get_client().create_bucket(bucket_name)

                if lifecycle is not None:
                    await self.get_client().set_bucket_lifecycle(bucket_name, LifecycleConfig([
                        Rule(ENABLED, expiration=Expiration(days=lifecycle), rule_filter=Filter(prefix=''))
                    ]))

            return True
        except Exception as e:
            if 'Bucket name contains invalid characters' in str(e):
                return False
            traceback.print_exc()
            return True

    async def _upload_file(self, path, bucket, bucket_filename, tries=0, max_tries=5):
        try:
            if await self.create_bucket_if_not_exists(bucket):
                await self.get_client().fput_object(bucket, bucket_filename, path)
                return True, 'minio://{}/{}'.format(bucket, bucket_filename)
            else:
                print('創建bucket失敗: {}'.format(bucket))
                return False, '創建bucket失敗'
        except Exception as e:
            if tries > max_tries:
                return False, e
            else:
                return await self._upload_file(path, bucket, bucket_filename, tries+1)
            
    async def upload_file(self, path, bucket, bucket_filename, max_tries=5):
        # future = self.upload_pool.submit(self._upload_file, path, bucket, bucket_filename)
        # return future.result(timeout=10)
        try:
            return await asyncio.wait_for(self._upload_file(path, bucket, bucket_filename, max_tries=max_tries), timeout=self.timeout)
        except Exception as e:
            return False, str(e)

    async def _upload_file_by_buffer(self, buffer, bucket, bucket_filename, tries=0):
        try:
            if await self.create_bucket_if_not_exists(bucket):
                await self.get_client().put_object(
                    bucket, bucket_filename, buffer, len(buffer.getvalue()))
                return True, 'minio://{}/{}'.format(bucket, bucket_filename)
            else:
                return False, '創建bucket失敗'
        except Exception as e:
            if tries > 3:
                return False, e
            else:
                return await self._upload_file_by_buffer(buffer, bucket, bucket_filename, tries+1)
            
    async def upload_file_by_buffer(self, buffer, bucket, bucket_filename):
        # future = self.upload_pool.submit(self._upload_file_by_buffer, buffer, bucket, bucket_filename)
        # return future.result(timeout=10)
        try:
            return await asyncio.wait_for(self._upload_file_by_buffer(buffer, bucket, bucket_filename), timeout=self.timeout)
        except Exception as e:
            return False, str(e)

    async def _download_file(self, path, bucket, bucket_filename, tries=0, max_tries=5):
        try:
            await self.get_client().fget_object(bucket, bucket_filename, path)
            return True, path
        except Exception as e:
            if tries > max_tries:
                return False, e
            else:
                return await self._download_file(path, bucket, bucket_filename, tries+1)
            
    async def download_file(self, path, bucket, bucket_filename, max_tries=5):
        # future = self.download_pool.submit(self._download_file, path, bucket, bucket_filename)
        # return future.result(timeout=10)
        try:
            return await asyncio.wait_for(self._download_file(path, bucket, bucket_filename, max_tries=max_tries), timeout=self.timeout)
        except Exception as e:
            return False, str(e)

    async def delete(self, bucket, bucket_name, tries):
        try:
            await self.get_client().remove_object(bucket, bucket_name)
            return True, None
        except Exception as e:
            if tries > 5:
                return False, e
            else:
                return await self.delete(bucket, bucket_name, tries + 1)

    async def exists(self, bucket, bucket_name):
        meta = await self.get_client().stat_object(bucket, bucket_name)

        return meta is not None
