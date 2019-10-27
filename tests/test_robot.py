"""
Test robot class.

Early stage
"""

from irbt import Robot


def test_robot_rooms(cloud):
    """
    Test robot rooms.

    Test robot rooms
    """
    robot = Robot(cloud)
    assert(robot is not None)
    assert(robot.rooms() == [
        {'id': '1', 'name': 'Living Room', 'region_type': 'living_room'},
        {'id': '2', 'name': 'Kitchen', 'region_type': 'kitchen'},
        {'id': '3', 'name': 'Foyer 1', 'region_type': 'foyer'},
        {'id': '4', 'name': 'BedRoom 1', 'region_type': 'bedroom'},
        {'id': '5', 'name': 'BedRoom 2', 'region_type': 'bedroom'},
        {'id': '6', 'name': 'BathRoom', 'region_type': 'bathroom'},
        {'id': '7', 'name': 'Custom', 'region_type': 'custom'}
    ])


def test_robot_maps(robot):
    """
    Test robot maps.

    Test robot maps
    """
    assert(robot.maps() == [{
        'active_pmapv_details': {
            'active_pmapv': {
                'child_seg_xfer_seq_err': 0,
                'create_time': 1570282549,
                'creator': 'user',
                'last_user_pmapv_id': '134043T209849',
                'last_user_ts': 1570282549,
                'pmap_id': 'en12a9_lTglkpPqazxDWED',
                'pmapv_id': '134043T209849',
                'proc_state': 'OK_Processed'
            },
            'map_header': {
                'create_time': 1570282549,
                'id': 'en12a9_lTglkpPqazxDWED',
                'learning_percentage': 100,
                'name': 'Appartement',
                'resolution': 0.10500000417232513,
                'user_orientation_rad': 0.0,
                'version': '134043T209849'
            },
            'regions': [
                {
                    'id': '1',
                    'name': 'Living Room',
                    'region_type': 'living_room'
                },
                {
                    'id': '2',
                    'name': 'Kitchen',
                    'region_type': 'kitchen'
                },
                {
                    'id': '3',
                    'name': 'Foyer 1',
                    'region_type': 'foyer'
                },
                {
                    'id': '4',
                    'name': 'BedRoom 1',
                    'region_type': 'bedroom'
                },
                {
                    'id': '5',
                    'name': 'BedRoom 2',
                    'region_type': 'bedroom'
                },
                {
                    'id': '6',
                    'name': 'BathRoom',
                    'region_type': 'bathroom'
                },
                {
                    'id': '7',
                    'name': 'Custom',
                    'region_type': 'custom'
                }
            ]
        },
        'active_pmapv_id': '134043T209849',
        'create_time': 1570276098,
        'last_pmapv_ts': 1571613652,
        'merged_pmap_ids': [],
        'pmap_id': 'en12a9_lTglkpPqazxDWED',
        'robot_pmapv_id': '191020T232046',
        'state': 'active',
        'user_pmapv_id': '134043T209849',
        'visible': True
    }])


def test_robot_missions(robot):
    """
    Test robot missions.

    Test robot missions
    """
    assert(robot.missions() == [{
        'chrgM': 0,
        'chrgs': 0,
        'cmd': {
            'command': 'dock',
            'initiator': 'rmtApp',
            'ordered': 0,
            'state': 'desired'
        },
        'dirt': 0,
        'dockedAtStart': True,
        'done': 'stuck',
        'doneM': 0,
        'done_raw': 'stuck',
        'durationM': 0,
        'eDock': 0,
        'evacs': 0,
        'flags': 0,
        'initiator': 'ifttt',
        'nMssn': 183,
        'pauseId': 0,
        'pauseM': 0,
        'pmaps': [{'en12a9_lTglkpPqazxDWED': '191020T232046'}],
        'pmaps_robot': [{'en12a9_lTglkpPqazxDWED': '191020T232046'}],
        'robot_id': '1234ABCD1234ABCD1234ABCD1234ABCD',
        'runM': 0,
        'saves': 0,
        'softwareVer': 'lewis+3.0.11+lewis-release-rt319+14',
        'sqft': 0,
        'startEndWlBars': [4, 4],
        'startTime': 1571613647,
        'timestamp': 1571613647,
        'wifiChannel': 4,
        'wlBars': [100, 0, 0, 0, 0]
    }, {
        'chrgM': 0,
        'chrgs': 0,
        'cmd': {
            'command': 'dock',
            'initiator': 'rmtApp',
            'ordered': 0,
            'state': 'desired'
        },
        'dirt': 0,
        'dockedAtStart': True,
        'done': 'ok',
        'doneM': 0,
        'done_raw': 'ok',
        'durationM': 3,
        'eDock': 1,
        'evacs': 0,
        'flags': 0,
        'initiator': 'rmtApp',
        'nMssn': 181,
        'pauseId': 0,
        'pauseM': 0,
        'pmaps': [{'en12a9_lTglkpPqazxDWED': '191020T095313'}],
        'pmaps_robot': [{'en12a9_lTglkpPqazxDWED': '191020T095313'}],
        'robot_id': '1234ABCD1234ABCD1234ABCD1234ABCD',
        'runM': 3,
        'saves': 0,
        'softwareVer': 'lewis+3.0.11+lewis-release-rt319+14',
        'sqft': 14,
        'startEndWlBars': [4, 4],
        'startTime': 1571565013,
        'timestamp': 1571565194,
        'wifiChannel': 4,
        'wlBars': [28, 51, 21, 0, 0]
    }])


def test_robot_evac_history(robot):
    """
    Test robot evac_history.

    Test robot evac_history
    """
    assert(robot.evac_history() == {
        'EvacReports': [],
        'LifetimeData': []
    })


def test_robot_timeline(robot):
    """
    Test robot timeline.

    Test robot timeline
    """
    assert(robot.timeline() == {
        'events': [
            {
                'hkc_sns_recv_ts': 1570983779,
                'event_type': 'HKC',
                'event_id': 'f0b41b2c1d254a75b456529c7f188004',
                'event_object_id': '52e8dfca54324d83bd92be37d1523385',
                'start_time': 1570902045,
                'expires': 1573575783,
                'hkc_created_ts': 1570983781,
                'end_time': 1602438045,
                'robot_id': '1234ABCD1234ABCD1234ABCD1234ABCD',
                'event_state': 0,
                'event_details': {
                    'details_content': {
                        'headline_text_id':
                        'notification_center_nps_title_dmc',
                        'category_title_id': 'feedback_dmc',
                        'responses': [{
                            'survey_id':
                            '19ac6322-447f-42dc-89fc-b84b58b1be83',
                            'response_type': 'Survey'
                        }],
                        'action_payload': [{
                            'numberOfSchedulesToDisplay': None,
                            'video_url': None,
                            'content_text_id':
                            'notification_center_nps_desc_dmc',
                            'internal_image_url': None,
                            'display_order': 0,
                            'video_id': None,
                            'content_html_id': None,
                            'html': None, 'content_html': None,
                            'image_id': None,
                            'internal_video_url': None,
                            'image_url': None,
                            'content_id': None,
                            'image': None,
                            'content_text': 'On a scale of 0 to 10 how likely '
                                            'would you be to recommend your '
                                            'iRobot product to a friend?'
                        }],
                        'category_title_text': 'Feedback',
                        'display_type': 'separate_view',
                        'action_type': 'content',
                        'category_icon_id':
                        'notification_center_icon_feedback',
                        'headline_text': 'Got a minute to give us some '
                        'feedback on your iRobot product?'
                    },
                    'details_content_id': 15,
                    'details_content_version': 1,
                    'details_type': 'NpsSurvey'
                }
            },
            {
                'hkc_sns_recv_ts': 1570983879,
                'event_type': 'HKC',
                'event_id': '6973ba11c979476cac8266fba43af2b9',
                'event_object_id': 'f25b3fecb4354a6cba82cab122e4b2d2',
                'start_time': 1570902080,
                'expires': 1573575879,
                'hkc_created_ts': 1570983879,
                'end_time': 1602438080,
                'robot_id': '1234ABCD1234ABCD1234ABCD1234ABCD',
                'event_state': 0,
                'event_details': {
                    'details_content': {
                        'headline_text_id':
                        'notification_center_nps_title_dmc',
                        'category_title_id': 'feedback_dmc',
                        'responses': [{
                            'survey_id':
                            '97de6426-2c5f-448d-8a6a-2f99de674be7',
                            'response_type': 'Survey'
                        }],
                        'action_payload': [{
                            'numberOfSchedulesToDisplay': None,
                            'video_url': None,
                            'content_text_id':
                            'notification_center_nps_desc_dmc',
                            'internal_image_url': None,
                            'display_order': 0,
                            'video_id': None,
                            'content_html_id': None,
                            'html': None,
                            'content_html': None,
                            'image_id': None,
                            'internal_video_url': None,
                            'image_url': None,
                            'content_id': None,
                            'image': None,
                            'content_text': 'On a scale of 0 to 10 how likely '
                            'would you be to recommend your iRobot '
                            'product to a friend?'
                        }],
                        'category_title_text': 'Feedback',
                        'display_type': 'separate_view',
                        'action_type': 'content',
                        'category_icon_id':
                        'notification_center_icon_feedback',
                        'headline_text':
                        'Got a minute to give us some '
                        'feedback on your iRobot product?'
                    },
                    'details_content_id': 15,
                    'details_content_version': 1,
                    'details_type': 'NpsSurvey'
                }
            }
        ]
    })


def test_robot_vector_map(robot):
    """
    Test robot vector_map.

    Test robot vector_map
    """
    assert(robot.vector_map() == {})
