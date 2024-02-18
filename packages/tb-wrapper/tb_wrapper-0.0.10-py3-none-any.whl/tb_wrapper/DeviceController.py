from tb_wrapper.handle_exception import *
from tb_wrapper.MainController import *


@handle_tb_wrapper_exception
class DeviceController(MainController):

    def __init__(self, tb_url=None, userfile=None, passwordfile=None, connection=None):
        super().__init__(tb_url, userfile, passwordfile, connection)

    def get_tenant_device(self, device_name):
        return self.tb_client.get_tenant_device(device_name)

    def check_device_exists_by_name(self, device_name):
        info_device = self.tb_client.get_tenant_device_infos(
            page_size=10000, page=0)
        found = False
        for info in info_device.data:
            if info.name == device_name:
                found = True
        return found

    def create_device_with_customer(self, device_profile_id, device_name, customer_obj_id):
        device = Device(
            name=device_name, device_profile_id=device_profile_id, customer_id=customer_obj_id)
        device = self.tb_client.save_device(device)
        return device

    def create_device_without_customer(self, device_profile_id, device_name):
        device = Device(name=device_name, device_profile_id=device_profile_id)
        device = self.tb_client.save_device(device)
        return device

    # TODO: Aggiungere un altro metodo che assegni un device esistente a un customer

    def save_device_attributes(self, device_id, scope, body):
        return self.tb_client.save_device_attributes(device_id, scope, body)

    def get_default_device_profile_info(self):
        return self.tb_client.get_default_device_profile_info()

    def save_device_telemetry(self, token, body):
        return self.tb_client.post_telemetry(token, body)
