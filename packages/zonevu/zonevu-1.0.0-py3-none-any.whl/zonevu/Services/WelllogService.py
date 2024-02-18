import numpy as np
from zonevu.zonevu.DataModels import Welllog
from zonevu.zonevu.DataModels import Wellbore
from zonevu.zonevu.DataModels import Curve
from .Client import Client


class WelllogService:
    client: Client = None

    def __init__(self, c: Client):
        self.client = c

    def get_welllogs(self, wellboreId: int) -> list[Welllog]:
        url = "welllogs/%s" % wellboreId
        items = self.client.get(url)
        logs = [Welllog.from_dict(w) for w in items]
        return logs

    def load_welllogs(self, wellbore: Wellbore, load_curves: bool = False) -> list[Welllog]:
        logs = self.get_welllogs(wellbore.id)
        wellbore.welllogs = logs

        if load_curves:
            for log in logs:
                for curve in log.curves:
                    self.load_curve_samples(curve)

        return logs

    def get_welllog(self, welllog_id: int) -> Welllog:
        url = "welllog/%s" % welllog_id
        item = self.client.get(url)
        return Welllog.from_dict(item)

    def add_welllog(self, wellbore: Wellbore, log: Welllog) -> None:
        """
        Adds a well log to a wellbore. Updates the passed in survey with zonevu ids.
        @param wellbore: Zonevu wellbore to which survey will be added.
        @param log: Well log object
        @return: Throw a ZonevuError if method fails
        """
        url = "welllog/add/%s" % wellbore.id

        # Build a dictionary of curve samples. Null out curve samples, so they are not copied to server.
        curveDict = dict(map(lambda c: (c.name, c.samples), log.curves))
        for curve in log.curves:
            curve.samples = None

        item = self.client.post(url, log.to_dict())
        server_log = log.from_dict(item)

        # Put curve samples back on curves
        for curve in log.curves:
            curve.samples = curveDict[curve.name]

        log.copy_ids_from(server_log)   # Copy server ids of logs to client

    def delete_welllog(self, log: Welllog, delete_code: str) -> None:
        url = "welllog/delete/%s" % log.id
        self.client.delete(url, {"deletecode": delete_code})

    def get_lasfile(self, welllog: Welllog) -> (str, None):
        url = "welllog/lasfile/%s" % welllog.id
        raw_ascii_text = self.client.get_text(url, 'ascii')
        if raw_ascii_text is None:
            return None
        # Fix up text
        # ascii_text = raw_ascii_text.replace('\\r', '')
        # ascii_text = ascii_text.replace('\\n', '\n')
        # N = len(ascii_text)
        # ascii_text = ascii_text[1:N - 1]
        ascii_text = raw_ascii_text.replace('\r', '')   # Remove carriage returns.
        return ascii_text

    def post_lasfile(self, welllog: Welllog, las_text: str) -> None:
        url = "welllog/lasfile/%s" % welllog.id
        txt_bytes = las_text.encode('ascii')
        self.client.post_data(url, txt_bytes)

    def create_las_file_server(self, welllog: Welllog, overwrite: bool = False):
        # Cause an LAS file to be created and saved on server from database info
        url = "welllog/lasfile/instantiate/%s" % welllog.id
        self.client.post(url, {}, False, {"overwrite": overwrite})

    def load_curve_samples(self, curve: Curve):
        url = "welllog/curvedatabytes/%s" % curve.id
        curve_float_bytes = self.client.get_data(url)
        curve.samples = np.frombuffer(curve_float_bytes, dtype=np.float32)

    def add_curve_samples(self, curve: Curve) -> None:
        url = "welllog/curvedatabytes/%s" % curve.id
        curve_float_bytes = curve.samples.tobytes()
        self.client.post_data(url, curve_float_bytes, 'application/octet-stream')
