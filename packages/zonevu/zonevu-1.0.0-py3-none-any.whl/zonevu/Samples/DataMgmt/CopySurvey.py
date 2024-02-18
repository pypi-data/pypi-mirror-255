import copy
from zonevu.zonevu.Zonevu import Zonevu
from zonevu.zonevu.Services.WellService import WellData
from zonevu.zonevu.Services import ZonevuError
from zonevu.zonevu.DataModels.Survey import DeviationSurveyUsageEnum


# Phase I - Get a survey to copy
def main():
    """
    This script will locate a well in ZoneVu, and make a copy of its actual deviation survey.
    """
    print('Making a copy of the actual deviation survey of a well in ZoneVu')
    well_svc = zonevu.well_service  # Get reference to ZoneVu WebAPI well service

    # Find the well for which I want to copy a deviation survey
    well_name = input("Enter well name: ")
    well = well_svc.get_first_named(well_name)
    if well is None:
        print("Exiting since no well named '%s' found." % well_name)
        exit(1)

    print('Well named "%s" was successfully found' % well_name)
    well_svc.load_well(well, {WellData.surveys})      # Load surveys into well
    wellbore = well.primary_wellbore                # Get reference to wellbore
    # Get reference to the actual deviation survey on wellbore
    survey_actual = next((item for item in wellbore.surveys if item.usage == DeviationSurveyUsageEnum.Actual), None)

    print("Survey ID = %s:" % survey_actual.id)
    print("   Num Stations = %d:" % len(survey_actual.stations))
    print("   Usage: %s" % survey_actual.usage)
    print()
    print("Successful execution.")

    do_copy = True

    if do_copy:
        # Phase II - Delete Copy if it exists
        survey_svc = zonevu.survey_service      # Get reference to ZoneVu WebAPI survey service
        survey_copy_name = "Actual-Copy"        # The copied survey will be called this
        print("The copied survey will be named '%s'." % survey_copy_name)
        try:
            # Here we check to see if a survey named "Actual-Copy" already exists, and maybe delete it.
            existing_copy = next((item for item in wellbore.surveys if item.name == survey_copy_name), None)
            if existing_copy is not None:
                print("There was an existing survey named '%s' so deleting it." % survey_copy_name)
                survey_svc.delete_survey(existing_copy)
                print("Delete process was successful")
        except ZonevuError as delete_err:
            print("Could not delete survey '%s' because %s" % (survey_copy_name, delete_err.message))

        # Phase III - Make a copy of the survey on the wellbore
        try:
            survey_copy = copy.deepcopy(survey_actual)      # Make a local copy of survey including stations.
            survey_copy.name = survey_copy_name             # Name the copy
            survey_copy.usage = DeviationSurveyUsageEnum.Plan   # Make the copy a plan. ZoneVu support multiple plans.
            survey_svc.add_survey(wellbore, survey_copy)    # Add survey to wellbore in ZoneVu
            print("Copy process was successful")
        except ZonevuError as copy_err:
            print("Could not copy survey because %s" % copy_err.message)

        print("Execution was successful")


try:
    zonevu = Zonevu.init_from_keyfile()          # Get zonevu python client using a keyfile that has the API key.
    main()
except ZonevuError as run_err:
    print('Execution of program failed because %s.' % run_err.message)



