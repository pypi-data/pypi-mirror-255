from tb_wrapper.handle_exception import *
from tb_wrapper.MainController import *


@handle_tb_wrapper_exception
class UserController(MainController):

    def __init__(self, tb_url=None, userfile=None, passwordfile=None, connection=None):
        super().__init__(tb_url, userfile, passwordfile, connection)

    def actual_user(self):
        return self.tb_client.get_user()

    def get_users_from_customer(self, customer_id):
        return self.tb_client.get_customer_users(customer_id=customer_id, page_size=1000, page=0)

    def get_tenant_id(self):
        return self.tb_client.get_user().tenant_id.id

    def get_tenant_entity_id(self):
        return self.tb_client.get_user().tenant_id
