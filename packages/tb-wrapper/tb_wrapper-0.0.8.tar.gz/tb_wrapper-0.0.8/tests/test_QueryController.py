import pytest
from unittest.mock import Mock, patch
from tb_wrapper.QueryController import QueryController
import unittest


def get_env():
    env = dict()
    tb_url = 'http://217.76.51.6:9090'
    userfile = 'user.secrets'
    passwordfile = 'pass.secrets'
    env['tb_url'] = tb_url
    env['userfile'] = userfile
    env['passwordfile'] = passwordfile
    env['body'] = {'entity_fields': [{'key': 'name', 'type': 'ENTITY_FIELD'}],
                   'entity_filter': {'entity_type': 'CUSTOMER',
                                     'resolve_multiple': True,
                                     'type': 'entityType'},
                   'key_filters': [{'key': {'key': 'test', 'type': 'SERVER_ATTRIBUTE'},
                                    'predicate': {'operation': 'EQUAL',
                                                  'type': 'STRING',
                                                  'value': {'defaultValue': 'test'}},
                                    'value_type': 'STRING'}],
                   'latest_values': [{'key': 'test', 'type': 'SERVER_ATTRIBUTE'}],
                   'page_link': {'dynamic': True,
                                 'page': 0,
                                 'page_size': 1000,
                                 'sort_order': None,
                                 'text_search': None}}
    env['result_body'] = {'data': [{'agg_latest': {},
                                    'entity_id': {'entity_type': 'CUSTOMER',
                                                  'id': '9567e930-f54f-11ed-91d5-ed8a7accb44b'},
                                    'latest': {'ENTITY_FIELD': {'name': {'ts': 1701788673431,
                                                                         'value': 'Customer C'}},
                                               'SERVER_ATTRIBUTE': {'test': {'ts': 1701788551372,
                                                                             'value': 'test'}}},
                                    'timeseries': {}}],
                          'has_next': False,
                          'total_elements': 1,
                          'total_pages': 1}
    return env


class TestQueryController(unittest.TestCase):

    @patch("tb_wrapper.QueryController.QueryController.query_body_attribute", autospec=True)
    @patch("tb_wrapper.MainController.RestClientCE", autospec=True)
    def test_find_customers_by_attribute(self, mockClient, mockBody):

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        env = get_env()
        filter_key_scope = "SERVER_ATTRIBUTE"
        filter_key_name = "test"
        filter_key_value = "test"
        filter_key_type = "STRING"
        mockBody.return_value = env['body']

        conn.find_entity_data_by_query.return_value = env['result_body']

        qc = QueryController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])

        result = qc.find_customers_by_attribute(filter_key_scope=filter_key_scope, filter_key_name=filter_key_name,
                                                filter_key_value=filter_key_value, filter_key_type=filter_key_type)
        assert result == env['result_body']

    @patch("tb_wrapper.QueryController.QueryController.query_body_attribute", autospec=True)
    @patch("tb_wrapper.MainController.RestClientCE", autospec=True)
    def test_find_customers_by_attribute_with_conn(self, mockClient, mockBody):

        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn

        env = get_env()
        filter_key_scope = "SERVER_ATTRIBUTE"
        filter_key_name = "test"
        filter_key_value = "test"
        filter_key_type = "STRING"
        mockBody.return_value = env['body']

        conn.find_entity_data_by_query.return_value = env['result_body']

        qc = QueryController(connection=conn)

        result = qc.find_customers_by_attribute(filter_key_scope=filter_key_scope, filter_key_name=filter_key_name,
                                                filter_key_value=filter_key_value, filter_key_type=filter_key_type)
        assert result == env['result_body']
