import copy
import time
from zonevu.zonevu.Zonevu import Zonevu
from zonevu.zonevu.Services.WellService import WellData
from zonevu.zonevu.Services import ZonevuError
from zonevu.zonevu.Services.Utils import Input


# Phase I - Get a well log to copy
def main():
    well_svc = zonevu.well_service
    log_svc = zonevu.welllog_service

    well_name = Input.get_name_from_args('well')
    well = well_svc.get_first_named(well_name, True)

    start_time = time.time()
    well_svc.load_well(well, {WellData.logs, WellData.curves})         # Load well logs into well
    end_time = time.time()
    print(f"Elapsed time to load logs and curves: {round(end_time - start_time, 3)} seconds")

    wellbore = well.primary_wellbore                # Get reference to wellbore
    #  survey = wellbore.surveys[0]                 # Get reference to first survey on wellbore
    log_original = next((item for item in wellbore.welllogs if item.name == 'GOTT_63N_1'), None)

    print("Well log = %s:" % log_original.name)
    print("   Num curves = %d:" % len(log_original.curves))
    for curve in log_original.curves:
        print('    %s' % curve.mnemonic)
    print()
    print("Successful execution")

    # curve_test = dict(map(lambda c: (c.id, c.samples), log_original.curves))

    # Test getting LAS file
    # las_file = log_svc.get_lasfile(log_original)
    # path = 'c:/delme/%s.las' % log_original.file_name
    # with open(path, 'w') as f:
    #     f.write(las_file)

    # Delete this.
    # service.delete_welllog(wellbore.welllogs[1])

    do_copy = True

    if do_copy:
        # Phase II - Delete Copy if it exists
        print("Copying well log %s" % log_original.name)
        log_copy_name = '%s_Copy' % log_original.name
        try:
            existing_copy = next((item for item in wellbore.welllogs if item.name == log_copy_name), None)
            if existing_copy is not None:
                print("Deleting existing copy of the well log %s ... " % log_copy_name, end="")
                delete_code = input("Enter delete 6-digit code:")  # Get code from console
                log_svc.delete_welllog(existing_copy, delete_code)
                print("Delete process was successful.")
        except ZonevuError as error:
            print("Could not delete well log '%s' because %s" % (log_copy_name, error.message))
            exit(2)

        # Phase III - Make a copy of the well data on the wellbore
        try:
            print("Saving well log to server... ", end="")
            log_copy = copy.deepcopy(log_original)
            log_copy.name = log_copy_name
            log_copy.file_name = '%s.las' % log_copy_name   # TODO: server controller method not saving filename!
            log_copy.external_id = 'my_external_id'
            log_copy.external_source = 'my_external_source'
            log_svc.add_welllog(wellbore, log_copy)
            print("Successfully saved copy of well log to server.")

            # Copy curve data samples.
            print("Saving curve samples... ", end="")
            start_time = time.time()
            for i in range(0, len(log_original.curves)):  # Loop over samples
                curve_orig = log_original.curves[i]
                curve_copy = log_copy.curves[i]
                log_svc.load_curve_samples(curve_orig)
                curve_copy.samples = curve_orig.samples
                log_svc.add_curve_samples(curve_copy)
            end_time = time.time()
            print("Successfully saved curve sample for %d curves in %s seconds." %
                  (len(log_original.curves), round(end_time - start_time, 3)))

            # Copy any the LAS file if any.
            print("Saving LAS file if any... ", end="")
            las_text = log_svc.get_lasfile(log_original)
            has_las = las_text is not None
            if has_las:
                log_svc.post_lasfile(log_copy, las_text)
                print("Successfully saved LAS file.")
            else:
                print("Log does not have an LAS file.")
        except ZonevuError as error:
            print("Could not copy well log because %s" % error.message)

        print("Copy of well log was successful")


try:
    zonevu = Zonevu.init_from_keyfile()          # Get zonevu client using a keyfile that has the API key.
    main()
except ZonevuError as run_err:
    print('Execution of program failed because %s.' % run_err.message)


