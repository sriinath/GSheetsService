from falcon import HTTPInternalServerError, HTTPError
from googleapiclient.errors import HttpError
from secrets import token_urlsafe

from processes.redis import Redis

class Base:
    # run must be a function 
    # it will throw any new exception while executing the function
    def main(self, run):
        try:
            if callable(run):
                run()
            else:
                raise Exception('run argument must be executable')
        # HttpError is different from HTTPError
        # HttpError is error from googleapiclient
        # HTTPError belongs to falcon
        except HttpError as err:
            status_code=err.resp.status
            if status_code==404:
                from falcon import HTTP_404
                falcon_status=HTTP_404
            elif status_code==403:
                from falcon import HTTP_403
                falcon_status=HTTP_403
            else:
                from falcon import HTTP_400
                falcon_status=HTTP_400
            raise HTTPError(falcon_status, description=err._get_reason() or '', code=status_code)
        except Exception as err:
            print('Exception in getting spreadsheet info', err)
            raise HTTPInternalServerError(description='Something went wrong while getting sheets info')

    def generate_token(self, nbytes=32):
        return token_urlsafe(nbytes)

    @property
    def redis_client(self):
        try:
            return Redis.get_redis_client()
        except Exception as err:
            print('Exception while accessing redis client instance', err)

    