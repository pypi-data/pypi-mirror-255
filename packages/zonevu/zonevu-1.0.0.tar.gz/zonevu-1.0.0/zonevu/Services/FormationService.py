from zonevu.zonevu.DataModels import StratColumn
from .Client import Client


# TODO: Create FormationController on SERVER
class FormationService:
    client: Client = None

    def __init__(self, c: Client):
        self.client = c

    # TODO: Implement on SERVER
    def get_stratcolumns(self) -> list[StratColumn]:
        url = "company/stratcolumns"
        items = self.client.get(url)
        cols = [StratColumn.from_dict(w) for w in items]
        return cols

    # TODO: Implement on SERVER
    def get_stratcolumn(self, column_id: int) -> StratColumn:
        url = "company/stratcolumn/%s" % column_id
        item = self.client.get(url)
        col = StratColumn.from_dict(item)
        return col

    # TODO: Implement on SERVER
    # def add_stratcolumn(self, col: StratColumn) -> None:
    #     raise ZonevuError('Not implemented')
    #     url = "stratcolumn/%s"
    #     item = self.client.post(url, col.to_dict())
    #     server_survey = StratColumn.from_dict(item)
    #     col.copy_ids_from(server_survey)
    #
    # # TODO: Implement on SERVER
    # def delete_stratcolumn(self, col: StratColumn) -> None:
    #     raise ZonevuError('Not implemented')
    #     url = "stratcolumn/delete/%s" % col.id
    #     self.client.delete(url)

    # TODO: Implement Add and Delete formation.




