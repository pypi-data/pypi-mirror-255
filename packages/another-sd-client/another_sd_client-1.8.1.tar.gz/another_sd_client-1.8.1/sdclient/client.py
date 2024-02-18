from pyexpat import ExpatError
from typing import OrderedDict
from typing import Tuple

import httpx
import xmltodict
from httpx import HTTPError
from httpx import HTTPStatusError
from httpx import StreamError

from sdclient.exceptions import SDCallError
from sdclient.exceptions import SDHTTPStatusError
from sdclient.exceptions import SDParseResponseError
from sdclient.requests import GetDepartmentRequest
from sdclient.requests import GetEmploymentRequest
from sdclient.requests import GetOrganizationRequest
from sdclient.requests import SDRequest
from sdclient.responses import GetDepartmentResponse
from sdclient.responses import GetEmploymentResponse
from sdclient.responses import GetOrganizationResponse


class SDClient:
    BASE_URL = "https://service.sd.dk/sdws/"
    ENDPOINT_SUFFIX = "20111201"

    def __init__(self, sd_username: str, sd_password: str, timeout: int = 120):
        self.username = sd_username
        self.password = sd_password
        self.timeout = timeout

    def _call_sd(
        self, query_params: SDRequest, xml_force_list: Tuple[str, ...] = tuple()
    ) -> OrderedDict:
        """
        Call SD endpoint.

        Easiest way to obtain a Pydantic instance (which is created based on
        the OrderedDict returned from this method) seems to be
        XML -> OrderedDict (via xmltodict) -> Pydantic instance
        instead of using the lxml library, since we can use the Pydantic method
        parse_obj to generate to instances directly from OrderedDicts.

        Args:
            query_params: The HTTP query parameters to set in the request
            xml_force_list: A tuple of elements in the returned OrderedDict
                which MUST be lists. This ensures that the SD OrderedDicts
                are compatible with the SD response Pydantic models
        Returns:
            XML response from SD in the form of an OrderedDict
        """

        # Get the endpoint name, e.g. "GetEmployment20111201"
        endpoint_name = query_params.get_name() + SDClient.ENDPOINT_SUFFIX

        try:
            response = httpx.get(
                SDClient.BASE_URL + endpoint_name,
                params=query_params.to_query_params(),
                auth=(self.username, self.password),
                timeout=self.timeout,
            )
        except (HTTPError, StreamError) as err:
            raise SDCallError(
                "There was a problem calling SD",
                endpoint_name,
                query_params,
            ) from err

        try:
            response.raise_for_status()
        except HTTPStatusError as err:
            raise SDHTTPStatusError(
                "HTTP error status returned",
                endpoint_name,
                query_params,
                response.status_code,
                response.text,
            ) from err

        # Nice for debugging
        # import lxml.etree
        # sd_xml_resp = lxml.etree.XML(response.text.split(">", maxsplit=1)[1])
        # xml = lxml.etree.tostring(sd_xml_resp, pretty_print=True).decode("utf-8")
        # print(xml)

        try:
            xml_to_ordered_dict = xmltodict.parse(
                response.text, force_list=xml_force_list
            )
        except Exception as err:
            raise SDParseResponseError(
                "XML response from SD could not be parsed",
                endpoint_name,
                query_params,
            ) from err

        root_elem = xml_to_ordered_dict.get(endpoint_name)

        return root_elem

    def get_department(
        self, query_params: GetDepartmentRequest
    ) -> GetDepartmentResponse:
        """
        Call the SD endpoint GetDepartment.

        Args:
            query_params: The HTTP query parameters to set in the request

        Returns:
            XML response from SD converted to Pydantic
        """
        root_elem = self._call_sd(query_params, xml_force_list=("Department",))
        return GetDepartmentResponse.parse_obj(root_elem)

    def get_employment(
        self, query_params: GetEmploymentRequest
    ) -> GetEmploymentResponse:
        """
        Call the SD endpoint GetEmployment.

        Args:
            query_params: The HTTP query parameters to set in the request

        Returns:
            XML response from SD converted to Pydantic
        """

        root_elem = self._call_sd(query_params, xml_force_list=("Person", "Employment"))
        return GetEmploymentResponse.parse_obj(root_elem)

    def get_organization(
        self, query_params: GetOrganizationRequest
    ) -> GetOrganizationResponse:
        """
        Call the SD endpoint GetEmployment.

        Args:
            query_params: The HTTP query parameters to set in the request

        Returns:
            XML response from SD converted to Pydantic
        """

        root_elem = self._call_sd(
            query_params, xml_force_list=("DepartmentReference", "Organization")
        )
        return GetOrganizationResponse.parse_obj(root_elem)
