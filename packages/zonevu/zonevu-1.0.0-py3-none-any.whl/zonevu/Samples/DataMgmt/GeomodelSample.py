import copy
import math
from zonevu.zonevu.Zonevu import Zonevu
from zonevu.zonevu.DataModels.Geospatial.Enums import DistanceUnitsEnum
from zonevu.zonevu.Services.CoordinatesService import Datum, UtmZone
from zonevu.zonevu.Services import ZonevuError


def main():
    # TODO revise / test
    service = zonevu.geomodel_service

    print('Geomodels:')

    models = service.get_geomodels('____')
    for entry in models:
        print('%s (%s)' % (entry.name, entry.id))

    geomodel = service.find_geomodel(models[0].id)
    codell = geomodel.data_grids[1]
    codell_copy = geomodel.data_grids[2]
    z_values = service.download_datagrid_z(codell)
    # z_values_copy = service.download_datagrid_z(codell_copy)

    codell_geom = codell.geometry
    copy_geom = codell_copy.geometry

    # Compute area
    grid = codell_geom.grid_info
    x_length = grid.inline_range.count * codell_geom.inline_bin_interval
    y_length = grid.crossline_range.count * codell_geom.crossline_bin_interval
    square_ft = x_length * y_length
    square_miles = square_ft / 5280 / 5280

    # Compute area 2
    c1 = codell_geom.corner1
    c3 = codell_geom.corner3
    dx = math.fabs(c3.p.X - c1.p.X)
    dy = math.fabs(c3.p.Y - c1.p.Y)
    square_ft2 = dx * dy
    square_miles2 = square_ft2 / 5280 / 5280

    coord_service = zonevu.coordinates_service
    crs_utm = coord_service.get_utm_crs(Datum.NAD27, 13, UtmZone.N, DistanceUnitsEnum.FeetUS)
    c1_xy = coord_service.get_coordinate(codell_geom.corner1.lat_long, crs_utm)

    copy_flag = False
    if copy_flag:
        print('Copying datagrid')
        datagrid_copy = copy.deepcopy(codell)
        datagrid_copy.name = codell.name + '-copy'
        datagrid_copy.id = -1
        service.add_datagrid(geomodel, datagrid_copy)
        datagrid_copy.z_values = codell.z_values.copy()
        service.upload_datagrid_z(datagrid_copy)


try:
    zonevu = Zonevu.init_from_keyfile()          # Get zonevu client using a keyfile that has the API key.
    zonevu.get_info().printNotice()         # Check that we can talk to ZoneVu server.
    main()
except ZonevuError as run_err:
    print('Execution of program failed because %s.' % run_err.message)

