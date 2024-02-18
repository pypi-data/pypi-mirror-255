from tb_wrapper.AssetController import *
import unittest
from unittest.mock import Mock, patch
import json


def get_env():
    env = dict()
    tb_url = 'http://217.76.51.6:9090'
    userfile = 'user.secrets'
    passwordfile = 'pass.secrets'
    env['tb_url'] = tb_url
    env['userfile'] = userfile
    env['passwordfile'] = passwordfile
    env['default_profile_info'] = {'default_dashboard_id': None,
                                   'id': {'entity_type': 'ASSET_PROFILE',
                                          'id': '94e524a0-f54f-11ed-91d5-ed8a7accb44b'},
                                   'image': None,
                                   'name': 'default',
                                   'tenant_id': {'entity_type': 'TENANT',
                                                 'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'}}
    env["saved_asset"] = {'additional_info': None,
                          'asset_profile_id': {'entity_type': 'ASSET_PROFILE',
                                               'id': '94e524a0-f54f-11ed-91d5-ed8a7accb44b'},
                          'created_time': 1701358904645,
                          'customer_id': {'entity_type': 'CUSTOMER',
                                          'id': '9567e930-f54f-11ed-91d5-ed8a7accb44b'},
                          'id': {'entity_type': 'ASSET', 'id': 'f6f91750-8f96-11ee-8034-97ab8762f59b'},
                          'label': None,
                          'name': 'Test',
                          'tenant_id': {'entity_type': 'TENANT',
                                        'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'},
                          'type': 'default'}
    env['asset'] = {'additional_info': None,
                    'asset_profile_id': {'entity_type': 'ASSET_PROFILE',
                                         'id': '94e524a0-f54f-11ed-91d5-ed8a7accb44b'},
                    'created_time': None,
                    'customer_id': {'entity_type': 'CUSTOMER',
                                    'id': '9567e930-f54f-11ed-91d5-ed8a7accb44b'},
                    'id': None,
                    'label': None,
                    'name': 'Test',
                    'tenant_id': None,
                    'type': None}

    env['asset_profile'] = {'created_time': None,
                            'default': None,
                            'default_dashboard_id': None,
                            'default_edge_rule_chain_id': None,
                            'default_queue_name': None,
                            'default_rule_chain_id': None,
                            'description': 'profile_name',
                            'id': None,
                            'image': None,
                            'name': 'profile_name',
                            'tenant_id': {'entity_type': 'TENANT',
                                          'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'}}

    env['saved_asset_profile'] = {'created_time': 1701689295340,
                                  'default': False,
                                  'default_dashboard_id': None,
                                  'default_edge_rule_chain_id': None,
                                  'default_queue_name': None,
                                  'default_rule_chain_id': None,
                                  'description': 'profile_name',
                                  'id': {'entity_type': 'ASSET_PROFILE',
                                         'id': '372c52c0-9298-11ee-878c-31ea2d675701'},
                                  'image': None,
                                  'name': 'profile_name',
                                  'tenant_id': {'entity_type': 'TENANT',
                                                'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'}}
    env['get_tenant_asset_response'] = {'additional_info': None,
                                        'asset_profile_id': {'entity_type': 'ASSET_PROFILE',
                                                             'id': '94e524a0-f54f-11ed-91d5-ed8a7accb44b'},
                                        'created_time': 1697547454337,
                                        'customer_id': {'entity_type': 'CUSTOMER',
                                                        'id': '13814000-1dd2-11b2-8080-808080808080'},
                                        'id': {'entity_type': 'ASSET', 'id': 'bd8e5f10-6cec-11ee-8bf0-899ee6c3e465'},
                                        'label': None,
                                        'name': 'FUNCTIONS',
                                        'tenant_id': {'entity_type': 'TENANT',
                                                      'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'},
                                        'type': 'default'}
    return env


class TestAssetController(unittest.TestCase):

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_get_default_profile_info(self, mockConn):

        conn = Mock()
        conn.login.return_value = conn
        mockConn.return_value = conn

        env = get_env()
        response_default_profile_info = env['default_profile_info']
        conn.get_default_asset_profile_info.return_value = response_default_profile_info
        asset_controller = AssetController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])

        result = asset_controller.get_default_asset_profile_info()
        assert result == response_default_profile_info

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_get_default_profile_info_exists_conn(self, mockConn):

        conn = Mock()
        conn.login.return_value = conn
        mockConn.return_value = conn

        env = get_env()
        response_default_profile_info = env['default_profile_info']
        conn.get_default_asset_profile_info.return_value = response_default_profile_info

        asset_controller = AssetController(connection=conn)
        result = asset_controller.get_default_asset_profile_info()
        assert result == response_default_profile_info

    @patch('tb_wrapper.AssetController.Asset', autospec=True)
    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_create_asset(self, mockClient, mockAsset):

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        asset_name = "Test"
        assetProfileID = {'entity_type': 'ASSET_PROFILE',
                                         'id': '94e524a0-f54f-11ed-91d5-ed8a7accb44b'}
        customerID = {'entity_type': 'CUSTOMER',
                      'id': '9567e930-f54f-11ed-91d5-ed8a7accb44b'}
        env = get_env()
        conn.save_asset.return_value = env['saved_asset']
        mockAsset.return_value = env['asset']
        ac = AssetController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])
        result = ac.create_asset(
            asset_profile_id=assetProfileID, asset_name=asset_name, customer_obj_id=customerID)

        conn.save_asset.assert_called_once_with(env['asset'])
        mockAsset.assert_called_once_with(
            name=asset_name, asset_profile_id=assetProfileID, customer_id=customerID)
        assert result == env['saved_asset']

    @patch('tb_wrapper.AssetController.Asset', autospec=True)
    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_create_asset_with_conn(self, mockClient, mockAsset):

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        asset_name = "Test"
        assetProfileID = {'entity_type': 'ASSET_PROFILE',
                                         'id': '94e524a0-f54f-11ed-91d5-ed8a7accb44b'}
        customerID = {'entity_type': 'CUSTOMER',
                      'id': '9567e930-f54f-11ed-91d5-ed8a7accb44b'}
        env = get_env()
        conn.save_asset.return_value = env['saved_asset']
        mockAsset.return_value = env['asset']
        ac = AssetController(connection=conn)
        result = ac.create_asset(
            asset_profile_id=assetProfileID, asset_name=asset_name, customer_obj_id=customerID)

        conn.save_asset.assert_called_once_with(env['asset'])
        mockAsset.assert_called_once_with(
            name=asset_name, asset_profile_id=assetProfileID, customer_id=customerID)
        assert result == env['saved_asset']

    @patch('tb_wrapper.AssetController.AssetProfile')
    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_create_asset_profile(self, mockClient, mockAssetProfile):

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn
        conn.get_user.tenant_id = "{'entity_type': 'TENANT','id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'}"
        env = get_env()
        asset_profile_name = "profile_name"
        tenant_id = {'entity_type': 'TENANT',
                     'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'}
        mockAssetProfile.return_value = env['asset_profile']
        conn.save_asset_profile.return_value = env['saved_asset_profile']

        ac = AssetController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])
        result = ac.create_asset_profile(asset_profile_name)

        assert result == env['saved_asset_profile']

    @patch('tb_wrapper.AssetController.AssetProfile')
    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_create_asset_profile(self, mockClient, mockAssetProfile):

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn
        conn.get_user.tenant_id = "{'entity_type': 'TENANT','id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'}"
        env = get_env()
        asset_profile_name = "profile_name"
        tenant_id = {'entity_type': 'TENANT',
                     'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'}
        mockAssetProfile.return_value = env['asset_profile']
        conn.save_asset_profile.return_value = env['saved_asset_profile']

        ac = AssetController(connection=conn)
        result = ac.create_asset_profile(asset_profile_name)

        assert result == env['saved_asset_profile']

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_exists_asset_by_name(self, mockClient):

        env = get_env()

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn
        mock_names = []
        for i in range(0, 5):
            m = Mock()
            m.name = str(i)
            mock_names.append(m)
        mockPageAsset = Mock()
        mockPageAsset.data = mock_names

        conn.get_tenant_asset_infos.return_value = mockPageAsset
        asset_name_true = "0"
        asset_name_false = "10"
        ac = AssetController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])
        result_false = ac.check_asset_exists_by_name(
            asset_name=asset_name_false)
        result_true = ac.check_asset_exists_by_name(asset_name=asset_name_true)
        assert result_true == True
        assert result_false == False

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_exists_asset_by_name_with_conn(self, mockClient):

        env = get_env()

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn
        mock_names = []
        for i in range(0, 5):
            m = Mock()
            m.name = str(i)
            mock_names.append(m)
        mockPageAsset = Mock()
        mockPageAsset.data = mock_names

        conn.get_tenant_asset_infos.return_value = mockPageAsset
        asset_name_true = "0"
        asset_name_false = "10"
        ac = AssetController(connection=conn)
        result_false = ac.check_asset_exists_by_name(
            asset_name=asset_name_false)
        result_true = ac.check_asset_exists_by_name(asset_name=asset_name_true)
        assert result_true == True
        assert result_false == False

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_exists_profile_asset_by_name(self, mockClient):

        env = get_env()

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn
        mock_names = []
        for i in range(0, 5):
            m = Mock()
            m.name = str(i)
            mock_names.append(m)
        mockPageAssetProfile = Mock()
        mockPageAssetProfile.data = mock_names

        conn.get_asset_profiles.return_value = mockPageAssetProfile
        asset_name_true = "0"
        asset_name_false = "10"
        ac = AssetController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])
        result_false = ac.check_asset_profile_exists_by_name(
            profile_name=asset_name_false)
        result_true = ac.check_asset_profile_exists_by_name(
            profile_name=asset_name_true)
        assert result_true == True
        assert result_false == False

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_exists_profile_asset_by_name_with_conn(self, mockClient):

        env = get_env()

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn
        mock_names = []
        for i in range(0, 5):
            m = Mock()
            m.name = str(i)
            mock_names.append(m)
        mockPageAssetProfile = Mock()
        mockPageAssetProfile.data = mock_names

        conn.get_asset_profiles.return_value = mockPageAssetProfile
        asset_name_true = "0"
        asset_name_false = "10"
        ac = AssetController(connection=conn)
        result_false = ac.check_asset_profile_exists_by_name(
            profile_name=asset_name_false)
        result_true = ac.check_asset_profile_exists_by_name(
            profile_name=asset_name_true)
        assert result_true == True
        assert result_false == False

    @patch('tb_wrapper.AssetController.AssetProfile', autospec=True)
    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_get_asset_profile_by_name(self, mockClient, mockAssetProfile):
        env = get_env()

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        mockTenant = Mock()
        mockTenant.tenant_id = {'entity_type': 'TENANT',
                                'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'}
        conn.get_user.return_value = mockTenant
        mockAssetProfile.return_value = env['asset_profile']

        conn.save_asset_profile.return_value = env['saved_asset_profile']
        profile_name = "profile_name"
        ac = AssetController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])
        result = ac.create_asset_profile(profile_name=profile_name)
        assert result == env['saved_asset_profile']

    @patch('tb_wrapper.AssetController.AssetProfile', autospec=True)
    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_get_asset_profile_by_name_with_conn(self, mockClient, mockAssetProfile):
        env = get_env()

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        mockTenant = Mock()
        mockTenant.tenant_id = {'entity_type': 'TENANT',
                                'id': '94cf0490-f54f-11ed-91d5-ed8a7accb44b'}
        conn.get_user.return_value = mockTenant
        mockAssetProfile.return_value = env['asset_profile']

        conn.save_asset_profile.return_value = env['saved_asset_profile']
        profile_name = "profile_name"
        ac = AssetController(connection=conn)
        result = ac.create_asset_profile(profile_name=profile_name)
        assert result == env['saved_asset_profile']

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_save_asset_attribute(self, mockClient):

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        env = get_env()
        asset_id = {'entity_type': 'ASSET',
                    'id': 'bd8e5f10-6cec-11ee-8bf0-899ee6c3e465'}
        scope = "SERVER_SCOPE"
        body = {'Test': 'test_save_asset_attribute'}

        conn.save_entity_attributes_v2.return_value = "Attribute updates"
        ac = AssetController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])
        result = ac.save_asset_attributes(
            asset_id=asset_id, scope=scope, body=body)

        conn.save_entity_attributes_v2.assert_called_once_with(
            asset_id, scope, body)
        assert result == "Attribute updates"

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_save_asset_attribute_with_conn(self, mockClient):

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        env = get_env()
        asset_id = {'entity_type': 'ASSET',
                    'id': 'bd8e5f10-6cec-11ee-8bf0-899ee6c3e465'}
        scope = "SERVER_SCOPE"
        body = {'Test': 'test_save_asset_attribute'}

        conn.save_entity_attributes_v2.return_value = "Attribute updates"
        ac = AssetController(connection=conn)
        result = ac.save_asset_attributes(
            asset_id=asset_id, scope=scope, body=body)

        conn.save_entity_attributes_v2.assert_called_once_with(
            asset_id, scope, body)
        assert result == "Attribute updates"

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_get_tenant_asset(self, mockClient):
        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        env = get_env()
        asset_name = "FUNCTIONS"
        conn.get_tenant_asset.return_value = env["get_tenant_asset_response"]
        ac = AssetController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])

        result = ac.get_tenant_asset(asset_name=asset_name)
        assert result == env["get_tenant_asset_response"]

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_get_tenant_asset(self, mockClient):
        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        env = get_env()
        asset_name = "FUNCTIONS"
        conn.get_tenant_asset.return_value = env["get_tenant_asset_response"]
        ac = AssetController(connection=conn)

        result = ac.get_tenant_asset(asset_name=asset_name)
        assert result == env["get_tenant_asset_response"]
