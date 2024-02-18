from zonevu.zonevu.DataModels import Survey
from zonevu.zonevu.DataModels import Station
from zonevu.zonevu.DataModels import Wellbore
from .Client import Client


class SurveyService:
    client: Client = None

    def __init__(self, c: Client):
        self.client = c

    def get_surveys(self, wellbore_id: int) -> list[Survey]:
        url = "surveys/%s" % wellbore_id
        items = self.client.get(url)
        surveys = [Survey.from_dict(w) for w in items]
        return surveys

    def find_survey(self, survey_id: int) -> Survey:
        url = "survey/%s" % survey_id
        item = self.client.get(url)
        survey = Survey.from_dict(item)
        return survey

    def load_survey(self, survey: Survey) -> Survey:
        full_survey = self.find_survey(survey.id)
        survey.copy_ids_from(full_survey)
        return survey

    def load_surveys(self, wellbore: Wellbore) -> list[Survey]:
        surveys = self.get_surveys(wellbore.id)
        wellbore.surveys = []
        for survey in surveys:
            complete_survey = self.find_survey(survey.id)
            wellbore.surveys.append(complete_survey)
        return surveys

    def add_survey(self, wellbore: Wellbore, survey: Survey) -> None:
        """
        Adds a survey to a wellbore. Updates the passed in survey with zonevu ids.
        @param wellbore: Zonevu id of wellbore to which survey will be added.
        @param survey: Survey object
        @return: Throw a ZonevuError if method fails
        """
        url = "survey/add/%s" % wellbore.id
        item = self.client.post(url, survey.to_dict())
        server_survey = Survey.from_dict(item)
        survey.copy_ids_from(server_survey)

    def delete_survey(self, survey: Survey) -> None:
        url = "survey/delete/%s" % survey.id
        self.client.delete(url)

    def add_stations(self, survey: Survey, stations: list[Station]) -> list[Station]:
        url = "survey/add-stations/%s" % survey.id
        data = [s.to_dict() for s in stations]
        r = self.client.post(url, data)
        return r




