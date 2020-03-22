import json
from falcon import HTTPUnauthorized, HTTPBadRequest, HTTPInternalServerError

from processes.redis import Redis
from config import ACCESS_TOKEN_VALIDATION_PATHS, AUTHENTICATION_VALIDATION_PATHS

class AuthMiddleware:
    def process_resource(self, req, resp, resource, params):
        template=req.uri_template
        method=req.method
        if 'auth_type' in params and params['auth_type'] == 'login':
            pass
        else:
            if template in AUTHENTICATION_VALIDATION_PATHS and method in AUTHENTICATION_VALIDATION_PATHS[template]:
                auth=req.get_header('Authorization')
                if auth and auth is not None:
                    try:
                        redis_cli=Redis.get_redis_client()
                        auth_info=redis_cli.hget('USERS_APIKEY', auth)
                        if auth_info is not None:
                            auth_info=json.loads(auth_info)
                            if auth_info['is_active']:
                                if template in ACCESS_TOKEN_VALIDATION_PATHS and method in ACCESS_TOKEN_VALIDATION_PATHS[template]:
                                    access_token=req.get_param('access_token')
                                    if access_token and access_token is not None:
                                        if auth_info['access_token'] == access_token:
                                            if not redis_cli.exists(auth_info['access_token']):
                                                raise HTTPUnauthorized(description='Access token is expired. Please login again and continue')
                                        else:
                                            raise HTTPBadRequest(description='Access token is not valid.')
                                    else:
                                        raise HTTPBadRequest(description='Access token is not valid.')
                                else:
                                    raise HTTPUnauthorized(description='access_token is mandatory to acccess the api.')
                            else:
                                raise HTTPBadRequest(description='Client is not active.')
                        else:
                            raise HTTPUnauthorized(description='Token sent in Authroization header is not valid.')
                    except (HTTPUnauthorized, HTTPBadRequest) as err:
                        raise err
                    except Exception as err:
                        print('Exception while accessing redis client instance', err)
                        raise HTTPInternalServerError(description='Something went wrong in server')
                else:
                    raise HTTPUnauthorized(description='Authorization header is mandatory to process the request.')
