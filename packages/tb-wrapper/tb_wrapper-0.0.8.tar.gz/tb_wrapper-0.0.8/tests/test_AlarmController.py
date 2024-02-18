import unittest
from unittest.mock import Mock, patch
from tb_wrapper.AlarmController import AlarmController
import pytest


def get_env():
    env = dict()
    tb_url = 'http://217.76.51.6:9090'
    userfile = 'user.secrets'
    passwordfile = 'pass.secrets'
    env['tb_url'] = tb_url
    env['userfile'] = userfile
    env['passwordfile'] = passwordfile
    env['build_alarm'] = {
        "tenantId": {
            "id": "94cf0490-f54f-11ed-91d5-ed8a7accb44b",
            "entityType": "TENANT"
        },
        "customerId": {
            "id": "13814000-1dd2-11b2-8080-808080808080",
            "entityType": "CUSTOMER"
        },
        "name": "alarm_name",
        "type": "alarm_type",
        "originator": {
            "id": "774f8440-8946-11ee-9593-fbf738de8bd6",
            "entityType": "ASSET"
        },
        "severity": "INDETERMINATE",
        "acknowledged": True,
        "cleared": False,
        "status": "ACTIVE_ACK"}
    env['save_alarm'] = {
        "id": {
            "id": "784f394c-42b6-435a-983c-b7beff2784f9",
            "entityType": "ALARM"
        },
        "createdTime": 1634058704567,
        "tenantId": {
            "id": "94cf0490-f54f-11ed-91d5-ed8a7accb44b",
            "entityType": "TENANT"
        },
        "customerId": {
            "id": "13814000-1dd2-11b2-8080-808080808080",
            "entityType": "CUSTOMER"
        },
        "name": "alarm_name",
        "type": "alarm_type",
        "originator": {
            "id": "774f8440-8946-11ee-9593-fbf738de8bd6",
            "entityType": "ASSET"
        },
        "severity": "INDETERMINATE",
        "acknowledged": True,
        "cleared": False,
        "startTs": 1634058704565,
        "endTs": 1634111163522,
        "ackTs": 1634115221948,
        "clearTs": 1634114528465,
        "assignTs": 1634115928465,
        "details": {},
        "propagate": True,
        "propagateToOwner": True,
        "propagateToTenant": True,
        "propagateRelationTypes": [
            "string"
        ],
        "status": "ACTIVE_ACK"
    }

    return env


class TestAlarmController(unittest.TestCase):

    @patch('tb_wrapper.AlarmController.Alarm', autospec=True)
    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_build_alarm(self, mockConn, mockAlarm):
        conn = Mock()
        conn.login.return_value = conn
        mockConn.return_value = conn

        env = get_env()
        response_build_alarm = env['build_alarm']

        mockAlarm.return_value = response_build_alarm

        tenant_obj = {'entity_type': 'TENANT',
                      'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'}
        customer_obj = {'entity_type': 'CUSTOMER',
                        'id': '13814000-1dd2-11b2-8080-808080808080'}
        entity_orginator = {'entity_type': 'ASSET',
                            'id': '774f8440-8946-11ee-9593-fbf738de8bd6'}
        alarm_name = "alarm_name"
        alarm_type = "alarm_type"
        severity_alarm = "INDETERMINATE"
        alarm_status = "ACTIVE_ACK"
        ack = True
        clear = False

        alarm_controller = AlarmController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])

        result = alarm_controller.build_alarm(tenant_obj, alarm_name, alarm_type, entity_orginator,
                                              customer_obj, severity_alarm, alarm_status, ack, clear)

        mockConn.assert_called_once()
        assert result == response_build_alarm
        assert alarm_controller.tb_client == conn
        mockConn.assert_called_once_with(env['tb_url'])
        mockAlarm.assert_called_once_with(tenant_id=tenant_obj,
                                          name=alarm_name,
                                          type=alarm_type,
                                          originator=entity_orginator,
                                          customer_id=customer_obj,
                                          severity=severity_alarm,
                                          status=alarm_status,
                                          acknowledged=ack,
                                          cleared=clear)

    @patch('tb_wrapper.AlarmController.Alarm', autospec=True)
    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_build_alarm_exists_conn(self, mockConn, mockAlarm):
        conn = Mock()
        conn.login.return_value = conn
        mockConn.return_value = conn

        env = get_env()
        response_build_alarm = env['build_alarm']
        mockAlarm.return_value = response_build_alarm

        tenant_obj = {'entity_type': 'TENANT',
                      'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'}
        customer_obj = {'entity_type': 'CUSTOMER',
                        'id': '13814000-1dd2-11b2-8080-808080808080'}
        entity_orginator = {'entity_type': 'ASSET',
                            'id': '774f8440-8946-11ee-9593-fbf738de8bd6'}
        alarm_name = "alarm_name"
        alarm_type = "alarm_type"
        severity_alarm = "INDETERMINATE"
        alarm_status = "ACTIVE_ACK"
        ack = True
        clear = False

        alarm_controller = AlarmController(connection=conn)
        result = alarm_controller.build_alarm(tenant_obj, alarm_name, alarm_type, entity_orginator,
                                              customer_obj, severity_alarm, alarm_status, ack, clear)

        assert result == response_build_alarm
        assert alarm_controller.tb_client == conn
        mockAlarm.assert_called_once_with(tenant_id=tenant_obj,
                                          name=alarm_name,
                                          type=alarm_type,
                                          originator=entity_orginator,
                                          customer_id=customer_obj,
                                          severity=severity_alarm,
                                          status=alarm_status,
                                          acknowledged=ack,
                                          cleared=clear)

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_save_alarm(self, mockConn):

        conn = Mock()
        conn.login.return_value = conn
        mockConn.return_value = conn

        env = get_env()
        alarm = env['build_alarm']
        response_save_alarm = env['save_alarm']

        conn.save_alarm.return_value = response_save_alarm
        alarm_controller = AlarmController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])
        result = alarm_controller.save_alarm(alarm=alarm)

        assert result == response_save_alarm
        assert result is not None
        conn.save_alarm.assert_called_once_with(alarm)

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_save_alarm_exits_conn(self, mockConn):

        conn = Mock()
        conn.login.return_value = conn
        mockConn.return_value = conn

        env = get_env()
        alarm = env['build_alarm']
        response_save_alarm = env['save_alarm']

        conn.save_alarm.return_value = response_save_alarm
        alarm_controller = AlarmController(connection=conn)
        result = alarm_controller.save_alarm(alarm=alarm)

        assert result == response_save_alarm
        assert result is not None
        conn.save_alarm.assert_called_once_with(alarm)
