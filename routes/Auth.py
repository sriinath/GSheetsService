import hashlib
import json
from json.decoder import JSONDecodeError
from falcon import HTTPBadRequest, \
    HTTPPreconditionFailed, \
    HTTPServiceUnavailable, \
    HTTPUnprocessableEntity, \
    HTTPInternalServerError, \
    HTTPNotFound, \
    HTTP_200, \
    HTTPUnauthorized, \
    HTTPNotAcceptable

from routes.Base import Base

class Auth(Base):
    def on_post(self, req, resp, auth_type):
        if auth_type == 'login':
            try:
                req_body=json.load(req.bounded_stream)
                if 'username' in req_body and req_body['username'] and 'password' in req_body and len(req_body['password']) > 5:
                    username=req_body['username']
                    redis_cli=super().redis_client
                    if redis_cli is not None:
                        user_info=redis_cli.hget('USERS', username)
                        if user_info is not None:
                            user_info=json.loads(user_info)
                            api_key=user_info['api_key']
                            hash_password=hashlib.pbkdf2_hmac(
                                'sha256',
                                req_body['password'].encode('utf-8'),
                                api_key[8:32].encode('utf-8'),
                                100000,
                                dklen=128
                            )
                            if user_info['password']==hash_password.hex():
                                access_info=redis_cli.hget('USERS_APIKEY', api_key)
                                access_info=json.loads(access_info)
                                if access_info is not None and access_info['is_active']:
                                    access_token=access_info['access_token']
                                    if not redis_cli.exists(access_token):
                                        access_token=super().generate_token(32)
                                        access_info['access_token']=access_token
                                        access_info=redis_cli.hset('USERS_APIKEY', api_key, json.dumps(access_info))
                                    redis_cli.set(access_token, api_key, ex=28800)
                                    resp.status=HTTP_200
                                    resp.body=json.dumps(dict(
                                        status='Success',
                                        user=dict(
                                            api_key=api_key,
                                            access_token=access_token,
                                            username=username
                                        )
                                    ))
                                else:
                                    raise HTTPNotAcceptable(description='User is not active')
                            else:
                                raise HTTPUnauthorized(description='Username and password doesnot match')
                        else:
                            raise HTTPNotFound(description='No user with username {}'.format(username))
                    else:
                        raise HTTPServiceUnavailable(description='Data instances are not yet active')
                else:
                    raise HTTPPreconditionFailed(description='Username and password are mandatory and must be valid for this request')
            except JSONDecodeError as err:
                print('Request body received', req.bounded_stream.read())
                print('Error while processing request', err)
                raise HTTPUnprocessableEntity(description='Cannot parse the body from the request')
            except (HTTPPreconditionFailed, HTTPServiceUnavailable, HTTPNotFound, HTTPUnauthorized, HTTPNotAcceptable) as err:
                raise err
            except Exception as e:
                print('Exception in signing in user', e)
                raise HTTPInternalServerError(description='Something went wrong while creating user info')
        elif auth_type== 'logout':
            try:
                api_key=req.get_header('Authorization')
                redis_cli=super().redis_client
                if redis_cli is not None:
                    access_info=redis_cli.hget('USERS_APIKEY', api_key)
                    access_info=json.loads(access_info)
                    access_token=access_info['access_token']
                    redis_cli.delete(access_token)
                    resp.status=HTTP_200
                    resp.body=json.dumps(dict(
                        status='Succcess',
                        message='Successfully signed out'
                    ))
                else:
                    raise HTTPServiceUnavailable(description='Data instances are not yet active')
            except Exception as err:
                print('Exception while signing out', err)
                raise HTTPInternalServerError(description='Something went wrong while signing out')
        else:
            raise HTTPBadRequest(description='The request is not valid')