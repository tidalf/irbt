# Library for irbt cloud api

[![Maintainability](https://api.codeclimate.com/v1/badges/f0307333bdf7a58f11bb/maintainability)](https://codeclimate.com/github/tidalf/irbt/maintainability)
[![Actions Status](https://github.com/tidalf/pyirbt/workflows/Python%20application/badge.svg)](https://github.com/tidalf/irbt/actions)
[![Actions Status](https://github.com/tidalf/pyirbt/workflows/Docker%20Image%20CI/badge.svg)](https://github.com/tidalf/irbt/actions)
[![Known Vulnerabilities](https://snyk.io/test/github/tidalf/pyirbt/badge.svg)](https://snyk.io/test/github/tidalf/irbt)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/071f2083c0634aef9fc33ea00ffa1ddd)](https://www.codacy.com/manual/dkorp/irbt?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=tidalf/irbt&amp;utm_campaign=Badge_Grade)

This library implements some parts of the irbt cloud api (to control the different
robots of the company).

Supported devices:

It has only been tested with a roomba i7.

## Features

- login using gigya/irbt api
- associated robot list
- history
- maps api (as json)
- missions api
- mqtt start, pause, stop, dock
- cli

```shell
usage: cli.py [-h] [-m] [-M] [-e] [-t] [-d] [-c [CMD]] [-l] [-r [ROOM_IDS]]
              [-p] [-R] [-i [ROBOT_ID]] [-I] [-j] [-w]

optional arguments:
  -h, --help            show this help message and exit
  -m, --map             output current map
  -M, --missions        Missions history
  -e, --evachistory     Evac history
  -t, --timeline        Timeline
  -d, --debug-mqtt      debug-mqtt
  -c [CMD], --cmd [CMD]
                        cmd for the robot (start, stop, dock, pause)
  -l, --list-rooms      List rooms
  -r [ROOM_IDS], --room-ids [ROOM_IDS]
                        room ids to clean
  -p, --robot-password  Show robot password
  -R, --robots          List robots
  -i [ROBOT_ID], --robot-id [ROBOT_ID]
                        Specify robot id
  -I, --robot-infos     Show robot infos
  -j, --output-json     Output as Json if possible
  -w, --raw             Output Raw Json (from server api) if possible
```

## Install the dependencies

```shell
pip3 install -r requirements
```

## Run

set your irobot credentials in the following var :

```shell
export IRBT_LOGIN="your.email@provider.com"
export IRBT_PASSWORD="yourpassword"
```

Then launch the cli (-h for the options)

```shell
./cli.py -h
```

You can also build the container using:

```shell
docker build . -t irbt_cli
```

Then run it with the credentials environment variable sets

```shell
docker run -e IRBT_LOGIN -e IRBT_PASSWORD -ti irbt_cli:latest python3 ./cli.py -h
```

### for wireshark debugging

```shell
import sslkeylog
sslkeylog.set_keylog("sslkeylog.txt")
```
