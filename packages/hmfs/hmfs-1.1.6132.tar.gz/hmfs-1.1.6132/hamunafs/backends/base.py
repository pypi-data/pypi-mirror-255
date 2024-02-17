import os
from .fetcher import file_fetcher

class BackendBase:
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        
    def put(self, filename, bucket, bucket_name):
        pass
    
    def put_buffer(self, buffer, bucket, bucket_name):
        pass

    async def put_async(self, filename, bucket, bucket_name):
        pass
    
    async def put_buffer_async(self, buffer, bucket, bucket_name):
        pass
    
    def get(self, filename, bucket, bucket_name):
        pass
    
    def geturl(self, entrypoint):
        return entrypoint

    async def get_async(self, filename, bucket, bucket_name):
        pass

    async def cleanup_old_files(self):
        pass

    def download_file(self, url, path):
        result = file_fetcher.fetch_file(url, path)
        return result

    async def download_file_async(self, url, path):
        # result = await file_fetcher.fetch_file_async(url, path)
        # return result
        return self.download_file(url, path)


    def create_dir_if_not_exists(self, path):
        os.makedirs(os.path.split(path)[0], exist_ok=True)
    