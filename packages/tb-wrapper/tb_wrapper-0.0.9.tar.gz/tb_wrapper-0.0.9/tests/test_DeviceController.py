import pytest
import unittest

from unittest.mock import Mock, patch
from tb_wrapper.DeviceController import DeviceController


def get_env():
    env = dict()
    tb_url = 'http://217.76.51.6:9090'
    userfile = 'user.secrets'
    passwordfile = 'pass.secrets'
    env['tb_url'] = tb_url
    env['userfile'] = userfile
    env['passwordfile'] = passwordfile

    env['device_info_result_byname'] = {'data': [{'active': False,
                                                  'additional_info': None,
                                                  'created_time': 1697205661205,
                                                  'customer_id': {'entity_type': 'CUSTOMER',
                                                                  'id': '13814000-1dd2-11b2-8080-808080808080'},
                                                  'customer_is_public': False,
                                                  'customer_title': None,
                                                  'device_data': {'configuration': {'type': 'DEFAULT'},
                                                                  'transport_configuration': {'type': 'DEFAULT'}},
                                                  'device_profile_id': {'entity_type': 'DEVICE_PROFILE',
                                                                        'id': '94dbfce0-f54f-11ed-91d5-ed8a7accb44b'},
                                                  'device_profile_name': 'default',
                                                  'firmware_id': None,
                                                  'id': {'entity_type': 'DEVICE',
                                                         'id': 'f0f95450-69d0-11ee-8bf0-899ee6c3e465'},
                                                  'label': None,
                                                  'name': 'prometheus',
                                                  'software_id': None,
                                                  'tenant_id': {'entity_type': 'TENANT',
                                                                'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'},
                                                  'type': 'default'}],
                                        'has_next': False,
                                        'total_elements': 11,
                                        'total_pages': 1}
    env['device'] = {'additional_info': None,
                     'created_time': None,
                     'customer_id': {'entity_type': 'CUSTOMER',
                                     'id': '9567e930-f54f-11ed-91d5-ed8a7accb44b'},
                     'device_data': None,
                     'device_profile_id': {'entity_type': 'DEVICE_PROFILE',
                                           'id': '94dbfce0-f54f-11ed-91d5-ed8a7accb44b'},
                     'firmware_id': None,
                     'id': None,
                     'label': None,
                     'name': 'Test_Device01',
                     'software_id': None,
                     'tenant_id': None,
                     'type': None}
    env['saved_device'] = {'additional_info': None,
                           'created_time': 1701706697802,
                           'customer_id': {'entity_type': 'CUSTOMER',
                                           'id': '9567e930-f54f-11ed-91d5-ed8a7accb44b'},
                           'device_data': {'configuration': {'type': 'DEFAULT'},
                                           'transport_configuration': {'type': 'DEFAULT'}},
                           'device_profile_id': {'entity_type': 'DEVICE_PROFILE',
                                                 'id': '94dbfce0-f54f-11ed-91d5-ed8a7accb44b'},
                           'firmware_id': None,
                           'id': {'entity_type': 'DEVICE', 'id': 'bbd94aa0-92c0-11ee-878c-31ea2d675701'},
                           'label': None,
                           'name': 'Test_Device01',
                           'software_id': None,
                           'tenant_id': {'entity_type': 'TENANT',
                                         'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'},
                           'type': 'default'}
    env['device_nc'] = {'additional_info': None,
                        'created_time': None,
                        'customer_id': None,
                        'device_data': None,
                        'device_profile_id': {'entity_type': 'DEVICE_PROFILE',
                                              'id': '94dbfce0-f54f-11ed-91d5-ed8a7accb44b'},
                        'firmware_id': None,
                        'id': None,
                        'label': None,
                        'name': 'Test_Device01',
                        'software_id': None,
                        'tenant_id': None,
                        'type': None}
    env['saved_device_nc'] = {'additional_info': None,
                              'created_time': 1701706697802,
                              'customer_id': None,
                              'device_data': {'configuration': {'type': 'DEFAULT'},
                                              'transport_configuration': {'type': 'DEFAULT'}},
                              'device_profile_id': {'entity_type': 'DEVICE_PROFILE',
                                                    'id': '94dbfce0-f54f-11ed-91d5-ed8a7accb44b'},
                              'firmware_id': None,
                              'id': {'entity_type': 'DEVICE', 'id': 'bbd94aa0-92c0-11ee-878c-31ea2d675701'},
                              'label': None,
                              'name': 'Test_Device01',
                              'software_id': None,
                              'tenant_id': {'entity_type': 'TENANT',
                                            'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'},
                              'type': 'default'}

    env['default_profile_info'] = {'default_dashboard_id': None,
                                   'id': {'entity_type': 'DEVICE_PROFILE',
                                          'id': '94dbfce0-f54f-11ed-91d5-ed8a7accb44b'},
                                   'image': None,
                                   'name': 'default',
                                   'tenant_id': {'entity_type': 'TENANT',
                                                 'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'},
                                   'transport_type': 'DEFAULT',
                                   'type': 'DEFAULT'}
    return env


class TestDeviceController(unittest.TestCase):

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_get_tenant_device(self, mockClient):
        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        env = get_env()
        conn.get_tenant_device.return_value = env['device_info_result_byname']
        device_name = "prometheus"
        dc = DeviceController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])
        result = dc.get_tenant_device(device_name=device_name)

        conn.get_tenant_device.assert_called_once_with(device_name)
        assert result == env['device_info_result_byname']

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_get_tenant_device_with_conn(self, mockClient):
        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        env = get_env()
        conn.get_tenant_device.return_value = env['device_info_result_byname']
        device_name = "prometheus"
        dc = DeviceController(connection=conn)
        result = dc.get_tenant_device(device_name=device_name)

        conn.get_tenant_device.assert_called_once_with(device_name)
        assert result == env['device_info_result_byname']

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_check_device_exists_by_name(self, mockClient):

        env = get_env()

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn
        mock_names = []
        for i in range(0, 5):
            m = Mock()
            m.name = str(i)
            mock_names.append(m)
        mockPageDevice = Mock()
        mockPageDevice.data = mock_names

        conn.get_tenant_device_infos.return_value = mockPageDevice
        device_name_true = "0"
        device_name_false = "10"
        dc = DeviceController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])
        result_false = dc.check_device_exists_by_name(
            device_name=device_name_false)
        result_true = dc.check_device_exists_by_name(
            device_name=device_name_true)
        assert result_true == True
        assert result_false == False

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_check_device_exists_by_name_with_conn(self, mockClient):

        env = get_env()

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn
        mock_names = []
        for i in range(0, 5):
            m = Mock()
            m.name = str(i)
            mock_names.append(m)
        mockPageDevice = Mock()
        mockPageDevice.data = mock_names

        conn.get_tenant_device_infos.return_value = mockPageDevice
        device_name_true = "0"
        device_name_false = "10"
        dc = DeviceController(connection=conn)
        result_false = dc.check_device_exists_by_name(
            device_name=device_name_false)
        result_true = dc.check_device_exists_by_name(
            device_name=device_name_true)
        assert result_true == True
        assert result_false == False

    @patch('tb_wrapper.DeviceController.Device', autospec=True)
    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_create_device_with_customer(self, mockClient, mockDevice):
        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        c_obj_id = {'entity_type': 'CUSTOMER',
                    'id': '9567e930-f54f-11ed-91d5-ed8a7accb44b'}
        name = "Test_Device01"
        device_profile_id = {'entity_type': 'DEVICE_PROFILE',
                             'id': '94dbfce0-f54f-11ed-91d5-ed8a7accb44b'}

        env = get_env()
        mockDevice.return_value = env['device']
        conn.save_device.return_value = env['saved_device']

        dc = DeviceController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])
        result = dc.create_device_with_customer(
            device_profile_id=device_profile_id, device_name=name, customer_obj_id=c_obj_id)

        mockDevice.assert_called_once_with(device_profile_id=device_profile_id, name=name,
                                           customer_id=c_obj_id)
        assert result == env['saved_device']

    @patch('tb_wrapper.DeviceController.Device', autospec=True)
    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_create_device_with_customer_with_conn(self, mockClient, mockDevice):
        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        c_obj_id = {'entity_type': 'CUSTOMER',
                    'id': '9567e930-f54f-11ed-91d5-ed8a7accb44b'}
        name = "Test_Device01"
        device_profile_id = {'entity_type': 'DEVICE_PROFILE',
                             'id': '94dbfce0-f54f-11ed-91d5-ed8a7accb44b'}

        env = get_env()
        mockDevice.return_value = env['device']
        conn.save_device.return_value = env['saved_device']

        dc = DeviceController(connection=conn)
        result = dc.create_device_with_customer(
            device_profile_id=device_profile_id, device_name=name, customer_obj_id=c_obj_id)

        mockDevice.assert_called_once_with(device_profile_id=device_profile_id, name=name,
                                           customer_id=c_obj_id)
        assert result == env['saved_device']

    @patch('tb_wrapper.DeviceController.Device', autospec=True)
    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_create_device_without_customer(self, mockClient, mockDevice):
        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        name = "Test_Device01"
        device_profile_id = {'entity_type': 'DEVICE_PROFILE',
                             'id': '94dbfce0-f54f-11ed-91d5-ed8a7accb44b'}

        env = get_env()
        mockDevice.return_value = env['device_nc']
        conn.save_device.return_value = env['saved_device_nc']

        dc = DeviceController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])
        result = dc.create_device_without_customer(
            device_profile_id=device_profile_id, device_name=name)

        mockDevice.assert_called_once_with(
            device_profile_id=device_profile_id, name=name)
        assert result == env['saved_device_nc']

    @patch('tb_wrapper.DeviceController.Device', autospec=True)
    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_create_device_without_customer_with_conn(self, mockClient, mockDevice):
        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        name = "Test_Device01"
        device_profile_id = {'entity_type': 'DEVICE_PROFILE',
                             'id': '94dbfce0-f54f-11ed-91d5-ed8a7accb44b'}

        env = get_env()
        mockDevice.return_value = env['device_nc']
        conn.save_device.return_value = env['saved_device_nc']

        dc = DeviceController(connection=conn)
        result = dc.create_device_without_customer(
            device_profile_id=device_profile_id, device_name=name)

        mockDevice.assert_called_once_with(
            device_profile_id=device_profile_id, name=name)
        assert result == env['saved_device_nc']

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_save_device_attributes(self, mockClient):

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        env = get_env()
        device_id = {'entity_type': 'DEVICE',
                     'id': 'f0f95450-69d0-11ee-8bf0-899ee6c3e465'}
        scope = "SERVER_SCOPE"
        body = {'Test': 'test_save_device_attribute'}

        conn.save_device_attributes.return_value = "Attribute updates"
        dc = DeviceController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])
        result = dc.save_device_attributes(
            device_id=device_id, scope=scope, body=body)

        conn.save_device_attributes.assert_called_once_with(
            device_id, scope, body)
        assert result == "Attribute updates"

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_save_device_attributes_with_conn(self, mockClient):

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        env = get_env()
        device_id = {'entity_type': 'DEVICE',
                     'id': 'f0f95450-69d0-11ee-8bf0-899ee6c3e465'}
        scope = "SERVER_SCOPE"
        body = {'Test': 'test_save_device_attribute'}

        conn.save_device_attributes.return_value = "Attribute updates"
        dc = DeviceController(connection=conn)
        result = dc.save_device_attributes(
            device_id=device_id, scope=scope, body=body)

        conn.save_device_attributes.assert_called_once_with(
            device_id, scope, body)
        assert result == "Attribute updates"

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_get_default_device_profile_info(self, mockClient):
        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        env = get_env()
        conn.get_default_device_profile_info.return_value = env['default_profile_info']

        dc = DeviceController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])
        result = dc.get_default_device_profile_info()

        assert result == env['default_profile_info']

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_get_default_device_profile_info_with_conn(self, mockClient):
        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        env = get_env()
        conn.get_default_device_profile_info.return_value = env['default_profile_info']

        dc = DeviceController(connection=conn)
        result = dc.get_default_device_profile_info()

        assert result == env['default_profile_info']
