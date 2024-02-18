from zonevu.zonevu.Zonevu import Zonevu
from zonevu.zonevu.Services import ZonevuError


def main():
    # TODO revise / test
    project_service = zonevu.project_service
    well_service = zonevu.well_service

    confirm_text = input('Click "D" to proceed with delete operation...')
    if confirm_text.lower() == 'd':
        print('Delete confirmed...')

    exit(77)

    proj_name = '_______'
    print('Finding wells for project "%s"' % proj_name)
    projects = project_service.get_projects(proj_name)
    if len(projects) == 0:
        print('No project named "%s" found.' % proj_name)
        exit(1)
    if len(projects) > 1:
        print('Multiple projects named "%s" found.' % proj_name)
        exit(2)

    project = projects[0]
    wells = project_service.get_wells(project)
    print('Number of wells found = %s:' % len(wells))
    for well in wells:
        try:
            print('   Deleting well "%s"...' % well.name, end=" ")
            well_service.delete_well(well)
            print('   Well "%s" deleted.' % well.name)
            count += 1
        except ZonevuError as err:
            if err.status_code == 404:
                print('   Well "%s" was not found.' % well.name)
            else:
                print('   Well "%s" could not be deleted because %s.' % (well.name, err.message))

    print()
    print("Execution was successful")


try:
    zonevu = Zonevu.init_from_keyfile()          # Get zonevu client using a keyfile that has the API key.
    zonevu.get_info().printNotice()         # Check that we can talk to ZoneVu server.
    main()
except ZonevuError as run_err:
    print('Execution of program failed because %s.' % run_err.message)
