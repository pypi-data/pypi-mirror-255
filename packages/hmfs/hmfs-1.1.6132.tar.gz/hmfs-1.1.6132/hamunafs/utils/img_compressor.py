import asyncio
import os
import shutil
import warnings
import numpy as np
from PIL import Image

import json
import random
import aiohttp

async def request(method, url, headers={}, data=None):
    async with aiohttp.ClientSession() as session:
        func = session.get if method == 'get' else session.post

        resp = await func(url, headers=headers, data=data, timeout=10)
        return resp



async def download_file(url, ofname):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        with open(ofname, 'wb') as f:
            async for chunk in resp.content.iter_chunked(1024):
                f.write(chunk)


async def compress_jpeg(fname, ofname):
    try:
        url = 'https://tinypng.com/web/shrink'
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
            'X-Forwarded-For': get_random_ip()
        }
        result = None
        with open(fname, 'rb') as f:
            response = await request('post', url, headers, f) #requests.post(url, headers=headers, data=file, timeout=5)
            result = json.loads(await response.text())
        if result and result['input'] and result['output']:
            url = result['output']['url']
            await download_file(url, ofname)
            return ofname
        else:
            return None
    except Exception as e:
        print(e)
        return None

def get_random_ip():
    ip = []
    for i in range(4):
        ip.append(str(random.randint(0 if i in (2, 3) else 1, 254)))
    return '.'.join(ip)


async def image_compress(fname, ofname):
    ret = await compress_jpeg(fname, ofname)
    if not ret:
        return fname
    else:
        return ofname


async def compress_files(files):
    tasks = [
        image_compress(f, os.path.join(os.path.split(f)[0], 'compressed_{}'.format(os.path.split(f)[1]))) for f in files    
    ]

    results = await asyncio.gather(*tasks)

    return results

import asyncio
import os
import shutil
import traceback
import warnings
import numpy as np
from PIL import Image

import json
import random
import aiohttp

async def request(method, url, headers={}, data=None):
    async with aiohttp.ClientSession() as session:
        func = session.get if method == 'get' else session.post

        resp = await func(url, headers=headers, data=data, timeout=30)
        return resp



async def download_file(url, ofname):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url, timeout=20)
        with open(ofname, 'wb') as f:
            async for chunk in resp.content.iter_chunked(1024):
                f.write(chunk)


async def compress_jpeg(fname, ofname):
    try:
        url = 'https://tinypng.com/web/shrink'
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
            'X-Forwarded-For': get_random_ip()
        }
        result = None
        with open(fname, 'rb') as f:
            response = await request('post', url, headers, f)
            result = json.loads(await response.text())
        if result and result['input'] and result['output']:
            url = result['output']['url']
            await download_file(url, ofname)
            return ofname
        else:
            return None
    except:
        traceback.print_exc()
        return fname

def get_random_ip():
    ip = []
    for i in range(4):
        ip.append(str(random.randint(0 if i in (2, 3) else 1, 254)))
    return '.'.join(ip)


async def image_compress(fname, ofname):
    ret = await compress_jpeg(fname, ofname)
    if not ret:
        return fname
    else:
        return ofname


async def compress_files(files):
    tasks = [
        image_compress(f, os.path.join(os.path.split(f)[0], 'compressed_{}'.format(os.path.split(f)[1]))) for f in files
    ]

    results = await asyncio.gather(*tasks)

    return results

# try:
#     results = asyncio.run(asyncio.wait_for(compress_files([
#         '/home/superpigy/图片/u=4285776745,180034356&fm=30&app=106&f=JPEG.jpeg',
#         '/home/superpigy/图片/00c3714a-eb88-11ec-b602-c27abc788e0b.jpg'
#     ]), 1))
# except:
#     traceback.print_exc()

# print(results)