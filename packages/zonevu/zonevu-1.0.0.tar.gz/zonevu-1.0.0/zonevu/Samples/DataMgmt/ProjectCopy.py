import copy
from zonevu.zonevu.Zonevu import Zonevu
from zonevu.zonevu.Services import ZonevuError


def main():
    # TODO revise / test
    project_service = zonevu.project_service

    print('Projects:')
    projects = project_service.get_projects()
    for project in projects:
        print('%s (%s)' % (project.name, project.id))
        geomodel = project_service.get_geomodel(project)
        if geomodel is not None:
            print('   - Geomodel Name: %s' % geomodel.name)

    project = project_service.find_project(1180)
    print('Project Name: %s' % project.name)
    # print(project)

    project_copy = copy.deepcopy(project)
    project_copy.name = '%s_Copy' % project.name
    project_service.create_project(project_copy)

    print("Execution was successful")


try:
    zonevu = Zonevu.init_from_keyfile()          # Get zonevu client using a keyfile that has the API key.
    zonevu.get_info().printNotice()         # Check that we can talk to ZoneVu server.
    main()
except ZonevuError as run_err:
    print('Execution of program failed because %s.' % run_err.message)
