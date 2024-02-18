import time
import urllib.parse
from zonevu.zonevu.DataModels.Well import Well
from zonevu.zonevu.DataModels import WellEntry
from .Client import Client, ZonevuError
from .WelllogService import WelllogService
from .SurveyService import SurveyService
from .WelltopService import WelltopService
from .GeosteeringService import GeosteeringService
from .NoteService import NoteService
from typing import Set, Union
from .WellData import WellData, WellDataOptions
from zonevu.zonevu.DataModels import ProjectEntry


class WellService:
    client: Client = None

    def __init__(self, c: Client):
        self.client = c

    def find_by_name(self, match_token: str = None, exact_match: bool = True, page: int = None) \
            -> list[Well]:
        """
        Find listing entries a well or wells whose names match a name or that start with a name fragment
        @param match_token: name or name fragment to use to search for wells. If not provided, gets all wells.
        @param exact_match: whether to exactly match the well name.
        @param page: page number that is used by this method to retrieve all wells since the limit is 500 per call.
        @return: A list of well entries (summary data structures) that match. These are not full well objects.
        """
        url = "wells"
        max_pages = 50     # This means that it won't do more than 50 round trips to retrieve search result pages.
        params = {"exactmatch": exact_match}
        all_entries: list[Well] = []
        more = True
        if match_token is not None:
            params["name"] = urllib.parse.quote_plus(match_token)

        counter = 0
        while more:
            if page is not None:
                params["page"] = page
            wells_response = self.client.get(url, params, False)
            items = wells_response['Wells']
            more = wells_response['More']
            page = wells_response['Page']
            entries = [WellEntry.from_dict(w) for w in items]
            all_entries.extend(entries)
            counter += 1
            if counter > max_pages:
                break               # Safety check. Limits us to 500 iterations, which is 250,000 wells.
            time.sleep(0.050)       # Pause for 50 ms so as not to run into trouble with webapi throttling.

        return all_entries

    def find_by_id(self, well_id: int) -> Well:
        url = "well/id/%s" % well_id
        item = self.client.get(url, {}, False)
        well = Well.from_dict(item)
        return well

    def find_by_uwi(self, uwi: str) -> Union[Well, None]:
        url = "well/uwi"
        params = {"uwi": urllib.parse.quote_plus(uwi)}
        try:
            item = self.client.get(url, params, False)
            well = Well.from_dict(item)
            return well
        except ZonevuError as err:
            if err.status_code == 404:
                return None
            raise err

    def find_wells_original_uwi(self, uwi: str) -> list[Well]:
        # Get wells by original UWI.
        url = "wells/originaluwi"
        params = {'uwi': uwi}
        items = self.client.get(url, params, False)
        entries = [Well.from_dict(w) for w in items]
        return entries

    def get_first_named(self, well_name: str, exact_match: bool = True) -> Union[Well, None]:
        """
        Finds well entry for the first well named 'well_name', and retrieves the full well
        @param well_name: the exact name of the well, including well number, if any
        @return: A well object
        """
        well_entries = self.find_by_name(well_name, exact_match)  # Find well listing entry by name doing an exact match
        if len(well_entries) == 0:
            return None
        well = self.find_by_id(well_entries[0].id)  # Get the full well object from ZoneVu
        return well

    def load_well(self, well: Well, well_data: Set[WellData] = frozenset([WellData.default])) -> None:
        options = WellDataOptions(well_data)
        loaded_well = self.find_by_id(well.id)
        well.merge_from(loaded_well)
        primary_wb = well.primary_wellbore

        if options.welllogs:
            try:
                log_svc = WelllogService(self.client)
                log_svc.load_welllogs(primary_wb, options.curves)
            except Exception as err:
                print('Could not load well logs because %s' % err)

        if options.surveys:
            try:
                survey_svc = SurveyService(self.client)
                survey_svc.load_surveys(primary_wb)
            except Exception as err:
                print('Could not load well surveys because %s' % err)

        if options.tops:
            try:
                top_svc = WelltopService(self.client)
                top_svc.load_welltops(primary_wb)
            except Exception as err:
                print('Could not load well tops because %s' % err)

        if options.geosteering:
            try:
                geosteer_svc = GeosteeringService(self.client)
                geosteer_svc.load_interpretations(primary_wb)
            except Exception as err:
                print('Could not load well geosteering interpretations because %s' % err)

        if options.notes:
            try:
                notes_svc = NoteService(self.client)
                notes_svc.load_notes(primary_wb)
            except Exception as err:
                print('Could not load well user notes because %s' % err)

    def create_well(self, well: Well, well_data: Set[WellData] = frozenset([WellData.default])) -> None:
        options = WellDataOptions(well_data)
        wellUrl = "well/create"
        trimmed_well = well.make_trimmed_copy()
        item = self.client.post(wellUrl, trimmed_well.to_dict())
        created_well = Well.from_dict(item)
        created_wellbore = created_well.primary_wellbore
        well.id = created_well.id
        for wb, wb_copy in zip(well.wellbores, created_well.wellbores):
            wb.id = wb_copy.id

        wellbore = well.primary_wellbore

        # Surveys
        if options.surveys:
            survey_svc = SurveyService(self.client)
            for survey in wellbore.surveys:
                survey_svc.add_survey(created_wellbore, survey)

        # Well tops
        if options.tops:
            top_svc = WelltopService(self.client)
            top_svc.add_tops(created_wellbore, wellbore.tops)

        # Well logs
        if options.welllogs:
            log_svc = WelllogService(self.client)
            for log in wellbore.welllogs:
                log_svc.add_welllog(created_wellbore, log)

        # Well log curve samples
        if options.curves:
            log_svc = WelllogService(self.client)
            for log in wellbore.welllogs:
                for curve in log.curves:
                    log_svc.add_curve_samples(curve)
                log_svc.create_las_file_server(log)    # Create

        # Geosteering interpretations
        if options.geosteering:
            geosteer_svc = GeosteeringService(self.client)
            for interp in wellbore.interpretations:
                geosteer_svc.add_interpretation(created_wellbore, interp)

        # Wellbore notes
        if options.notes:
            notes_svc = NoteService(self.client)
            notes_svc.add_notes(created_wellbore, wellbore.notes)

    def delete_well(self, well_id: int, delete_code: str) -> None:
        url = "well/delete/%s" % well_id
        self.client.delete(url, {"deletecode": delete_code})

    def get_well_projects(self, well_id: int) -> list[ProjectEntry]:
        # Get a list of projects that include this well.
        url = "well/projects/%s" % well_id
        items = self.client.get(url)
        entries = [ProjectEntry.from_dict(w) for w in items]
        return entries





