"""
Parse command line args.

Helper for our cli
"""

import argparse

args_dict = [
    {
        'flag': '-m',
        'name': '--map',
        'action': 'store_true',
        'required': False,
        'dest': 'map',
        'help': 'output current map',
        'default': False
    },
    {
        'flag': '-c',
        'name': '--cmd',
        'action': 'store',
        'required': False,
        'nargs': '?',
        'const': 1,
        'dest': 'cmd',
        'help': 'cmd for the robot (start, stop, dock, pause, find)',
        'default': False
    },
    {
        'flag': '-d',
        'name': '--debug-mqtt',
        'action': 'store_true',
        'required': False,
        'dest': 'debug_mqtt',
        'help': 'debug-mqtt',
        'default': False
    },
    {
        'flag': '-M',
        'name': '--missions',
        'action': 'store_true',
        'required': False,
        'dest': 'missions',
        'help': 'Missions history',
        'default': False
    },
    {
        'flag': '-e',
        'name': '--evachistory',
        'action': 'store_true',
        'required': False,
        'dest': 'evac_history',
        'help': 'Evac history',
        'default': False
    },
    {
        'flag': '-t',
        'name': '--timeline',
        'action': 'store_true',
        'required': False,
        'dest': 'timeline',
        'help': 'Timeline',
        'default': False
    },
    {
        'flag': '-l',
        'name': '--list-rooms',
        'action': 'store_true',
        'required': False,
        'dest': 'list_rooms',
        'help': 'List rooms',
        'default': False
    },
    {
        'flag': '-r',
        'name': '--room-ids',
        'action': 'store',
        'required': False,
        'nargs': '?',
        'const': 1,
        'dest': 'room_ids',
        'help': 'Specify rooms id'
        'room ids to clean',
        'default': None
    },
    {
        'flag': '-p',
        'name': '--robot-password',
        'action': 'store_true',
        'required': False,
        'dest': 'show_password',
        'help': 'Show robot password',
        'default': None
    },
    {
        'flag': '-R',
        'name': '--robots',
        'action': 'store_true',
        'required': False,
        'dest': 'list_robots',
        'help': 'List robots',
        'default': None
    },
    {
        'flag': '-i',
        'name': '--robot-id',
        'action': 'store',
        'required': False,
        'nargs': '?',
        'const': 1,
        'dest': 'robot_id',
        'help': 'Specify robot id',
        'default': None
    },
    {
        'flag': '-I',
        'name': '--robot-infos',
        'action': 'store_true',
        'required': False,
        'dest': 'robot_infos',
        'help': 'Show robot infos',
        'default': None
    },
    {
        'flag': '-j',
        'name': '--output-json',
        'action': 'store_true',
        'required': False,
        'dest': 'output_json',
        'help': 'Output as Json if possible',
        'default': None
    },
    {
        'flag': '-o',
        'name': '--assoc',
        'action': 'store_true',
        'required': False,
        'dest': 'associate',
        'help': 'Associate provided robot id with account',
        'default': None
    },
    {
        'flag': '-w',
        'name': '--raw',
        'action': 'store_true',
        'required': False,
        'dest': 'output_raw',
        'help': 'Output Raw Json (from server api) if possible',
        'default': None
    },
    {
        'flag': '-P',
        'name': '--set-robot-password',
        'action': 'store',
        'required': False,
        'nargs': '?',
        'const': 1,
        'dest': 'robot_password',
        'help': 'Provide robot password for association',
        'default': None
    }
]


def get_argument_parser():
    """Parse command line args."""
    arguments_parser = argparse.ArgumentParser()

    def get_and_del(dct, name):
        value = dct[name]
        del dct[name]
        return value

    for cmd in args_dict:
        flag = get_and_del(cmd, 'flag')
        name = get_and_del(cmd, 'name')
        arguments_parser.add_argument(flag, name, **cmd)
    return arguments_parser
