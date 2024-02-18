from future.utils import raise_
from .SecurityLayer import SecurityLayer
from .AuthAnswer import AuthAnswer
from cryptography.fernet import Fernet
from .Error import *
import os
import json
from .default import crypt as D20_SL_CRYPTOKEY

# def api_back_auth(request=None, **kwargs):
def api_back_auth(auth_type = None, auth=None, oauth=False, client_id=None, origin=None, permalink=False, action_details={}, action=None):
    try:
        token = _api_auth(auth_type = auth_type, auth=auth, oauth=oauth, client_id=client_id, origin=origin, permalink=permalink)
        if token.get('_key') == None:
            return AuthAnswer(False, error= SSOInvalidCredentialsError())
        if permalink == True and 'pl' not in token.get('actions') and 'sso' not in token.get('actions'):
            return AuthAnswer(False, error= SSONoPermalinksAllowedError())
        if action_details.get('action', None) != None:
            if action_clearance(token, action_details.get('action')) != True:
                return AuthAnswer(False, error=  SSOAccessDeniedError(action_details.get('action')))
        if action_details.get('clearance', None) != None:
            if access_clearance(token, action_details.get('clearance'), action) != True:
                return AuthAnswer(False, error=   SSOAccessDeniedError(action_details.get('clearance'), action))
        if action_details.get('object_action', None) != None:
            if object_action_clearance(token, action_details.get('object_action'), action) != True:
                return AuthAnswer(False, error=   SSOAccessDeniedError(action_details.get('object_action'), action))
        return AuthAnswer(True, token=token)
    except HTTPError as e:
        return AuthAnswer(False, error= e())


def _api_auth(auth_type = None, auth=None, oauth=False, client_id=None, origin=None, permalink=False):
    if oauth == True and client_id != None:
        token_id = client_id
    elif auth != None and auth_type != None:
        if auth_type == 'BEARER':
            token_id = client_id
        elif auth_type == 'BASIC':
            user = auth.get('username')
            secret = auth.get('password')
            token = SecurityLayer.AccessToken(data={
                'apiuser':user,
                'apisecret':secret,
                'origin':origin,
                'permalink':permalink,
                'oauth':oauth
            })
            token.auth()
            return token
    else:
        raise SSONoCredentialsError
    token = SecurityLayer.AccessToken(data={
        '_key':token_id,
        'origin':origin
    })
    token.find()
    return token

    # if request.headers.get('Authorization', '').split(" ")[0].upper() == 'BEARER':
    #     token_id = request.headers.get('Authorization').split(" ")[1]
    #     token = SecurityLayer.AccessToken(data= {'_key':token_id, 'origin' : request.headers.get('origin',request.headers.get('referer',''))})
    #     try:
    #         token.find()
    #     except HTTPError as e:
    #         AuthAnswer(False, error= e())
    # elif request.headers.get('Authorization', '').split(" ")[0].upper() == 'BASIC':
    #     jr['apiuser'] = request.authorization.get('username')
    #     jr['apisecret'] = request.authorization.get('password')
    #     jr['origin'] = request.headers.get('origin',request.headers.get('referer',''))
    #     jr['permalink'] = kwargs.get('permalink', False)
    #     if jr.get('permalink', False) == True:
    #         jr['permalink'] = jr.get('permalink', False)
    #         jr['origin'] = jr.get('permalink_origin', jr['origin'])
    #     jr['oauth'] = kwargs.get('oauth', False)
    #     token = SecurityLayer.AccessToken(data=jr)
    #     try:
    #         token.auth()
    #     except HTTPError as e:
    #         AuthAnswer(False, error= e())
    # elif (kwargs.get('oauth', False) == True or kwargs.get('file_req', False) == True) and request.args.get('client_id', '') != '':
    #     token_id = request.args.get('client_id', '')
    #     token = SecurityLayer.AccessToken(data= {'_key':token_id, 'origin' : request.headers.get('origin',request.headers.get('referer',''))})
    #     try:
    #         token.find()
    #     except HTTPError as e:
    #         AuthAnswer(False, error= e())
    # else:
    #     return AuthAnswer(False, error= SSONoCredentialsError())
    # if token.get('_key') == None:
    #     return AuthAnswer(False, error= SSOInvalidCredentialsError())
    # if jr.get('permalink', False) == True and 'pl' not in token.get('actions') and 'sso' not in token.get('actions'):
    #     return AuthAnswer(False, error= SSONoPermalinksAllowedError())
    # if 'action' in kwargs:
    #     if action_clearance(token, kwargs.get('action'),  jr=jr) != True:
    #         return AuthAnswer(False, error=  SSOAccessDeniedError(kwargs.get('action')))
    # if 'clearance' in kwargs:
    #     if access_clearance(token, kwargs.get('clearance'), request.method, jr=jr) != True:
    #         return AuthAnswer(False, error=   SSOAccessDeniedError(kwargs.get('clearance'), request.method))
    # if 'object_action' in kwargs:
    #     if object_action_clearance(token, kwargs.get('object_action'), request.method, jr=jr) != True:
    #         return AuthAnswer(False, error=   SSOAccessDeniedError(kwargs.get('clearance'), request.method))
    # return AuthAnswer(True, token=token)




def user_back_auth(user_id, password=None, token_id=None, access_code=None, oauth=False, apiuser=None, scopes=None, delegated_action=None):
    user_token = _user_auth(user_id, password=password, token_id=token_id, access_code=access_code, oauth=oauth, apiuser=apiuser, scopes=scopes)
    if user_token.get('delegated', None) != None and delegated_clearance(user_token, delegated_action) != True:
        raise SSOInvalidUserTokenError
    return AuthAnswer(True, token=user_token)


def _user_auth(user_id, password=None, token_id=None, access_code=None, oauth=False, apiuser=None, scopes=None):
#     jr={}
#     if request.content_type == 'application/json' and request.get_json(silent=True) != None:
#         jr.update(request.get_json(silent=True))
#     elif request.content_type != None and request.content_type.split(";")[0] == 'multipart/form-data':
#         jr.update(request.form.to_dict())
#     if request.args != None:
#         jr.update(request.args.to_dict())
#     jr['oauth'] = oauth
#     access_code = request.headers.get('Oauth-Token', request.headers.get('Access-Token', jr.get('Oauth-Token', jr.get('access_token', request.args.get('user_token', '')))))
#     token_id = request.headers.get('UserToken', jr.get('UserToken', ''))
#     user_id = request.headers.get('UserId', kwargs.get('UserId', jr.get('UserId', jr.get('_key', ''))))
    if token_id != None:
        token = SecurityLayer.UserToken(data={'_key': token_id, 'userid': user_id})
        token.find()
    elif password != None:
        token = SecurityLayer.UserToken(data={'username':user_id, 'password':password, 'oauth': oauth, 'oauth_client': apiuser, 'scopes': scopes})
        try:
            token.auth()
        except HTTPError:
            token_id = password
            otp = SecurityLayer.OneTimeAccess(data= {'_key': token_id, 'username': user_id})
            otp.find()
            token = SecurityLayer.UserToken(data={'username': user_id, 'oauth': oauth, 'oauth_client': apiuser, 'scopes': scopes, 'userid': otp.get('userid')})
            token.insert()  
    elif oauth == True and access_code != None:
        try:
            token = break_access_token(access_code)
        except:
            raise SSOInvalidUserTokenError
            # return AuthAnswer(False, error= SSOInvalidUserTokenError())
        # token = SecurityLayer.UserToken('find', {'_key': token_id, 'userid': userid})
        # if token.get('status') != True:
        #     return AuthAnswer(False, error= SSOInvalidUserTokenError())
    else:
        raise SSONoCredentialsError
        # return AuthAnswer(False, error= SSONoCredentialsError())
    # if token.get("_key", None) == None:
    #     return AuthAnswer(False, error= SSOInvalidUserTokenError())
    return token

def access_clearance(api_token: SecurityLayer.AccessToken, obj_type: str, action: str, **kwargs) -> bool:
    if not obj_type in api_token.get('allowed_types'):
        return False
    if action == 'PUT':
        permission = 'create'
    elif action == 'DELETE':
        permission = 'create'
    elif action == 'GET':
        permission = 'display'
    elif action == 'POST':
        permission = 'search'
    elif action == 'PATCH':
        permission = 'update'
    if not permission in api_token.get('allowed_types')[obj_type]:
        return False
    return True

def object_action_clearance(api_token: SecurityLayer.AccessToken, obj_type: str, action: str, **kwargs) -> bool:
    if not obj_type in api_token.get('allowed_types'):
        return False
    if action == 'PUT':
        permission = 'C'
    elif action == 'DELETE':
        permission = 'D'
    elif action == 'GET':
        permission = 'R'
    elif action == 'POST':
        permission = 'A'
    elif action == 'PATCH':
        permission = 'U'
    if api_token.get('allowed_types')[obj_type].find(permission) < 0:
        return False
    return True

def action_clearance(api_token: SecurityLayer.AccessToken, action: str, **kwargs) -> bool:
    return action in api_token.get('actions')

def scope_clearance(api_token: SecurityLayer.UserToken, scope: str, **kwargs) -> bool:
    return scope in api_token.get('scopes')

def delegated_clearance(user_token: SecurityLayer.UserToken, action: str, **kwargs) -> bool:
    if user_token.get('isadmin', False) == True:
        return True
    if action in ['GET', 'POST']:
        return True
    return user_token.get('can_write', False)

def action_user(user_token: SecurityLayer.UserToken, **kwargs) -> str:
    return user_token.get('delegated', user_token.get('userid'))

def gen_access_token(user_token: SecurityLayer.UserToken, **kwargs) -> str:
    userid = user_token.get('userid')
    tokenid = user_token.get('_key')
    crypt =  os.environ.get('CRYPTOKEY', D20_SL_CRYPTOKEY)

    f = Fernet(crypt)
    access_token = f.encrypt(bytes(f'{userid}.{tokenid}', 'utf-8')).decode()
    return access_token

def break_access_token(access_token:str) -> SecurityLayer.UserToken:
    crypt =  os.environ.get('CRYPTOKEY', D20_SL_CRYPTOKEY)

    f = Fernet(crypt)
    userid, token_id = f.decrypt(bytes(access_token, 'utf-8')).decode().split('.')
    token = SecurityLayer.UserToken(data={'_key': token_id, 'userid': userid})
    token.find()
    return token

def gen_refresh_token(user_token: SecurityLayer.UserToken, **kwargs) -> str:
    userid = user_token.get('userid')
    tokenid = user_token.get('_key')
    crypt =  os.environ.get('CRYPTOKEY', D20_SL_CRYPTOKEY)

    f = Fernet(crypt)
    access_token = f.encrypt(bytes(f'{tokenid}.{userid}', 'utf-8')).decode()
    return access_token

def break_refresh_token(access_token:str) -> SecurityLayer.UserToken:
    crypt =  os.environ.get('CRYPTOKEY', D20_SL_CRYPTOKEY)

    f = Fernet(crypt)
    token_id, userid = f.decrypt(bytes(access_token, 'utf-8')).decode().split('.')
    token = SecurityLayer.UserToken(data={'_key': token_id, 'userid': userid})
    token.find()
    return token

def api_access_from_token(api_token: SecurityLayer.AccessToken) -> SecurityLayer.APIAccess:
    api_access = SecurityLayer.APIAccess(data={'username':api_token.get('apiuser')})
    api_access.load_multikey(['username'])
    return api_access

def gen_password_token(user_token: SecurityLayer.PasswordRecoveryToken, **kwargs) -> str:
    userid = user_token.get('userid')
    tokenid = user_token.get('_key')
    crypt =  os.environ.get('CRYPTOKEY', D20_SL_CRYPTOKEY)

    f = Fernet(crypt)
    access_token = f.encrypt(bytes(f'passwordrec.{tokenid}.{userid}', 'utf-8')).decode()
    return access_token

def break_password_token(access_token:str) -> SecurityLayer.UserToken:
    crypt =  os.environ.get('CRYPTOKEY', D20_SL_CRYPTOKEY)

    f = Fernet(crypt)
    val, token_id, userid = f.decrypt(bytes(access_token, 'utf-8')).decode().split('.')
    if val != 'passwordrec':
        raise ObjectNotFoundException
    token = SecurityLayer.PasswordRecoveryToken()
    token.find(_key=token_id, userid= userid)
    return token


