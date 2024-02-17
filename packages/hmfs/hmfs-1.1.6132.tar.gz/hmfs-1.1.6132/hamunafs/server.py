import traceback
# from function_scheduling_distributed_framework import fsdf_background_scheduler, task_deco, patch_frame_config, get_publisher, BrokerEnum
# from function_scheduling_distributed_framework.consumers.base_consumer import ExceptionForRequeue

from funboost import boost as task_deco, fsdf_background_scheduler, patch_frame_config, get_publisher, BrokerEnum
from funboost.consumers.base_consumer import ExceptionForRequeue

from hamunafs.utils.cachemanager import CacheManager, CacheManagerAsync
from hamunafs.utils.minio_async import MinioAgentAsync
from hamunafs.client import Client as FSClient

import uvloop
import asyncio
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

import time
import os
import argparse
import shutil

from hamunafs.utils.nsqmanager import MQManager
from hamunafs.sqlite import DB
from hamunafs.utils.timeutil import is_time_in_range


def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1:9000')
    parser.add_argument('--weights', type=str, default='5')
    parser.add_argument('--acs-key', type=str, default='hmcz')
    parser.add_argument('--acs-secret', type=str, default='1987yang')
    parser.add_argument('--location', type=str, default='brick1')
    parser.add_argument('--root-path', type=str, default='../hmfs_data')
    parser.add_argument('--api-host', type=str,
                        default='backend.ai.hamuna.club')
    parser.add_argument('--broker-host', type=str,
                        default='kafka.ai.hamuna.club')
    parser.add_argument('--broker-port', type=int, default=4150)
    parser.add_argument('--broker-http-port', type=int, default=34151)
    parser.add_argument('--redis-host', type=str,
                        default='cache.ai.hamuna.club')
    parser.add_argument('--redis-port', type=int, default=6379)
    parser.add_argument('--redis-pass', type=str, default='1987yang')
    parser.add_argument('--redis-db', type=int, default=2)

    opt = parser.parse_args()
    return opt


opt = get_opts()

root_path = opt.root_path

cache_path = os.path.join(root_path, 'cache')
db_path = os.path.join(root_path, 'db')

os.makedirs(cache_path, exist_ok=True)
os.makedirs(db_path, exist_ok=True)

# init sqlite
sqlite_db = DB(os.path.join(db_path, 'data.sqlite3'), is_relative=False)

sqlite_db.create_table('ttl_files', [
                       "id integer PRIMARY KEY", "bucket text NOT NULL", "bucket_name text NOT NULL", "expired integer"])

broker_cfg = {
    'host': opt.broker_host,
    'port': opt.broker_port,
    'http_port': opt.broker_http_port
}

endpoints = [{
    'endpoint': host, 
    'access_key': opt.acs_key, 
    'secret_key': opt.acs_secret, 
    'secure': False,
    'region': opt.location
} for host in opt.host.split(';')]


minio = MinioAgentAsync(endpoints, list(map(int, opt.weights.split(';'))), check_awailable_ts=10, timeout=30)

cache_engine_async = CacheManagerAsync(
    opt.redis_host, opt.redis_pass, opt.redis_port, opt.redis_db, local_cache=None)

patch_frame_config(
    NSQD_TCP_ADDRESSES=['{}:{}'.format(
        broker_cfg['host'], broker_cfg['port'])],
    NSQD_HTTP_CLIENT_HOST=broker_cfg['host'],
    NSQD_HTTP_CLIENT_PORT=broker_cfg['http_port']
)

hmfs_client = FSClient(opt.api_host, cache_engine_async.client, None)


@task_deco('fs_put', function_timeout=120, concurrent_mode=4, broker_kind=BrokerEnum.NSQ)
async def file_transfer_put(url, bucket, bucket_name, ttl):
    key = 'file_transfer_put_{}_{}'.format(bucket, bucket_name)
    if await cache_engine_async.get_cache(key, return_obj=False) is not None:
        return
    try:
        file_path = os.path.join(
            cache_path, '{}_{}'.format(bucket, bucket_name))
        ret, file_path = await hmfs_client.get_from_cloud_async(file_path, url)

        if ret:
            print('cloud downloaded. start uploading...')
            ret, e = await minio.upload_file(file_path, bucket, bucket_name)
            if ret:
                print('uploaded. writing to redis middleware...')
                await cache_engine_async.cache('tmp_file_{}_{}'.format(bucket, bucket_name), {
                    'ret': True,
                    'url': url
                }, expired=24 * 60 * 60)
                print('upload success!!')


                try:
                    os.remove(file_path)
                    print('remove file success')
                except Exception as e:
                    print(e)

                if ttl != -1:
                    expired_time = time.time() + ttl * 24 * 60 * 60
                    sqlite_db.iud('insert into ttl_files(bucket, bucket_name, expired) values (?, ?, ?)', (
                        bucket, bucket_name, expired_time))

            else:
                print('upload failed. writing to redis middleware...')
                await cache_engine_async.cache('tmp_file_{}_{}'.format(bucket, bucket_name), {
                    'ret': False,
                    'err': e
                }, expired=60)
        else:
            print('fput -> cloud download failed -> ' + e)
            await cache_engine_async.cache('tmp_file_{}_{}'.format(bucket, bucket_name), {
                'ret': False,
                'err': '文件中转错误'
            }, expired=60)
        await cache_engine_async.cache(key, 1, expired=60)
    except Exception as e:
        await cache_engine_async.cache('tmp_file_{}_{}'.format(bucket, bucket_name), {
            'ret': False,
            'err': '锁错误'
        }, expired=60)


async def put_to_cloud(task_id, file_path, bucket, bucket_name, refresh=False, tries=0):
    ret, e = await hmfs_client.put_to_cloud_async(
        file_path, bucket, bucket_name, refresh=refresh)
    if ret:
        print('fget -> uploaded to cloud')
        await cache_engine_async.cache(task_id, {
            'ret': True,
            'url': e
        }, expired=60 * 60 * 24 * 1)
        ext = os.path.splitext(file_path)[-1]
        if ext not in ['.jpg', '.jpeg', '.png']:
            try:
                os.remove(file_path)
                print('remove file success')
            except Exception as e:
                print(e)
    else:
        if tries > 3:
            print('fget -> failed uploading to cloud')
            await cache_engine_async.cache(task_id, {
                'ret': False,
                'err': e
            }, expired=60)
        else:
            print('fget -> retry put to cloud')
            await put_to_cloud(task_id, file_path, bucket, bucket_name,
                         refresh=refresh, tries=tries+1)


@task_deco('fs_get', function_timeout=60, concurrent_mode=4, broker_kind=BrokerEnum.NSQ)
async def file_transfer_get(bucket, bucket_name, refresh='no'):
    try:
        task_id = 'tmp_file_{}_{}'.format(bucket, bucket_name)
        file_path = os.path.join(
            cache_path, '{}_{}'.format(bucket, bucket_name))
        if not os.path.isfile(file_path) or refresh == 'yes':
            try:
                ret, e = await minio.download_file(file_path, bucket, bucket_name)
                if ret:
                    print('fget -> downloaded from minio')
                    file_path = e
                else:
                    print('fget -> failed from minio')
                    await cache_engine_async.cache(task_id, {
                        'ret': False,
                        'err': '获取错误'
                    }, expired=60)
                    return
            except Exception as e:
                await cache_engine_async.cache(task_id, {
                        'ret': False,
                        'err': str(e)
                    }, expired=60)
                return

        await put_to_cloud(task_id, file_path, bucket,
                     bucket_name, refresh=refresh == 'yes')
    except Exception as e:
        traceback.print_exc()

import psutil
def get_system_status():
    # Get cpu statistics
    cpu = str(psutil.cpu_percent())

    # Calculate memory information
    memory = psutil.virtual_memory()
    # Convert Bytes to MB (Bytes -> KB -> MB)
    mem_available = round(memory.available/1024.0/1024.0,1)
    mem_total = round(memory.total/1024.0/1024.0,1)
    

    # Calculate disk information
    disk = psutil.disk_usage('/')
    # Convert Bytes to GB (Bytes -> KB -> MB -> GB)
    disk_free = round(disk.free/1024.0/1024.0/1024.0,1)
    disk_total = round(disk.total/1024.0/1024.0/1024.0,1)

    return {
        'cpu': cpu,
        'memory': {
            'free': mem_available,
            'total': mem_total
        },
        'disk': {
            'free': disk_free,
            'total': disk_total
        },
        'ts': time.time()
    }

@task_deco('health_check', function_timeout=60, concurrent_mode=4, broker_kind=BrokerEnum.NSQ)
async def health_check(task_id):
    try:
        system_status = get_system_status()
        minio_status = minio.availability[0]

        await cache_engine_async.cache('fs_health_{}'.format(task_id), {
            'ret': True,
            'status': {
                'system_status': system_status,
                'minio_status': minio_status
            }
        }, expired=20)
    except Exception as e:
        await cache_engine_async.cache('fs_health_{}'.format(task_id), {
            'ret': False,
            'err': str(e)
        }, expired=20)
    
# @task_deco('file_transfer_del', function_timeout=60, concurrent_mode=4, broker_kind=BrokerEnum.NSQ)
# async def file_transfer_del(bucket, bucket_name):
#     key = 'del_file_{}_{}'.format(bucket, bucket_name)
#     if await cache_engine.get_cache_async(key, return_obj=False) is not None:
#         return

#     with cache_engine.lock(key, ttl=30) as lock:
#         if lock:
#             if await cache_engine.get_cache_async(key, return_obj=False) is not None:
#                 return
#             file_path = os.path.join(cache_path, '{}_{}'.format(bucket, bucket_name))
#             if not os.path.isfile(file_path):
#                 ret, e = minio.delete(bucket, bucket_name)

#             print('ok')

async def ttl_cleanup():
    rows = sqlite_db.select(
        'select id, bucket, bucket_name from ttl_files where expired < ?', (time.time(),))
    affected_records = 0
    if rows is not None:
        for r in rows:
            bucket, bucket_name = r['bucket'], r['bucket_name']
            ret, e = await minio.delete(bucket, bucket_name, 0)
            if ret:
                affected_records += 1
                print('removing file id: {} from db...'.format(r['id']))
                sqlite_db.iud(
                    'delete from ttl_files where id={};'.format(r['id']))
            else:
                print(e)

    return affected_records


async def extra_tasks():
    while True:
        try:
            affected_records = await ttl_cleanup()
            if affected_records > 0:
                print('data cleaned')

            if is_time_in_range('02:00', '04:00'):
                if await cache_engine_async.get_cache('hmfs_cleanup'):
                    continue
                await hmfs_client.cleanup_cloud()
                await cache_engine_async.cache('hmfs_cleanup', 1, expired=7200)

                shutil.rmtree(cache_path, ignore_errors=True)
                os.mkdir(cache_path)
        except:
            traceback.print_exc()
        finally:
            await asyncio.sleep(30)


def run():
    file_transfer_get.consume()
    file_transfer_put.consume()
    # file_transfer_del.consume()

    # asyncio.get_event_loop().run_until_complete(file_transfer_put('qiqiu5://tmp_file_pigcount-202306/ebcadbfe0fdd11ee96d300155d923235.jpg', 'pigcount-202306', 'ebcadbfe0fdd11ee96d300155d923235.jpg', -1))

    loop = asyncio.new_event_loop()
    loop.run_until_complete(extra_tasks())
    # asyncio.get_event_loop().run_until_complete(hmfs_client.cleanup_cloud())
