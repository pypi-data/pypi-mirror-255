import os
import re
import base64
import hashlib
import requests
import webbrowser
from authlib.integrations.requests_client import OAuth2Session
from datetime import datetime, timedelta


class FeideOAuth2:
    """
    A class to manage OAuth2 login to Feide for the Kudaf project
    """
    def __init__(self):
        self.state = None
        self.granted_variables = None
        self.basic_auth_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        self.config = self.get_config()

        # OAuth2 setup
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        self.oauth2_session = self.get_oauth2_session()
        self.code_verifier, self.code_challenge = self.gen_code_challenge()

    def get_config(self):
        _config = {}

        # OpenID
        _config['client_id'] = '65eb45e0-c9b8-40cc-b117-0e76832db907'  # JupyterLab Service in Feide KP
        _config['response_type'] = 'code'
        _config['scope'] = 'openid'
        _config['code_challenge_method'] = 'S256'

        # Feide OAuth2 endpoints
        _config['token_endpoint'] = "https://auth.dataporten.no/oauth/token"
        _config['auth_endpoint'] = "https://auth.dataporten.no/oauth/authorization"
        _config['userinfo_endpoint'] = "https://auth.dataporten.no/openid/userinfo"
        _config['permissions_endpoint'] = "https://kudaf-core.paas2.uninett.no/api/v1/permissions/"
        _config['redirect_uri'] = 'http://localhost:8888/kudaf/oauth2-redirect'

        # Datasource/Audience URLs
        _config['datasources_url'] = "https://n.feide.no/datasources/"
        
        return _config 

    def get_oauth2_session(self):
        """
        Create Feide OAuth2 session instance
        """
        oauth2_session = OAuth2Session(
            client_id=self.config.get('client_id'), 
            redirect_uri=self.config.get('redirect_uri'),
            response_type=self.config.get('response_type'),
            scope=self.config.get('scope'),
            code_challenge_method=self.config.get('code_challenge_method'),
        )
        
        return oauth2_session

    async def login(self, ksettings: dict[str, str]) -> dict:
        if not ksettings.get('access_token_expires') or \
            self.is_expired(datetime.fromisoformat(ksettings.get('access_token_expires'))):
            print("Initiating Kudaf Login process...")
            authorize_url, state = await self.authorization_request()
        else:
            print("Already logged in, until {}".format(
                ksettings.get('jwt_token_expires')
            ))

        return ksettings
    
    async def token_refresh(self, access_token: str, datasource_id: str = None):
        jwt_token, jwt_token_expires = await self.token_exchange(access_token, datasource_id)
        print("REFRESHED JWT Token: {}".format(jwt_token))
        return jwt_token, jwt_token_expires

    async def authorization_request(self):
        """
        Feide OAuth2 login step 1: Authorization GET Request
        """
        authorize_url, state = self.oauth2_session.create_authorization_url(
            url=self.config.get('auth_endpoint'),
            code_challenge=self.code_challenge,
            code_verifier=self.code_verifier,
        )
        if authorize_url:
            self.state = state
            webbrowser.open(authorize_url)

        return authorize_url, state

    async def get_access_token(self, code: str, state: str = None):
        """
        Feide OAuth2 login step 2: Access Token POST Request
        """
        if code is not None:
            access_token_request_body = {
                "grant_type": "authorization_code",
                "code": code,
                "state": state if state is not None else self.state,
                "code_verifier": self.code_verifier,
            }
            
            token = self.oauth2_session.fetch_token(
                url=self.config.get('token_endpoint'), 
                headers=self.basic_auth_headers, 
                **access_token_request_body
            )
            atoken = token.get('access_token')
            jupyter_jwt = token.get('id_token')
            atoken_expires = datetime.fromtimestamp(token.get('expires_at'))

            return atoken, jupyter_jwt, atoken_expires
        else:
            return None, None, None

    async def token_exchange(self, access_token: str, datasource_id: str = "", state: str = None):
        """
        Feide OAuth2 login step 3: Token Exchange POST Request
        """
        token_exchange_body = {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "client_id": self.config.get('client_id'),
            "audience": self.config.get('datasources_url') + datasource_id, 
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "subject_token": access_token,
            "state": state if state is not None else self.state,
            "scope": "basic",
        }
        
        print("TOKEN EXCHANGE BODY: {}".format(token_exchange_body))
        response = requests.post(
                url=self.config.get('token_endpoint'),
                headers=self.basic_auth_headers,
                data=token_exchange_body
            )
        print("Token Exchange Response: {}".format(response.json()))
        if response.status_code == 200: 
            jwt_token = response.json().get("access_token")
            jwt_token_expires = datetime.now() + timedelta(seconds=response.json().get('expires_in'))

            # 
            return jwt_token, jwt_token_expires
        else:
            return response.json(), None

    async def get_user_info(self, access_token: str, access_token_expires: datetime) -> dict[str, str]:
        if access_token and not self.is_expired(access_token_expires):
            response = requests.get(
                url=self.config.get('userinfo_endpoint'),
                headers={
                    "Authorization": "Bearer " + access_token,
                    "Accept": "application/json",
                }
            )
            if response.status_code == 200:
                user = {
                    "feide_uuid": response.json().get('sub'),
                    "email": response.json().get('email'),
                    "name": response.json().get('name'),
                }
                print("User Info: {}".format(user))

                return user
            
        return {}

    @staticmethod
    def get_kudaf_settings():
        response = requests.get('http://localhost:8888/kudaf/settings')
        return response.json()

    @staticmethod
    def is_expired(timestamp: datetime) -> bool:
        if timestamp < datetime.now():
            return True 
        else:
            return False 
        
    @staticmethod
    def gen_code_challenge():
        code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
        code_verifier = re.sub('[^a-zA-Z0-9]+', '', code_verifier)
        code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
        code_challenge = code_challenge.replace('=', '')

        return code_verifier, code_challenge


feide_oauth2 = FeideOAuth2()
