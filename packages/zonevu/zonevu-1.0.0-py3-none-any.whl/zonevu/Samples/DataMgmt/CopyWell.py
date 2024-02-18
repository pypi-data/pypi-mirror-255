import copy
from zonevu.zonevu.Zonevu import Zonevu
from zonevu.zonevu.Services.WellService import WellData
from zonevu.zonevu.Services import ZonevuError
from zonevu.zonevu.Services.Utils import Input


def main():
    well_svc = zonevu.well_service

    well_name = Input.get_name_from_args('well')
    well = well_svc.get_first_named(well_name, True)
    well_svc.load_well(well, {WellData.surveys})  # Load well and its surveys
    print('Well %s%s (id=%d, UWI=%s)' % (well.name, well.number, well.id, well.uwi))
    print()

    # Setup for copy
    well_copy = copy.deepcopy(well)
    well_copy.name = '%s_Copy' % well.name
    well_copy.uwi = '%s 2' % well_copy.name

    # Delete well
    try:
        existing_copy = well_svc.get_first_named(well_copy.full_name)
        if existing_copy is not None:
            well_svc.load_well(existing_copy)  # Load well
            delete_code = input("Enter delete 6-digit code:")  # Get code from console
            well_svc.delete_well(existing_copy.id, delete_code)
    except ZonevuError as error:
        print("Execution failed because %s" % error.message)

    # Copy well

    well_svc.create_well(well_copy, {WellData.surveys})     # Copy well and its surveys
    print('Well copy %s%s (id=%d, UWI=%s)' % (well_copy.name, well_copy.number, well_copy.id, well_copy.uwi))
    print()


try:
    zonevu = Zonevu.init_from_keyfile()          # Get zonevu client using a keyfile that has the API key.
    main()
except ZonevuError as run_err:
    print('Execution of program failed because %s.' % run_err.message)
