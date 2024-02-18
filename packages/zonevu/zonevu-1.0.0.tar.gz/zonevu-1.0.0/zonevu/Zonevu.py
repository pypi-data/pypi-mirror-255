import sys
from typing import Callable, Dict
from zonevu.zonevu.DataModels import Company
from zonevu.zonevu.Services.Error import ZonevuError
from zonevu.zonevu.Services.EndPoint import EndPoint
from zonevu.zonevu.Services import WellService
from zonevu.zonevu.Services import SurveyService
from zonevu.zonevu.Services.Client import Client, UnitsSystemEnum
from zonevu.zonevu.Services import CompanyService
from zonevu.zonevu.Services.WelllogService import WelllogService
from zonevu.zonevu.Services import GeosteeringService
from zonevu.zonevu.Services import ProjectService
from zonevu.zonevu.Services import CoordinatesService
from zonevu.zonevu.Services import FormationService
from zonevu.zonevu.Services import GeomodelService
from zonevu.zonevu.Services import MapService


class Zonevu:
    # Represents the ZoneVu version 1.1 API
    # private
    _client: Client = None

    def __init__(self, endPoint: EndPoint, units_system: UnitsSystemEnum = UnitsSystemEnum.US):
        # Make sure we are running in python 3.11 or later
        correct_python = sys.version_info.major >= 3 and sys.version_info.minor >= 11
        if not correct_python:
            raise ZonevuError.local("Python version is too old. The ZoneVu python library requires python "
                                    "version 3.11 or later.")
        self._client = Client(endPoint, units_system)

    @classmethod
    def init_from_keyfile(cls, units_system: UnitsSystemEnum = UnitsSystemEnum.US) -> 'Zonevu':
        """
        Instantiates an instance of Zonevu from a keyfile whose path is specified as an argument to the script
        See EndPoint.from_keyfile() for details on how to set up a keyfile.
        @return: A reference to the zonevu instance.
        """
        endpoint = EndPoint.from_keyfile()
        zonevu = cls(endpoint, units_system)  # Get zonevu python client
        zonevu.get_info().printNotice()       # Check that we can talk to ZoneVu server and print notice.
        return zonevu

    def run(self, main: Callable[[Dict[str, any]], None], params: [Dict[str, any]]) -> None:
        """
        A convenience method to run a function in a standardized zonevu execution harness.
        @param params:
        @param main:
        """
        main_name = main.__name__
        try:
            print('ZoneVu SDK execution of program "%s"' % main_name)
            self.get_info().printNotice()
            main(params)
            print('ZoneVu SDK execution of program "%s" succeeded' % main_name)
        except ZonevuError as error:
            print('** ZoneVu SDK execution of program "%s" failed because %s.' % (main_name, error.message))

    # Services -- use these properties to get an instance of a particular zonevu web api service.
    @property
    def company_service(self) -> CompanyService:
        return CompanyService(self._client)

    @property
    def well_service(self) -> WellService:
        return WellService(self._client)

    @property
    def welllog_service(self) -> WelllogService:
        return WelllogService(self._client)

    @property
    def survey_service(self) -> SurveyService:
        return SurveyService(self._client)

    # @property
    # def curve_service(self) -> CurveService:
    #     return CurveService(self._client)

    @property
    def geosteering_service(self) -> GeosteeringService:
        return GeosteeringService(self._client)

    @property
    def project_service(self) -> ProjectService:
        return ProjectService(self._client)

    @property
    def coordinates_service(self) -> CoordinatesService:
        return CoordinatesService(self._client)

    @property
    def formation_service(self) -> FormationService:
        return FormationService(self._client)

    @property
    def geomodel_service(self) -> GeomodelService:
        return GeomodelService(self._client)

    @property
    def map_service(self) -> MapService:
        return MapService(self._client)

    # High level API
    # Company
    def get_info(self) -> Company:
        """
        Gets information about the company using this API and the ZoneVu version
        :return: The info
        :rtype: Company info object
        """
        return self.company_service.get_info()







