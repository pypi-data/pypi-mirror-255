from tb_wrapper.handle_exception import *
from tb_wrapper.MainController import *


@handle_tb_wrapper_exception
class TelemetryController(MainController):

    def __init__(self, tb_url=None, userfile=None, passwordfile=None, connection=None):
        super().__init__(tb_url, userfile, passwordfile, connection)

    # this method manages one entity id and a list of keys

    def get_timeseries(self, entities_keys=None, start_ts=None, end_ts=None):
        if entities_keys is None:
            raise ValueError(
                "Entity IDs and Keys must be specified")
        if (start_ts is not None and end_ts is None) or (start_ts is None and end_ts is not None):
            raise ValueError(
                "both (start_ts,end_ts) must be specified or neither")
        if start_ts is None and end_ts is None:
            pass  # calcolo end_ts = datetime.now e start_ts = end - qualcosa

        timeseries_data = {}
        for e in entities_keys.keys():
            result = self.tb_client.get_timeseries(
                entity_id=EntityId(entity_type="DEVICE", id=e), keys=entities_keys[e], start_ts=start_ts, end_ts=end_ts)
            for key, values in result.items():
                temp_data = {}
                combined_key = f"{e}_{key}"
                temp_data[combined_key] = values
                timeseries_data.update(temp_data)
        return timeseries_data
