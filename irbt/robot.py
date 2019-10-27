"""
Robot class.

It allows interactions with the robot cloud api
"""
import functools
import json

from .cloud import mqtt_manager
from .logger import logging

logger = logging.getLogger(__name__)


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

    def __init__(self, cloud=None, rid=None, output_raw=None):
        """
        Initialize the robot instance.

        Check if a cloud is provided and
        set the current map id.
        """
        self.command = Robot.Commands(self)
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

    # return maps and set active one
    def maps(self):
        """
        Return the map lists.

        Used to return a map lists and to set the active one in the instance
        only retrieve first map for now (fixme)
        """
        params = {
            'visible': 'true',
            'activeDetails': '1'
        }
        maps = self._cloud.api.get(self._id, 'pmaps', params=params)
        path = ['active_pmapv_details', 'active_pmapv', 'pmap_id']
        self._current_map_id = maps[0][path[0]][path[1]][path[2]]
        self._current_user_pmapv_id = maps[0]['user_pmapv_id']
        return maps

    def rooms(self):
        """
        Return the room lists.

        Retrieve a correctly formated room list for humans
        """
        return (self.maps()[0]['active_pmapv_details']['regions'])

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

    def _output_status(self, payload, response_status, token):
        if not payload:
            return
        payload_dict = json.loads(payload)
        if not payload_dict:
            return
        if self.output_raw:
            print(json.dumps(payload_dict))
        else:
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

    def _make_payload(self, room_ids, cmd):
        payload = {
            'state': 'desired',
            'command': cmd,
            'initiator': 'rmtApp',
            'ordered': 0,
        }
        if cmd == 'start' and room_ids:
            logger.info('starting cleaning of %s', room_ids)
            regions = [{'region_id': room_id}
                       for room_id in room_ids.split(',')] \
                if ',' in room_ids else [{'region_id': room_ids}]
            payload.update({
                'pmap_id': self._current_map_id,
                'regions': regions,
                'user_pmapv_id': self._current_user_pmapv_id
            })
        return payload

    def _cmd(self, cmd, room_ids=None):
        topic = '%s/things/%s/cmd' % (self._cloud.mqtt_topic, self._id)
        qos = 1
        payload = self._make_payload(room_ids, cmd)
        with mqtt_manager(self._cloud, self) as mqtt:
            if cmd == 'status':
                mqtt.device.shadowGet(self._output_status, 5)
                mqtt.device.shadowRegisterDeltaCallback(self._output_status)
                exit(0)
            logger.info(
                'executing command %s on robot %s', cmd, self._id)
            if mqtt.connection.publish(topic, json.dumps(payload), qos):
                mqtt.device.shadowGet(self._output_status, 5)
                mqtt.device.shadowRegisterDeltaCallback(self._output_status)
            else:
                raise Exception('MqttPublish%sError' % cmd)
