import json
import requests
from requests import Response
from urllib3.exceptions import InsecureRequestWarning
from dataclasses import dataclass
from typing import Union, Dict
from .EndPoint import EndPoint
from strenum import StrEnum
from .Error import ZonevuError


class UnitsSystemEnum(StrEnum):
    Metric = 'Metric'
    US = 'US'


class Client:
    # private
    _headers = None     # Custom HTTP headers (including Auth header)
    _verify = True      # Whether to check SSL certificate
    _baseurl: str = ''       # ZoneVu instance to call
    _units_system: UnitsSystemEnum    # Units system to use when requesting data

    def __init__(self, endPoint: EndPoint, units: UnitsSystemEnum = UnitsSystemEnum.US):
        self.apikey = endPoint.apikey
        host = endPoint.base_url
        self._verify = endPoint.verify
        if not self._verify:
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        self._baseurl = "https://%s/api/v1.1" % (host)
        self._headers = {'authorization': 'bearer ' + endPoint.apikey}
        self._units_system = units

    def make_url(self, relativeUrl: str, query_params=None, include_units: bool = True):
        if query_params is None:
            query_params = {}
        url = "%s/%s" % (self._baseurl, relativeUrl)
        units = "Meters" if self._units_system == UnitsSystemEnum.Metric else "Feet"
        if include_units:
            query_params['options.distanceunits'] = units
            query_params['options.depthunits'] = units

        for index, (key, value) in enumerate(query_params.items()):
            separator = '?' if index == 0 else '&'
            fragment = "%s%s=%s" % (separator, key, value)
            url += fragment

        return url

    def call_api_get(self, relativeUrl, query_params: dict = None, include_units: bool = True) -> Response:
        if query_params is None:
            query_params = {}
        url = self.make_url(relativeUrl, query_params, include_units)

        r = requests.get(url, headers=self._headers, verify=self._verify)
        try:
            textJson = json.loads(r.text)
            textMsg = textJson['Message'] if ('Message' in textJson) else r.reason
            r.reason = "%s (%s)" % (textMsg, r.status_code)
        except Exception as err:
            pass
        return r

    def get(self, relativeUrl, query_params: dict = None, include_units: bool = True) -> (dict or list):
        r = self.call_api_get(relativeUrl, query_params, include_units)
        Client.assert_ok(r)
        json_obj = json.loads(r.text) if r.text else None
        return json_obj

    def get_text(self, relativeUrl: str, encoding: str = 'utf-8', query_params: dict = None) -> str:
        if query_params is None:
            query_params = {}
        url = self.make_url(relativeUrl, query_params)
        r = requests.get(url, headers=self._headers, verify=self._verify)
        Client.assert_ok(r)
        r.encoding = encoding  # We do this because python assumes strings are utf-8 encoded.
        ascii_text = r.text

        # Test
        r.encoding = 'utf-8'
        utf8_text = r.text

        same = ascii_text == utf8_text

        return ascii_text

    def get_data(self, relativeUrl, query_params: dict = None) -> bytes:
        r = self.call_api_get(relativeUrl, query_params)
        Client.assert_ok(r)
        return r.content

    def call_api_post(self, relativeUrl: str, data: Union[dict, list], include_units: bool = True,
                      query_params: Dict = None) -> Response:
        url = self.make_url(relativeUrl, query_params, include_units)
        r = requests.post(url, headers=self._headers, verify=self._verify, json=data)
        if not r.ok:
            textMsg = ''
            if r.status_code == 404:
                textMsg = r.reason
            else:
                textJson = json.loads(r.text)
                textMsg = textJson['Message'] if ('Message' in textJson) else r.reason
            r.reason = "%s (%s)" % (textMsg, r.status_code)
        return r

    def post(self, relativeUrl: str, data: Union[dict, list], include_units: bool = True,
             query_params: Dict = None) -> (dict or list or None):
        r = self.call_api_post(relativeUrl, data, include_units, query_params)
        Client.assert_ok(r)
        json_obj = json.loads(r.text) if r.text else None
        return json_obj

    def call_api_post_data(self, relativeUrl: str, data: Union[bytes, str, dict], content_type: str = None) -> Response:
        url = self.make_url(relativeUrl, {})
        the_headers = self._headers.copy()
        if content_type is not None:
            the_headers["content-type"] = content_type
        r = requests.post(url, headers=the_headers, verify=self._verify, data=data)
        if not r.ok:
            textMsg = ''
            if r.status_code == 404:
                textMsg = r.reason
            else:
                textJson = json.loads(r.text)
                textMsg = textJson['Message'] if ('Message' in textJson) else r.reason
            r.reason = "%s (%s)" % (textMsg, r.status_code)
        return r

    def post_data(self, relativeUrl, data: Union[bytes, str, dict], content_type: str = None) -> None:
        r = self.call_api_post_data(relativeUrl, data, content_type)
        Client.assert_ok(r)

    def call_api_delete(self, relativeUrl: str, query_params: dict = None) -> Response:
        url = self.make_url(relativeUrl, query_params)
        r = requests.delete(url, headers=self._headers, verify=self._verify)
        if not r.ok:
            textMsg = ''
            if r.status_code == 404:
                textMsg = r.reason
            else:
                textJson = json.loads(r.text)
                textMsg = textJson['Message'] if ('Message' in textJson) else r.reason
            r.reason = "%s (%s)" % (textMsg, r.status_code)
        return r

    def delete(self, relativeUrl: str, query_params: dict = None) -> None:
        r = self.call_api_delete(relativeUrl, query_params)
        Client.assert_ok(r)

    @staticmethod
    def assert_ok(r: Response):
        if not r.ok:
            # raise ResponseError(r)
            raise ZonevuError.server(r)

