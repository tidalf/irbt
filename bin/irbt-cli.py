#!/usr/bin/env python3
"""
CLI for roomba.

Set IRBT_LOGIN and IRBT_PASSWORD environment variables
"""

import json
import os
import sys

from irbt import (Cloud, Robot, enable_mqtt_logging, get_argument_parser,
                  logging)


def print_output(payload, response_status, token):
    """
    Print callback for the mqtt stuff.

    Used if none is provided
    """
    if not payload:
        return
    payload_dict = json.loads(payload)
    if not payload_dict:
        return
    print(json.dumps(payload_dict['state']['reported']))


logger = logging.getLogger('irbt-cli')

parser = get_argument_parser()
if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    exit(1)
args = parser.parse_args()

# enable mqtt debug
if args.debug_mqtt:
    enable_mqtt_logging()

# instance Robot
username = os.environ.get('IRBT_LOGIN')
password = os.environ.get('IRBT_PASSWORD')

if not username or not password:
    logger.error('IRBT_LOGIN or IRBT_PASSWORD are not set')
    exit(1)

# cloud connexion
cloud = Cloud(username=username, password=password)

# associate robot
if args.associate:
    if not args.robot_id or not args.robot_password:
        logger.error('No robot ID \
                      or password provided for the association')
        exit(1)
    else:
        cloud.assoc(args.robot_password, args.robot_id)

try:
    robot_id = args.robot_id if args.robot_id else list(cloud.robots())[0]
except IndexError:
    logger.error('[-] No robot found in the account')
    exit(0)

# show robot list
if args.list_robots:
    for index, robot in enumerate(cloud.robots()):
        print('robot {} : {}'.format(index, robot))
    sys.exit(0)
# show password of selected robot
elif args.show_password:
    print('Robot password: {}'.format(cloud.robots()[robot_id]['password']))
    sys.exit(0)
# show robot general infos
elif args.robot_infos:
    infos = cloud.robots()[robot_id]
    if args.output_json:
        print('%s' % json.dumps(infos))
    else:
        print("""Informations on {robot_id}
    Name: {name}
    Model: {sku}
    Password: {password}
    Software Version: {software_ver}""".format(
            robot_id=robot_id,
            name=infos['name'],
            sku=infos['sku'],
            password=infos['password'],
            software_ver=infos['softwareVer']))
        sys.exit(0)

# instance robot !
robot = Robot(rid=args.robot_id, cloud=cloud, output_raw=args.output_raw)

# list rooms
if args.list_rooms:
    for room in robot.rooms():
        print('{}: {}'.format(room['name'], room['id']))

# contains all the map (parse me)
elif args.missions:
    print(json.dumps(robot.missions()))
# evacutation history
elif args.evac_history:
    print(json.dumps(robot.evac_history()))
# timeline
elif args.timeline:
    print(json.dumps(robot.timeline()))
# get active map
elif args.map:
    print(json.dumps(robot.vector_map()))
# commands
elif args.cmd:
    robot.connect()
    getattr(robot.command, args.cmd)(room_ids=args.room_ids,
                                     print_output=print_output)
    robot.disconnect()
sys.exit(0)
