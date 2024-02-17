import asyncio
import json
import traceback
import aiohttp
from aiohttp_retry import ExponentialRetry, RetryClient

class SessionWrapper:
    def __init__(self, max_retries=3, timeout=20, tojson=True) -> None:
        conn = aiohttp.TCPConnector(verify_ssl=False)
        self._session = RetryClient(retry_options=ExponentialRetry(attempts=max_retries), connector=conn)
        self.timeout = timeout
        self.tojson = tojson

    async def get(self, url, params, headers):
        try:
            async with self._session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)) as resp:
                if resp.status == 200:
                    response = await resp.text()
                    if self.tojson:
                        response = json.loads(response)
                    return True, response
                else:
                    return False, '获取信息失败'
        except Exception as e:
            return False, str(e)
    
    async def post(self, url, params, headers):
        try:
            async with self._session.post(url, json=params, headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)) as resp:
                if resp.status == 200:
                    response = await resp.text()
                    if self.tojson:
                        response = json.loads(response)
                    return True, response
                else:
                    return False, '获取信息失败'
        except Exception as e:
            return False, str(e)

    async def upload(self, url, params, file, headers):
        try:
            with open(file, 'rb') as f:
                params['file'] = f
                async with self._session.post(url, data=params, headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)) as resp:
                    if resp.status == 200:
                        response = await resp.text()
                        if self.tojson:
                            response = json.loads(response)
                        return True, response
                    else:
                        return False, '上传失败'
        except Exception as e:
            return False, str(e)

    async def close(self):
        try:
            await self._session.close()
        except Exception as e:
            pass
            

async def send(url, method='get', params={}, headers={}, max_retries=3, timeout=20, tojson=True):
    session = SessionWrapper(max_retries, timeout, tojson=tojson)
    try:
        if method == 'post':
            func = session.post
        else:
            func = session.get
        ret, response = await func(url, params, headers=headers)
        if ret:
            return response
        else:
            return None
    except Exception as e:
        raise e
    finally:
        await session.close()

async def upload(url, file, params={}, headers={}, max_retries=3, timeout=20, tojson=True):
    session = SessionWrapper(max_retries, timeout, tojson=tojson)
    try:
        ret, response = await session.upload(url, params, file, headers=headers)
        if ret:
            return response
        else:
            return None
    except Exception as e:
        raise e
    finally:
        await session.close()

if __name__ == '__main__':
    import time
    asyncio.get_event_loop().run_until_complete(send('https://backend.ai.hamuna.club/api/monitor/group/event/add_event', 'post', {
            'region': '全部',
            'event_name': '摄像头无法访问',
            'event_type': 'camera_offline',
            'warning_level': 3,
            'warning_text': '摄像头无法访问，请联系场地检查',
            'evidence': [],
            'timestamp': time.time(),
            'camera_id': ''
        }, {
            'from': 'edge',
            'app_id': '236cc8be7f8711ea86f3525400725587',
            'group_id': '6118b1db533e19685e6cd61d'
        }))

