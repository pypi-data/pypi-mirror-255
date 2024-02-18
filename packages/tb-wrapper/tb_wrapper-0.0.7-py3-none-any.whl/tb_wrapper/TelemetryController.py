from tb_wrapper.handle_exception import *
from tb_wrapper.MainController import *


@handle_tb_wrapper_exception
class TelemetryController(MainController):

    def __init__(self, tb_url=None, userfile=None, passwordfile=None, connection=None):
        super().__init__(tb_url, userfile, passwordfile, connection)

    def get_timeseries(self,entity_id=None,keys=None,start_ts=None,end_ts=None):
        if entity_id is  None or keys is not None:
            raise ValueError(
                "Entity ID and Keys must be specified")
        if (start_ts is not None and end_ts is None) or (start_ts is None and end_ts is not None):
            raise ValueError("both (start_ts,end_ts) must be specified or neither")
        if start_ts is None and end_ts is None:
            pass #calcolo end_ts = datetime.now e start_ts = end - qualcosa

        timeseries_data = self.tb_client.get_timeseries(entity_id=entity_id, keys=keys, start_ts=start_ts, end_ts=end_ts)
        return timeseries_data
