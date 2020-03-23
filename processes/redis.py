import os
import redis
import json

class Redis:
    __redis=None
    @staticmethod
    def connect():
        host=os.environ.get('REDIS_HOST')
        port=os.environ.get('REDIS_PORT')
        password=os.environ.get('REDIS_PASSWORD') or ''
        if host is not None and port is not None and password is not None:
            Redis.__redis=redis.Redis(
                host=host,
                port=port, 
                password=password
            )
            try:
                print('Pinging redis connection', Redis.__redis.ping())
            except Exception as err:
                print('Redis is not connected', err)
        else:
            raise Exception('HOST {}, PORT {} and PASSWORD {} should not be NONE for redis connection'.format(host, port, password))

    @staticmethod
    def get_redis_client():
        try:
            if Redis.__redis.ping():
                return Redis.__redis
            else:
                return  None
        except Exception as err:
            print('Redis connection is not valid', err)
            return None