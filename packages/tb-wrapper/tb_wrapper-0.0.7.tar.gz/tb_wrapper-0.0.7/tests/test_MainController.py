import pytest
from unittest.mock import patch, Mock
from tb_wrapper.MainController import MainController
import unittest


def get_env():
    env = dict()
    tb_url = 'http://217.76.51.6:9090'
    userfile = 'user.secrets'
    passwordfile = 'pass.secrets'
    env['tb_url'] = tb_url
    env['userfile'] = userfile
    env['passwordfile'] = passwordfile
    return env


class TestMainController(unittest.TestCase):

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_destroyConnection(self, mockClient):
        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn
        conn.logout.return_value = None
        env = get_env()
        mc = MainController(
            tb_url=env['tb_url'], userfile=env['userfile'], passwordfile=env['passwordfile'])
        result = mc.destroyConnection()
        assert result == None

    @patch('tb_wrapper.MainController.RestClientCE', autospec=True)
    def test_destroyConnection_with_conn(self, mockClient):
        conn = Mock()
        conn.login.return_value = conn
        mockClient.return_value = conn
        conn.logout.return_value = None
        env = get_env()
        mc = MainController(connection=conn)
        result = mc.destroyConnection()
        assert result == None
