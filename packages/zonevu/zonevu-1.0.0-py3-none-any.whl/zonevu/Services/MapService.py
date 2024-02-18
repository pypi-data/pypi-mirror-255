from .Client import Client
from zonevu.zonevu.DataModels import UserLayer


class MapService:
    client: Client = None

    def __init__(self, c: Client):
        self.client = c

    def get_user_layers(self, project_id: int) -> list[UserLayer]:
        """
        Gets a list of the user layers in a project
        @param project_id: id of project
        @return: a list of user layer objects with the geojson not populated
        """
        url = "userlayers/%s" % project_id
        items = self.client.get(url)
        layers = [UserLayer.from_dict(w) for w in items]
        return layers

    def find_layer(self, project_id: int, layer_id: int) -> UserLayer:
        """
        Retrieves a user layer with its geojson populated
        @param layer_id:
        @return: A user layer object
        """
        url = "userlayer/project/%s/layerid/%s" % (project_id, layer_id)
        item = self.client.get(url, {}, False)
        layer = UserLayer.from_dict(item)
        return layer

    def load_user_layer(self, layer: UserLayer) -> None:
        """
        Loads the geojson for the specified user layer
        @param layer: target layer to load
        """
        server_layer = self.find_layer(layer.project_id, layer.id)
        layer.geo_json = server_layer.geo_json

    def add_user_layer(self, project_id: int, layer: UserLayer) -> None:
        """
        Adds a user map layer to a project. Updates the passed in layer with zonevu ids.
        @param project_id: Zonevu id of project to which survey layer be added.
        @param layer: User map layer
        @return: Throw a ZonevuError if method fails
        """
        url = "userlayer/add/%s" % project_id
        item = self.client.post(url, layer.to_dict())
        server_layer = UserLayer.from_dict(item)
        layer.copy_ids_from(server_layer)

