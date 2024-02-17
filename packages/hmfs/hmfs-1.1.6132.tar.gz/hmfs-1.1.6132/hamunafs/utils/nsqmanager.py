
import traceback
from gnsq import Producer
from ansq import open_connection, ConnectionOptions
import asyncio
import orjson
import time

from hamunafs.utils.singleton_wrapper import Singleton


class MQManager(Singleton):
    def __init__(self, host, port, async_mq=False, init=True):
        if not self.need_init():
            return
        self.host = host
        self.port = port
        self.async_mq = async_mq
        self.inited = False
        if init:
            self._init()
        self._inited = True

        self.connection_locker = asyncio.Lock()
    
    def _init(self):
        self.addr = '{}:{}'.format(self.host, self.port)
        self.producer = Producer(nsqd_tcp_addresses=[self.addr])
        self.producer.start()

    async def _init_async(self):
        if self.async_mq:
            self.mq = await open_connection(self.host, self.port, connection_options=ConnectionOptions(debug=True))

    def close(self):
        if not self.async_mq:
            self.close_producer()

    async def close_async(self):
        try:
            if self.async_mq:
                try:
                    await self.mq.close()
                    del self.mq
                except:
                    pass
        except:
            traceback.print_exc()

    async def get_mq_conn(self):
        # async with self.connection_locker:
            # if not hasattr(self, 'mq') or self.mq.status.is_closed:
            #     await self._init_async()
            #     await asyncio.sleep(0.1)
            # else:
            #     if not self.mq.status.is_connected:
            #         is_timeout = False
            #         t = time.time()
            #         while self.mq.status.is_reconnecting:
            #             if time.time() - t > 5:
            #                 is_timeout = True
            #                 break
            #             await asyncio.sleep(0.1)
                    
            #         if self.mq.status.is_connected:
            #             return self.mq
                    
            #         if is_timeout:
            #             await self.close_async()
            #             return None
        async with self.connection_locker:
            if not hasattr(self, 'mq'):
                await self._init_async()
                await asyncio.sleep(0.1)
        return self.mq
            
    def _encode_message(self, message):
        if isinstance(message, str):
            message = message.encode('utf-8')
        else:
            message = orjson.dumps(message)
        return message

    def close_producer(self):
        try:
            self.producer.close()
        except:
            pass 
        
    def restart_producer(self):
        try:
            self.close_producer()
            del self.producer
        except:
            pass
        finally:
            self._init()
            
    def publish(self, topic, message, multi=False):
        try:
            if not self.producer.is_running:
                self.producer.close()
                time.sleep(0.5)
                self._init()
                
            if multi and isinstance(message, list):
                message = list(map(self._encode_message, message))
            else:
                message = self._encode_message(message)
            
            if multi:
                pub_func = self.producer.multipublish
            else:
                pub_func = self.producer.publish
            
            ret = pub_func(topic, message).decode()
        except Exception as e:
            traceback.print_exc()
            ret = 'ERR'
        max_t = 5
        t = 0
        while ret != 'OK' and t < max_t: 
            try:
                ret = pub_func(topic, message).decode()
            except:
                ret = 'ERR'
            if ret == 'ERR':
                time.sleep(1)
            t += 1
        ret = ret == 'OK'
        if ret:
            print('nsq publish success!')
        return ret

    async def __mq_pub(self, topic, message, mq=None, tries=0):
        if tries > 5:
            return False
        if mq is None:
            mq = await self.get_mq_conn()
        try:
            if mq is None:
                return await self.__mq_pub(topic, message, None, tries+1)
                
            resp = await mq.pub(topic, message)
            return resp.is_ok
        except:
            traceback.print_exc()
            await self.close_async()
            return await self.__mq_pub(topic, message, None, tries+1)

    async def async_publish(self, topic, message, mq=None):
        try:
            if isinstance(message, str):
                message = message.encode('utf-8')
            elif isinstance(message, bytes):
                pass
            else:
                message = orjson.dumps(message)

            ret = await self.__mq_pub(topic, message)
            if ret:
                print('published')
            else:
                print('publish failed')
            return ret
        except Exception as e:
            print(traceback.print_exc())
            return False

if __name__ == "__main__":
    manager = MQManager('kafka.ai.hamuna.club', 34150, async_mq=True)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(manager._init_async())
    
    for i in range(100):
        ret = loop.run_until_complete(manager.async_publish('test', 'test'))
        # ret = manager.publish('test', 'test'.encode('utf-8'))
        print(ret)