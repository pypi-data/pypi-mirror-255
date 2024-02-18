from zonevu.zonevu.DataModels.Geomodels.Geomodel import Geomodel
from zonevu.zonevu.DataModels.Geomodels.DataGrid import DataGrid, GridUsageEnum
from zonevu.zonevu.DataModels.Geomodels.Structure import Structure
from zonevu.zonevu.DataModels.Geospatial.GridGeometry import GridInfo
from zonevu.zonevu.DataModels.Geomodels.SimpleGrid import SimpleGrid
from typing import Union
import numpy as np
from .Client import Client, ZonevuError
from ..Services.CoordinatesService import CoordinatesService


class GeomodelService:
    client: Client = None

    def __init__(self, c: Client):
        self.client = c

    def get_geomodels(self, match_token: str = None) -> list[Geomodel]:
        url = "geomodels"
        if match_token is not None:
            url += "/%s" % match_token
        items = self.client.get(url)
        entries = [Geomodel.from_dict(w) for w in items]
        return entries

    def find_geomodel(self, geomodel_id: int) -> Union[Geomodel | None]:
        url = "geomodel/%s" % geomodel_id
        item = self.client.get(url)
        project = Geomodel.from_dict(item)
        return project

    def download_datagrid_z(self, datagrid: DataGrid) -> np.ndarray:
        url = "geomodel/%s/zvalues/%s" % ('datagrid', datagrid.id)
        datagrid.z_values = self.__load_z_values(url, datagrid.geometry.grid_info)
        return datagrid.z_values

    def upload_datagrid_z(self, datagrid: DataGrid):
        url = "geomodel/datagrid/zvalues/%s" % datagrid.id
        float_values = datagrid.z_values.reshape(-1)
        float_bytes = float_values.tobytes()
        self.client.post_data(url, float_bytes, 'application/octet-stream')

    def download_structure_z(self, structure: Structure) -> np.ndarray:
        url = "geomodel/structure/zvalues/%s" % structure.id
        structure.z_values = self.__load_z_values(url, structure.geometry.grid_info)
        return structure.z_values

    def create_geomodel(self, geomodel: Geomodel) -> None:
        raise ZonevuError.local('Not implemented')

    def add_datagrid(self, geomodel: Geomodel, datagrid: DataGrid) -> None:
        url = "geomodel/datagrid/add/%s" % geomodel.id

        datagrid_dict = datagrid.to_dict()
        del datagrid_dict['ZValues']       # Delete ref to the zvalues. We upload those separately

        item = self.client.post(url, datagrid_dict, True, {"overwrite": False})    # Post to server

        server_datagrid = DataGrid.from_dict(item)          # Convert grid as returned from server to Datagrid object
        datagrid.copy_ids_from(server_datagrid)             # Copy server ids of grid created on server to local copy

    def add_simple_grid(self, geomodel: Geomodel, grid: SimpleGrid) -> DataGrid:
        """
        Converts a simple grid to a datagrid, geolocates it, creates it in ZoneVu & uploads the z-values
        @param geomodel:
        @param grid:
        @return: The datagrid that was created on server
        """
        coordinate_service = CoordinatesService(self.client)
        grid_geometry = coordinate_service.simple_to_grid_geometry(grid)
        datagrid = DataGrid()
        datagrid.geometry = grid_geometry
        datagrid.name = grid.name
        datagrid.usage = GridUsageEnum.Structural

        # Fix up z values
        negative_infinity = float('-inf')
        for n in range(len(grid.z_values)):  # Replace any None values with our -inf empty grid value
            if grid.z_values[n] is None:
                grid.z_values[n] = negative_infinity
        z_values = np.array(grid.z_values, dtype=np.float32)
        z_matrix = z_values.reshape(grid.num_rows, grid.num_cols)  # Make 2D array
        datagrid.z_values = z_matrix

        neg_inf = float('-inf')
        mask = z_values != neg_inf
        useful_values = z_values[mask]
        datagrid.average_value = np.average(useful_values).item()   # Make sure these are regular floats.
        datagrid.min_value = np.min(useful_values).item()
        datagrid.max_value = np.max(useful_values).item()

        self.add_datagrid(geomodel, datagrid)
        self.upload_datagrid_z(datagrid)

        return datagrid

    # Internal methods
    def __load_z_values(self, url: str, grid: GridInfo) -> np.ndarray:
        float_bytes = self.client.get_data(url)
        float_array = np.frombuffer(float_bytes, dtype=np.float32)
        z_values = float_array.reshape(grid.inline_range.count, grid.crossline_range.count)
        return z_values
