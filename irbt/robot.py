"""
Robot class.

It allows interactions with the robot cloud api
"""
import functools
import json
import os

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

from .logger import logging

logger = logging.getLogger(__name__)


def _output_status(payload, response_status, token):
    if not payload:
        return
    payload_dict = json.loads(payload)
    if not payload_dict:
        return

    prefix = payload_dict['state']['reported']
    infos = {
        'Battery': '%s%%' % prefix['batPct'],
        'Name': prefix['name'],
        'Bin Present': prefix['bin']['present'],
        'Bin full': prefix['bin']['full'],
        'Mission phase': prefix['cleanMissionStatus']['cycle'],
        'Initiator': prefix['cleanMissionStatus']['initiator'],
        'Last Command': prefix['lastCommand']['command'],
        # 'Last initiator': prefix['lastCommand']['initiator'],
        'Time Zone': prefix['timezone'],
        'Cloud env': prefix['cloudEnv'],
        'Cloud connected': prefix['connected'],
        'Country': prefix['country'],
        'Wlan mac address': prefix['hwPartsRev']['wlan0HwAddr']
    }
    logger.info(json.dumps(infos))


class Robot:
    """
    Class Robot.

    Used to interact with the robot, it needs a cloud instance
    """

    command = None

    class Commands:
        """
        The robot mqtt command class.

        Used for the mqtt commands
        """

        start: None
        stop: None
        pause: None
        dock: None
        status: None
        find: None
        resume: None

        def __init__(self, robot):
            """
            Declare the partial functools.

            Used to gate what command are sent through mqtt
            """
            self.start = functools.partial(robot._cmd, 'start')
            self.stop = functools.partial(robot._cmd, 'stop')
            self.pause = functools.partial(robot._cmd, 'pause')
            self.dock = functools.partial(robot._cmd, 'dock')
            self.status = functools.partial(robot._cmd, 'status')
            self.find = functools.partial(robot._cmd, 'find')
            self.resume = functools.partial(robot._cmd, 'resume')

    def __init__(self, cloud=None, rid=None, output_raw=None):
        """
        Initialize the robot instance.

        Check if a cloud is provided and
        set the current map id.
        """
        self.command = Robot.Commands(self)
        # alias for hass
        self.send_command = self._cmd

        # if no cloud connexion is passed,create one using provided credentials
        if not cloud:
            raise Exception('You need to provide a cloud connection')
        else:
            self._cloud = cloud

        # use provided id or first robot available
        if rid:
            self._id = rid
        else:
            self._id = list(self._cloud.robots())[0]

        self._current_map_id = None
        self._current_user_pmapv_id = None
        self.maps()
        self.device = None
        self.output_raw = output_raw
        self.name = None
        self.shadow_client = None

    def connect(self):
        """
        Instantiate mqtt clients and delete them when exiting.

        We use AWSIoTMQTTShadowClient to create our MQTT connection.
        This manager will close the connection on exit
        """
        self.shadow_client = AWSIoTMQTTShadowClient(
            self._cloud.app_id + str(os.urandom(6)),
            useWebsocket=True)
        self.shadow_client.configureEndpoint(self._cloud.mqtt_endpoint, 443)
        self.shadow_client.configureCredentials('config/aws-root-ca1.cer')
        self.shadow_client.configureIAMCredentials(
            self._cloud.access_key_id,
            self._cloud.secret_key,
            self._cloud.session_token)
        self.shadow_client.configureAutoReconnectBackoffTime(1, 128, 20)
        self.shadow_client.configureConnectDisconnectTimeout(10)
        self.shadow_client.configureMQTTOperationTimeout(5)
        # Set keepAlive interval to be 1 second and connect
        # Raise exception if there is an error in connecting to AWS IoT

        try:
            if not self.shadow_client.connect(5):
                raise Exception('AWSIoTMQTTShadowClientCouldNotConnect')
        except ValueError as e:
            logger.error("shadow_client.connect returned '%s'"
                         ', credentials are not authorized.', str(e))
            return -1
        self.device = self.shadow_client.createShadowHandlerWithName(self._id,
                                                                     True)
        self.connection = self.shadow_client.getMQTTConnection()
        logger.info('[+] mqtt connected')

    def disconnect(self):
        """Disconnect the mqtt stuff."""
        logger.info('[+] mqtt disconnected')
        self.connection.disconnect()

    # return maps and set active one
    def maps(self):
        """
        Return the map lists.

        Used to return a map lists and to set the active one in the instance
        only retrieve first map for now (fixme)
        """
        maps=[]
        params = {
            'visible': 'true',
            'activeDetails': '1'
        }
        maps = self._cloud.api.get(self._id, 'pmaps', params=params)
        if maps:
            path = ['active_pmapv_details', 'active_pmapv', 'pmap_id']
            self._current_map_id = maps[0][path[0]][path[1]][path[2]]
            self._current_user_pmapv_id = maps[0]['user_pmapv_id']
        return maps

    def rooms(self):
        """
        Return the room lists.

        Retrieve a correctly formated room list for humans
        """
        if self.maps():
            return (self.maps()[0]['active_pmapv_details']['regions'])
        else:
            return []

    def missions(self):
        """
        Return achieved mission list.

        return a json with the list of the finished missions and their statuses
        """
        params = {
            'filterType': 'omit_quickly_canceled_not_scheduled'
        }
        return self._cloud.api.get(self._id,
                                   'missionhistory',
                                   params=params)

    def evac_history(self):
        """
        Return logs of evacuations.

        return a json with logs of evacuations
        """
        params = {
            'robotId': self._id,
            'maxAge': 90
        }
        return self._cloud.api.get('evachistory', params=params)

    def timeline(self):
        """
        Return event timeline.

        return a json with the event timeline
        """
        params = {
            'event_type': 'HKC',
            'details_type_filter': 'all'
        }
        return self._cloud.api.get('robots',
                                   self._id,
                                   'timeline',
                                   params=params)

    def vector_map(self, map_id=None, user_pmapv_id=None):
        """
        Return a map as json.

        Return a json with coordinates of the map
        and history of the mission if any.
        """
        if not map_id:
            map_id = self._current_map_id
        if not user_pmapv_id:
            user_pmapv_id = self._current_user_pmapv_id
        return self._cloud.api.get(self._id,
                                   'pmaps',
                                   map_id,
                                   'versions',
                                   user_pmapv_id,
                                   'umf')

    def _make_payload(self, room_ids, cmd):
        payload = {
            'state': 'desired',
            'command': cmd,
            'initiator': 'rmtApp',
            'ordered': 0,
        }
        if cmd == 'start' and room_ids:
            logger.info('start cleaning of :')
            for room_id in room_ids.split(','):
                logger.info('  - %s (%s)', self.get_room_name(room_id),
                            room_id)
            regions = [{'region_id': room_id}
                       for room_id in room_ids.split(',')] \
                if ',' in room_ids else [{'region_id': room_ids}]
            payload.update({
                'pmap_id': self._current_map_id,
                'regions': regions,
                'user_pmapv_id': self._current_user_pmapv_id
            })
        return payload

    def _cmd(self, cmd, room_ids=None, print_output=_output_status):
        topic = '%s/things/%s/cmd' % (self._cloud.mqtt_topic, self._id)
        qos = 1

        payload = self._make_payload(room_ids, cmd)

        if cmd == 'status':
            try:
                self.device.shadowGet(print_output, 5)
            except Exception as e:
                logger.info('shadow get failed, exception: %s', e)
                logger.info('trying to refresh the connection (and the aws \
                             credentials)')
                self.disconnect()
                self.connect()
                self.device.shadowGet(print_output, 5)

            self.device.shadowRegisterDeltaCallback(print_output)
            return 0  # exit(0)
        logger.info(
            'executing command %s on robot %s, payload : %s',
            cmd, self._id, payload)

        if self.connection.publish(topic, json.dumps(payload), qos):
            try:
                self.device.shadowGet(print_output, 5)
            except Exception as e:
                logger.info('shadow get failed, exception: %s', e)
                logger.info('trying to refresh the connection (and the aws \
                             credentials)')
                self.disconnect()
                self.connect()
                self.device.shadowGet(print_output, 5)
            self.device.shadowRegisterDeltaCallback(print_output)
        else:
            raise Exception('MqttPublish%sError' % cmd)

    def current_state(self, state):
        """Return state as expected by the hass module."""
        # https://github.com/NickWaterton/Roomba980-Python/blob/master/roomba/roomba.py
        states = {'charge': 'Charging',
                  'new': 'New Mission',
                  'run': 'Running',
                  'resume': 'Running',
                  'hmMidMsn': 'Recharging',
                  'recharge': 'Recharging',
                  'stuck': 'Stuck',
                  'hmUsrDock': 'User Docking',
                  'dock': 'Docking',
                  'dockend': 'Docking - End Mission',
                  'cancelled': 'Cancelled',
                  'stop': 'Stopped',
                  'pause': 'Paused',
                  'hmPostMsn': 'End Mission',
                  '': None}
        return states[state]

    def set_preference(self, **kwargs):
        """Set preferences in robot (not implemented)."""
        logger.info('Set preference not implemented for %s', self._id)
        logger.info('-- Received keys --')
        if kwargs is not None:
            for key, value in kwargs.iteritems():
                logger.info('%s == %s' % (key, value))
        logger.info('-- End of Received keys --')

    def get_room_id(self, name):
        """Get room id from name."""
        for room in self.rooms():
            if name == room['name']:
                return room['id']

    def get_room_name(self, room_id):
        """Get room name from id."""
        for room in self.rooms():
            if room_id == room['id']:
                return room['name']
