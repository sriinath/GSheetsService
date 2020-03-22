import hashlib
import json
from json.decoder import JSONDecodeError
from base64 import b64encode
from falcon import HTTPPreconditionFailed, \
    HTTPUnprocessableEntity, \
    HTTPInternalServerError, \
    HTTPServiceUnavailable, \
    HTTPConflict, \
    HTTPNotFound, \
    HTTP_201, \
    HTTP_200

from routes.Base import Base

class User(Base):
    def on_post(self, req, resp, username):
        try:
            req_body=json.load(req.bounded_stream)
            if username and 'password' in req_body and len(req_body['password']) > 5:
                redis_cli=super().redis_client
                if redis_cli is not None:
                    password=req_body['password']
                    api_key=super().generate_token(32)
                    access_token=super().generate_token(32)
                    hash_password = hashlib.pbkdf2_hmac(
                        'sha256',
                        password.encode('utf-8'),
                        api_key[8:32].encode('utf-8'),
                        100000,
                        dklen=128
                    )
                    user_info=dict(
                        username=username,
                        password=hash_password.hex(),
                        api_key=api_key
                    )
                    access_info=dict(
                        username=username,
                        is_active=True,
                        access_token=access_token
                    )
                    try:
                        if not redis_cli.hexists('USERS', username):
                            redis_cli.hset('USERS', username, json.dumps(user_info))
                            redis_cli.hset('USERS_APIKEY', api_key, json.dumps(access_info))
                            redis_cli.set(access_token, api_key, ex=28800)
                            resp.status=HTTP_201
                            resp.body=json.dumps(dict(
                                status='Succcess',
                                message='Successfully created the user',
                                user=dict(
                                    api_key=api_key,
                                    access_token=access_token,
                                    username=username
                                )
                            ))
                        else:
                            raise HTTPConflict(description='User already exists with username {}'.format(username))
                    except HTTPConflict as err:
                        raise err
                    except Exception as err:
                        raise Exception('Something went wrong while executing redis commands', err)
                else:
                    raise HTTPServiceUnavailable(description='Data instances are not yet active')
            else:
                raise HTTPPreconditionFailed(description='Username and password are mandatory and must be valid for this request')
        except JSONDecodeError as err:
            print('Request body received', req.bounded_stream.read())
            print('Error while processing request', err)
            raise HTTPUnprocessableEntity(description='Cannot parse the body from the request')
        except (HTTPPreconditionFailed, HTTPServiceUnavailable, HTTPConflict) as err:
            raise err
        except Exception as e:
            print('Exception in creating user', e)
            raise HTTPInternalServerError(description='Something went wrong while creating user info')

    def on_get(self, req, resp, username):
        try:
            redis_cli=super().redis_client
            if redis_cli is not None:
                user_info=redis_cli.hget('USERS', username)
                access_info=redis_cli.hget('USERS_APIKEY', user_info['api_key'])
                access_token=''
                if access_info is not None and access_info['access_token']:
                    if redis_cli.exists(access_info['access_token']):
                        access_token=access_info['access_token']
                if user_info is not None:
                    user_info=json.loads(user_info)
                    resp.status=HTTP_200
                    resp.body=json.dumps(dict(
                        status='Success',
                        user=dict(
                            username=user_info['username'],
                            api_key=user_info['api_key'],
                            access_token=access_token
                        )
                    ))
                else:
                    raise HTTPNotFound(description='No user with username {}'.format(username))
            else:
                raise HTTPServiceUnavailable(description='Data instances are not yet active')
        except (HTTPNotFound, HTTPServiceUnavailable) as e:
            raise e
        except Exception as e:
            print('Exception in getting user', e)
            raise HTTPInternalServerError(description='Something went wrong while getting user info')
                
    def on_delete(self, req, resp, username):
        try:
            redis_cli=super().redis_client
            if redis_cli is not None:
                user_info=redis_cli.hdel('USERS', username)
                if user_info:
                    resp.status=HTTP_200
                    resp.body=json.dumps(dict(
                        status='Success',
                        message='Successfully deleted the user'
                    ))
                else:
                    raise HTTPNotFound(description='No user with username {}'.format(username))
            else:
                raise HTTPServiceUnavailable(description='Data instances are not yet active')
        except (HTTPNotFound, HTTPServiceUnavailable) as e:
            raise e
        except Exception as e:
            print('Exception in deleting user', e)
            raise HTTPInternalServerError(description='Something went wrong while deleting user info')

    def on_put(self, req, resp, username):
        token=req.get_header('Authorization')
        is_active=req.get_param_as_bool('is_active', required=True)
        try:
            redis_cli=super().redis_client
            if redis_cli is not None and 'auth_info' in req.context:
                temp_auth_info=json.loads(req.context['auth_info'])
                temp_auth_info.is_active=is_active
                redis_cli.hset('USERS_APIKEY', token, json.dumps(temp_auth_info))
                resp.status=HTTP_200
                resp.body=json.dumps(dict(
                    status='Success',
                    message='Successfully updated the staus of the user'
                ))
            else:
                raise HTTPServiceUnavailable(description='Data instances are not yet active')
        except (HTTPNotFound, HTTPServiceUnavailable) as e:
            raise e
        except Exception as e:
            print('Exception in deleting user', e)
            raise HTTPInternalServerError(description='Something went wrong while deleting user info')
