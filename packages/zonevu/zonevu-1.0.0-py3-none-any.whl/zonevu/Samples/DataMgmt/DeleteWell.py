from zonevu.zonevu.Zonevu import Zonevu
from zonevu.zonevu.Services import ZonevuError


def main():
    # TODO revise / test
    well_svc = zonevu.well_service

    # Find a well by ID

    # well_name = '________'
    # name_exists, well_id = well_svc.get_well_exists_and_id(well_name, None, '')
    #
    # if name_exists:
    #     url = "well/delete/%s" % well_id
    #     zonevu._client.delete(url)


try:
    zonevu = Zonevu.init_from_keyfile()          # Get zonevu client using a keyfile that has the API key.
    zonevu.get_info().printNotice()         # Check that we can talk to ZoneVu server.
    main()
except ZonevuError as run_err:
    print('Execution of program failed because %s.' % run_err.message)