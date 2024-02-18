import copy
from zonevu.zonevu.Zonevu import Zonevu
from zonevu.zonevu.Services.WellService import WellData
from zonevu.zonevu.Services import ZonevuError


# Phase I - Get an interpretation to copy
def main():
    """
    This script will locate a well in ZoneVu, and make a copy of the first geosteering interpretation named 'Main'.
    """
    well_svc = zonevu.well_service
    interp_svc = zonevu.geosteering_service

    well_name = input("Enter well name: ")
    well = well_svc.get_first_named(well_name)
    if well is None:
        print("Exiting since no well named '%s' found." % well_name)
        exit(1)

    well_svc.load_well(well, {WellData.geosteering})  # Load geosteering interpretations into well
    wellbore = well.primary_wellbore                # Get reference to wellbore
    # Get reference to first geosteering interpretation on wellbore that doesn't end with 'copy'
    interp = next((item for item in wellbore.interpretations if not item.name.endswith('copy')), None)
    interp_svc.load_interpretation(interp)              # Load up the geosteering interpretation with all its data

    print("Geosteering interpretation = %s:" % interp.name)
    print("   Num picks = %d:" % len(interp.picks))
    print("   Num horizons = %d:" % len(interp.horizons))
    print("   Num curve defs = %d:" % len(interp.curve_defs))
    print()
    print("Successful execution")

    do_copy = True

    if do_copy:
        # Phase II - Delete Copy if it exists
        service = zonevu.geosteering_service
        interp_copy_name = "%s-copy" % interp.name
        try:
            existing_copy = next((item for item in wellbore.interpretations if item.name == interp_copy_name), None)
            if existing_copy is not None:
                service.delete_interpretation(existing_copy)
                print("Delete_interpretation process was successful")
        except ZonevuError as error:
            print("Could not delete interpretation '%s' because %s" % (interp_copy_name, error.message))

        # Phase III - Make a copy of the interpretation on the wellbore
        try:
            interp_copy = copy.deepcopy(interp)
            interp_copy.name = interp_copy_name
            service.add_interpretation(wellbore.id, interp_copy)
            print("Copy process was successful")
        except ZonevuError as error:
            print("Could not copy interpretation because %s" % error.message)


try:
    zonevu = Zonevu.init_from_keyfile()          # Get zonevu python client using a keyfile that has the API key.
    main()
except ZonevuError as run_err:
    print('Execution of program failed because %s.' % run_err.message)


