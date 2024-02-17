import traceback
from .base import BackendBase

class ShareImageHost(BackendBase):
    def __init__(self, cfg) -> None:
        self.key, self.secret, self.domain, self.default_bucket = cfg['key'], cfg['secret'], cfg['domain'], cfg['default_bucket']

    def _get_auth_header(self):
        return {
            'Authorization': 'Bearer 1|1bJbwlqBfnggmOMEZqXT5XusaIwqiZjCDs7r1Ob5',
            'Accept': 'application/json'
        }
        
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
