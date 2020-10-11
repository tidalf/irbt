"""
Cloud class for authentication and connexion setup.

It allow interactions with the irbt cloud api
"""
import json
from urllib.parse import urlparse

from aws_requests_auth.aws_auth import AWSRequestsAuth

import requests

from .logger import logging

logger = logging.getLogger(__name__)


class Cloud:
    """
    Cloud class.

    It allow interactions with the irbt cloud api
    """

    api = None

    class Api:
        """
        Api class.

        HTTP cloud api
        """

        cloud = None

        def __init__(self, cloud):
            """Init our cloud."""
            self.cloud = cloud

        def get(self, *a, params=None, as_json=True):
            """
            HTTP GET.

            Authenticated GET method
            """
            parts = [
                self.cloud._disc_api['httpBaseAuth'],
                self.cloud._api_version
            ]
            parts.extend(a)

            response = requests.get('/'.join(parts),
                                    params=params,
                                    auth=self.cloud.auth)
            if response.status_code != 200:
                if response.status_code == 403:
                    logger.error('Authentication failed, provided aws '
                                 'credentials are unauthorized for the '
                                 'requested endpoint: %s',
                                 '/'.join(parts))
                    logger.error('Possible token expiration, trying renewal:')
                    if self.cloud.login(username=self.cloud.username,
                                        password=self.cloud.password):
                        logger.error('renewal successfull')
                        response = requests.get('/'.join(parts),
                                                params=params,
                                                auth=self.cloud.auth)
                        if response.status_code != 200:
                            raise Exception('CloudAPIGetError<{}>'.format(
                                response.status_code))
                    else:
                        logger.error('something wrong, cannot login.')
                    # return self.get(a, params, as_json)
                else:
                    raise Exception('CloudAPIGetError<{}>'.format(
                        response.status_code))
            if as_json:

                return response.json()
            return response

    def __init__(self, username=None, password=None):
        """
        Initialize usefull params.

        Use user credentials to call the login method during the init
        if provided.
        """
        self._disc_api = None
        self._api_version = 'v1'
        self.service_url = None
        self._api_key = None
        self._aws_host = None
        self._aws_region = None
        self._http_base = None
        self.app_id = 'ANDROID-5B4E9B96-C1A8-48BE-ACD7-B41C9F3DC1DE'
        self.auth = None
        self.mqtt_endpoint = None
        self.mqtt_topic = None
        self.debug_mqtt = None
        self.access_key_id = None
        self.secret_key = None
        self.session_token = None
        self.shadow_client = None
        self.device = None
        self.username = None
        self.password = None

        if username and password:
            # save them for reauth
            self.username = username
            self.password = password
            # then login
            self.login(username=username, password=password)
        self.api = Cloud.Api(self)
    # discover the current api and mqtt params

    def _disc(self):
        params = {
            'country_code': 'FR'
        }
        self._disc_api = json.loads(
            requests.get(
                'https://disc-prod.iot.irobotapi.com/v1/app/discover',
                params=params)
            .content.decode('utf-8'))

        # check if all the needed keys are there
        api_keys = ['gigya', 'httpBaseAuth', 'httpBase', 'awsRegion',
                    'mqtt', 'irbtTopics']
        for api_key in api_keys:
            if api_key not in self._disc_api.keys():
                logger.error('discover url not working, %s key is not there',
                             api_key)
                return -1
        if 'api_key' not in self._disc_api['gigya'].keys():
            logger.error('discover url is not working, api key is not there')
            return -1

        self._api_key = self._disc_api['gigya']['api_key']  # gigya api key

        # the aws api service url
        # used for aws api gateway request
        self.service_url = '%s/%s/' % (
            self._disc_api['httpBaseAuth'], self._api_version)

        parsed_uri = urlparse(self.service_url)
        self._aws_host = '{uri.netloc}'.format(
            uri=parsed_uri)  # host used for iam requests
        self._aws_region = self._disc_api['awsRegion']  # aws region
        self._http_base = self._disc_api['httpBase']  # irbt unauth api
        self.mqtt_endpoint = self._disc_api['mqtt']  # the mqtt endpoint
        # the topic used to send commands
        # broken for now (fixme)
        self.mqtt_topic = self._disc_api['irbtTopics']

    # gigya login gather credentials used later in ibrbt login api
    def _gigya_login(self, username, password):
        gigya_login_data = {
            'ApiKey': self._api_key,
            'ctag': 'webbridge',
                    'format': 'json',
                    'loginID': username,
                    'password': password,
                    'sessionExpiration': '-2',
                    # if not set we gather cookies instead of gigya secrets
                    'targetEnv': 'mobile'
        }
        return json.loads(
            requests.post(
                # default login  url for gigya :
                # https://developers.gigya.com/display/GD/accounts.linkAccounts+REST
                'https://accounts.us1.gigya.com/accounts.login',
                data=gigya_login_data)
            .content.decode('utf-8'))

    # loggin in irbt login api to gather aws credentials
    def _irbt_login_api(self, signature, timestamp, uid):
        data = {
            'assume_robot_ownership': '0',
            'signature': signature,
            'timestamp': timestamp,
            'app_id' : self.app_id,
            'uid': uid
        }
        # retrieve the aws credentials
        unauth_api = json.loads(
            requests.post(
                self._http_base + '/v1/login/account',
                data=json.dumps(data))
            .content.decode('utf-8'))
        return (
            unauth_api['credentials']['AccessKeyId'],
            unauth_api['credentials']['SecretKey'],
            unauth_api['credentials']['SessionToken'])

    # login to the irbt cloud
    def login(self, username, password):
        """
        Retrieve the aws credentials used by the apis.

        The login is staged, p1 we login to gigya, p2 we use p1 credentials
        in irbt login api, that finally return aws credentials to
        use in all the subsequent calls (mqtt and api gateway)
        """
        # discover cloud settings
        self._disc()

        # login to gigya (get uid, timestamp and signature)
        gigya_login = self._gigya_login(username, password)

        # get aws keys through irbt login api
        try:
            (self.access_key_id,
             self.secret_key,
             self.session_token) = self._irbt_login_api(
                gigya_login['UIDSignature'],
                gigya_login['signatureTimestamp'],
                gigya_login['UID'])
        except KeyError:
            logger.error('Authentication failed, wrong login/password')
            return -1
        # use AWSRequestsAuth module to set the aws authentication headers
        # (Signature Version 4 Signing Process)
        self.auth = AWSRequestsAuth(
            aws_access_key=self.access_key_id,
            aws_secret_access_key=self.secret_key,
            aws_token=self.session_token,
            aws_host=self._aws_host,
            aws_region=self._aws_region,
            aws_service='execute-api')
        return True

    # Assoc
    def assoc(self, password, robot_id):
        """
        Associate provided robotid and password to the account.

        It only needs to be done once
        """
        data = {'password': password}
        return requests.post(
            self.service_url + 'user/associations/robots/%s?app_id=%s'
            % (robot_id, self.app_id),
            auth=self.auth, json=data).content

    # return a list of our robots
    def robots(self):
        """
        Return a list of robots provided by the api.

        The first json key is the robot id
        """
        return self.api.get('user', 'associations', 'robots')
