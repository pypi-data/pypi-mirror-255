# File: Rest/JSON API + User security. ArangoDB Flavor
# Author: alexsanchezvega
# Company: d20
# Version: 2.0.0

from .Error import *
from pyArango.connection import *
from pyArango.collection import *
from pyArango.graph import *
from dtwentyORM import BasicElement, Metadata, GraphClassFactory
from threading import Thread
import datetime
import hashlib
import binascii
import os
import json

def sl_dbname():
    return f'{os.environ.get("DBPREFIX", "")}security_layer'

class SecurityLayer():

    def __init__(self, conf={}):
        graphname = ''
        collections = ['UserCredentials', 'APICredentials', 'UserTokens', 'APITokens', 'OTP', 'PasswordRecoveryTokens']
        edgeDefinitions={}
        db_name = sl_dbname()
        factory = GraphClassFactory.ClassFactory(graphname, db_name, collections = collections, edgeDefinitions=edgeDefinitions, conf=conf)

        print(factory, " - OK")
                
    class PasswordRecoveryToken(BasicElement):
        def __init__(self, data=None):
            super().__init__(db_name = sl_dbname(), data=data)
            self.collection = 'PasswordRecoveryTokens'

        def make(self):
            self.attributes = ['_key', 'created', 'updated', 'valid_thru', 'active', 'userid', 'username']
            for key in self.attributes:
                setattr(self, key, None)

        def insert(self):
            p = Metadata.Parameter()
            p.load('psswdrec_lifespawn')
            psswdrec_lifespawn = p.get('value')
            self.valid_thru = datetime.datetime.utcnow() + datetime.timedelta(minutes=psswdrec_lifespawn)
            self.active = True
            return super().insert()

        def find(self, _key=None, userid=None, username=None):
            try:
                if userid == None:
                    raise ObjectNotFoundException
                query = [{"dim":"_key", 'op':'==', 'val': _key},
                     {"dim":"active", 'op':'==', 'val': True},
                     {"dim":"userid", 'op':'==', 'val': userid}]
                with open("debug.log", mode='a', encoding='utf-8') as logfile:
                    logfile.write("=================SL PRC find query ================")
                    logfile.write(f"{query}")
                self.search(query_list=query, limit=1)
                if len(self.found) <= 0:
                    raise ObjectNotFoundException
            except ObjectNotFoundException:
                if username == None:
                    raise ObjectNotFoundException
                query = [{"dim":"_key", 'op':'==', 'val': _key},
                     {"dim":"active", 'op':'==', 'val': True},
                     {"dim":"username", 'op':'==', 'val': username}]
                self.search(query_list=query, limit=1)
                if len(self.found) <= 0:
                    raise ObjectNotFoundException

            for key in self.attributes:
                setattr(self, key, self.found[0].get(key) if key in self.found[0].to_dict() else self.get(key, None))
            self.valid_thru = datetime.datetime.strptime(self.valid_thru, '%Y-%m-%d %H:%M:%S.%f')
            self.status = (self.valid_thru >= datetime.datetime.utcnow() and self.active)
            delete_thread = Thread(target=self.found[0].delete)
            delete_thread.start()
        

    class OneTimeAccess(BasicElement):
        def __init__(self, data=None):
            super().__init__(db_name = sl_dbname(), data=data)
            self.collection = 'OTP'

        def make(self):
            self.attributes = ['_key', 'created', 'updated', 'valid_thru', 'active', 'userid', 'username']
            for key in self.attributes:
                setattr(self, key, None)

        def insert(self):
            p = Metadata.Parameter()
            p.load('otp_lifespawn')            
            otp_lifespawn = p.get('value')
            self.valid_thru = datetime.datetime.utcnow() + datetime.timedelta(minutes=otp_lifespawn)
            self.active = True
            return super().insert()

        def find(self):
            query = [{"dim":"_key", 'op':'==', 'val': self._key},
                     {"dim":"active", 'op':'==', 'val': True},
                     {"dim":"userid", 'op':'==', 'val': self.userid}]
            try:
                self.search(query_list=query, limit=1)
            except ORM_Error.ObjectNotFoundException:
                query = [{"dim":"_key", 'op':'==', 'val': self._key},
                     {"dim":"active", 'op':'==', 'val': True},
                     {"dim":"username", 'op':'==', 'val': self.userid}]
                self.search(query_list=query, limit=1)

            for key in self.attributes:
                setattr(self, key, self.found[0].get(key) if key in self.found[0].to_dict() else self.get(key, None))
            self.valid_thru = datetime.datetime.strptime(self.valid_thru, '%Y-%m-%d %H:%M:%S.%f')
            self.status = (self.valid_thru >= datetime.datetime.utcnow() and self.active)
            delete_thread = Thread(target=self.found[0].delete)
            delete_thread.start()
        

    class UserToken(BasicElement):
        def __init__(self, data=None):
            super().__init__(db_name = sl_dbname(), data=data)
            self.collection = 'UserTokens'

        def make(self):
            self.attributes = ['_key', 'created', 'updated', 'valid_thru', 'active', 'userid', 'username', 'password', 'oauth', 'oauth_client', 'scopes', 'delegated', 'can_write', 'isadmin']
            for key in self.attributes:
                setattr(self, key, None)
        
        def auth(self):
            user = SecurityLayer.UserAccess(data={"username" : self.get('userid', self.get('username')), 'password' : self.get('password')})
            self.password = None
            
            if user.auth()==True:
                self.userid = user.get('_key')
                self.insert()
            else: 
                raise SSOInvalidCredentialsException

        def insert(self):
            p = Metadata.Parameter()
            p.load('user_token_lifespawn')
            user_token_lifespawn = p.get('value')
            self.valid_thru = datetime.datetime.utcnow() + datetime.timedelta(minutes=user_token_lifespawn)
            self.active = True
            return super().insert()

        def find(self):
            query = [{"dim":"_key", 'op':'==', 'val': self._key},
                     {"dim":"oauth" if self.get('oauth') == True else "active", 'op':'==', 'val': True},
                     {"dim":"userid", 'op':'==', 'val': self.userid}]
            try:
                self.search(query_list=query, limit=1)
            except ORM_Error.ObjectNotFoundException:
                query = [{"dim":"_key", 'op':'==', 'val': self._key},
                     {"dim":"oauth" if self.get('oauth') != True else "active", 'op':'==', 'val': True},
                     {"dim":"username", 'op':'==', 'val': self.userid}]
                self.search(query_list=query, limit=1)
            if len(self.found) < 1:
                raise SSOInvalidTokenException
            for key in self.attributes:
                setattr(self, key, self.found[0].get(key) if key in self.found[0].to_dict() else self.get(key, None))
            self.valid_thru = datetime.datetime.strptime(self.valid_thru, '%Y-%m-%d %H:%M:%S.%f')
            if self.get('oauth') != True and (self.valid_thru < datetime.datetime.utcnow() or not self.active):
                self.active = False
                delete_thread = Thread(target=self.found[0].delete)
                delete_thread.start()
                raise SSOInvalidTokenException
            else:
                self.active = True
                p = Metadata.Parameter()
                p.load('user_token_lifespawn')
                user_token_lifespawn = p.get('value')
                self.valid_thru = datetime.datetime.utcnow() + datetime.timedelta(minutes=user_token_lifespawn)
                update_thread = Thread(target=self.update)
                update_thread.start()
            self.status = self.active
            self.id = self.get("_key", None)

    class UserAccess(BasicElement):
        def __init__(self, data=None):
            super().__init__(db_name = sl_dbname(), data=data)
            self.collection = 'UserCredentials'

        def make(self):
            self.attributes = ['_key', 'password', 'username', 'created', 'updated']
            for key in self.attributes:
                setattr(self, key, None)
        
        def auth(self):
            return self.verify_password()

        def insert(self):
            self.password = self.hash_password()
            self.active = True
            return super().insert()
            
        def verify_password(self):
            received_password = self.get("password")
            try:
                self.load(self.get('username'))
            except:
                query = [{"dim":"username", 'op':'==', 'val': self.get('username')}]
                self.search(query_list=query)
                try:
                    self.load(self.found[0].get('_key'))
                except IndexError:
                    return False
            self.id = self.get("_key")
            stored_password = self.get("password")
            salt = stored_password[:64]
            stored_password = stored_password[64:]
            pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                        received_password.encode('utf-8'), 
                                        salt.encode('ascii'), 
                                        100000)
            pwdhash = binascii.hexlify(pwdhash).decode('ascii')
            return pwdhash == stored_password
        
        def hash_password(self):
            salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
            pwdhash = hashlib.pbkdf2_hmac('sha512', self.password.encode('utf-8'), 
                                        salt, 100000)
            pwdhash = binascii.hexlify(pwdhash)
            return (salt + pwdhash).decode('ascii')

        def update(self):
            self.id = self.get('_key')
            if self.password != None and self.password != '':
                self.password = self.hash_password()
            else:
                self.password = None
            super().update()
        
    class AccessToken(BasicElement):
        def __init__(self, data=None):
            super().__init__(db_name = sl_dbname(), data=data)
            self.collection = 'APITokens'


        def make(self):
            self.attributes = ['_key', 'created', 'updated', 'valid_thru', 'active', 'deleted', 'apiuser', 'apisecret', 'origin', 'partners', 'actions', 'allowed_types','permalink', 'oauth', 'oauth_urls', 'oauth_scopes', 'scopes']
            for key in self.attributes:
                setattr(self, key, None)
        
        def add_partner(self, partner_code):
            if self.partners == None:
                self.partners = []
            self.partners.append(partner_code)
            self.update()

        def build_from_access(self, api_access) -> None:
            api_access._key=None
            self.set_from_dict(api_access.to_dict())
            self.apisecret = ''
            self.password = ''

        def auth(self):
            api_access = SecurityLayer.APIAccess(data={"username" : self.get('apiuser'), 'password' : self.get('apisecret')})
            self.password = None
            if api_access.auth()==True:
                self.build_from_access(api_access)
                self._key = None
                self.insert()
            else:
                raise SSOInvalidCredentialsException

        def insert(self):
            if self.get('origin') == None or self.get('origin') == '':
                self.origin = ['NoCors']
            if not isinstance(self.get('origin'), list):
                self.origin = [self.get('origin')]
            if not isinstance(self.get('oauth_urls'), list):
                self.oauth_urls = [self.get('oauth_urls')]
            if self.get('permalink') == True:
                self.valid_thru = datetime.datetime.utcnow() + datetime.timedelta(weeks=52000)
            else:
                p = Metadata.Parameter()
                p.load('api_token_lifespawn')
                api_token_lifespawn = p.get('value')
                self.valid_thru = datetime.datetime.utcnow() + datetime.timedelta(minutes=api_token_lifespawn)
            self.active = True
            self.deleted = False
            return super().insert()

        def find(self):
            self.id = self.get('_key')
            origin = self.get('origin')
            self.load(self.id)
            if origin == None or origin == '':
                origin = 'NoCors'
            if max([origin.find(url) for url in self.get('origin', [])]) != 0 and max(['any'.find(url) for url in self.get('origin', [])]) != 0:
                raise SSOInvalidTokenException
            self.valid_thru = datetime.datetime.strptime(self.valid_thru, '%Y-%m-%d %H:%M:%S.%f')
            if self.valid_thru < datetime.datetime.utcnow() or not self.active:
                self.active = False
                delete_thread = Thread(target=self.delete)
                delete_thread.start()
            else:
                if self.permalink != True:
                    p = Metadata.Parameter()
                    p.load('api_token_lifespawn')
                    api_token_lifespawn = p.get('value')
                    self.valid_thru = datetime.datetime.utcnow() + datetime.timedelta(minutes=api_token_lifespawn)
                    update_thread = Thread(target=self.update)
                    update_thread.start()
            self.status = self.active


    class APIAccess(BasicElement):
        def __init__(self, data=None):
            super().__init__(db_name = sl_dbname(), data=data)
            self.collection = 'APICredentials'

        # V2
        @property
        def password(self):
            return getattr(self, '_password', None)

        @password.setter
        def password(self, value):
            self._password = value
            self.hashed = False
            
        def load(self, id, get_if_deleted=False):
            super().load(id, get_if_deleted=get_if_deleted)
            self.hashed=True

        def make(self):
            self.attributes = ['_key', 'password', 'username', 'created', 'updated', 'partners', 'actions', 'email', 'active', 'oauth_urls', 'oauth_scopes', 'allowed_types', 'deleted']
            for key in self.attributes:
                setattr(self, key, None)

        def update_all_tokens(self):
            tokens_list = SecurityLayer.AccessToken()
            query = [{"dim":"username", 'op':'==', 'val': self.get('username')}]
            tokens_list.search(query_list=query)
            for t in tokens_list.found:
                t.build_from_access(self)
                try:
                    t.update()
                except:
                    pass
        
        def add_partner(self, partner_code):
            if self.partners == None:
                self.partners = []
            self.partners.append(partner_code)
            self.update()
        
        def auth(self):
            return self.verify_password()
            
        def verify_password(self):
            received_password = self.get("password")
            try:
                self.load(self.get('username'))
            except:
                query = [{"dim":"username", 'op':'==', 'val': self.get('username')}]
                self.search(query_list=query)
                try:
                    self.load(self.found[0].get('_key'))
                except IndexError:
                    return False
            self.id = self.get("_key")
            stored_password = self.get("password")
            salt = stored_password[:64]
            stored_password = stored_password[64:]
            pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                        received_password.encode('utf-8'), 
                                        salt.encode('ascii'), 
                                        100000)
            pwdhash = binascii.hexlify(pwdhash).decode('ascii')
            return pwdhash == stored_password

        def hash_password(self):
            salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
            pwdhash = hashlib.pbkdf2_hmac('sha512', self.password.encode('utf-8'), 
                                        salt, 100000)
            pwdhash = binascii.hexlify(pwdhash)
            return (salt + pwdhash).decode('ascii')

        def update(self):
            if self.password != None and self.password != '':
                if self.get('hashed') != True:
                    self.password = self.hash_password()
                    self.hashed = True
            else:
                self.password = None
            return super().update()

        def insert(self):
            if self.password == None or self.password == '':
                raise Error(message='Password required for insertion')
            access = SecurityLayer.APIAccess()
            if self.get('hashed') != True:
                self.password = self.hash_password()
                self.hashed = True
            try:
                access.load(self.get('username'))
            except ObjectNotFoundException:
                query = [{"dim":"username", 'op':'==', 'val': self.get('username')}]
                access.search(query_list=query)
                if len(access.found) <= 0:
                    return super().insert()
                access.load(access.found[0].get('_key'))
                self._key = access.found[0].get('_key')
                access.set(data=self.to_dict(), id=access.id)
                access.update()
            