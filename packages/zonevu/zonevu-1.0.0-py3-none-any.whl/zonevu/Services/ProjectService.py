from zonevu.zonevu.DataModels import Project, ProjectEntry
from zonevu.zonevu.DataModels.Well import Well
from zonevu.zonevu.DataModels import Survey
from zonevu.zonevu.DataModels import Geomodel
from .Client import Client, ZonevuError
from typing import Tuple, Union


class ProjectService:
    client: Client = None

    def __init__(self, c: Client):
        self.client = c

    def get_projects(self, match_token: str = None) -> list[ProjectEntry]:
        url = "projects"
        if match_token is not None:
            url += "/%s" % match_token
        items = self.client.get(url)
        entries = [ProjectEntry.from_dict(w) for w in items]
        return entries

    def project_exists(self, name: str) -> Tuple[bool, int]:
        projects = self.get_projects(name)
        exists = len(projects) > 0
        project_id = projects[0].id if exists else -1
        return exists, project_id

    def find_project(self, project_id: int) -> Project:
        url = "project/%s" % project_id
        item = self.client.get(url)
        project = Project.from_dict(item)
        return project

    def create_project(self, project: Project) -> None:
        """
        Create a project.
        @param project: project object to be added.
        @return: Throw a ZonevuError if method fails
        """
        url = "project/create"
        item = self.client.post(url, project.to_dict())
        server_project = Survey.from_dict(item)
        project.copy_ids_from(server_project)

    def get_wells(self, project: Union[Project, ProjectEntry]) -> list[Well]:
        """
        Get a list of the wells in a project
        @return:
        """
        url = "project/wells/%s" % project.id
        params = {}
        items = self.client.get(url, params, False)
        entries = [Well.from_dict(w) for w in items]
        return entries

    def add_well(self, project: Project, well: Well) -> None:
        """
        Add a well to a project
        @param project:
        @param well:
        @return:
        """
        url = "project/%s/addwell/%s" % (project.id, well.id)
        # params = [project.id, well.id]
        self.client.post(url, {}, False)

    def remove_well(self, project: Union[Project, ProjectEntry], well: Well) -> None:
        """
        Remove a well from a project
        @param project:
        @param well:
        @return:
        """
        url = "project/%s/removewell/%s" % (project.id, well.id)
        self.client.post(url, {}, False)

    def get_geomodel(self, project: Union[Project, ProjectEntry]) -> Union[Geomodel | None]:
        """
        Get the geomodel for a project
        @return:
        """
        url = "project/geomodel/%s" % project.id
        try:
            item = self.client.get(url, None, False)
            entry = Geomodel.from_dict(item)
            return entry
        except ZonevuError as err:
            if err.status_code == 404:
                return None
            raise err
