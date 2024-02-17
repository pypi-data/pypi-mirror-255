# pylint: disable=too-few-public-methods,super-init-not-called,no-member,broad-exception-raised,attribute-defined-outside-init,arguments-differ,import-error,too-many-arguments,too-many-locals,line-too-long, disable=useless-elif-before-else, disable=R1705, disable=R1720, disable=W1309, disable=C0103
""" GKG Reader SDK"""

import os
from google.cloud import enterpriseknowledgegraph as ekg
from google.protobuf.json_format import MessageToDict
from sdc_dp_helpers.api_utilities.retry_managers import retry_handler, request_handler

class ServiceUnavailableException(Exception):
    """Class for GKG V2  Service Unavailable Exception"""


class GoogleKnowledgeGraphQuotaException(Exception):
    """Class for GKG V2  Quota Exception"""


class RequestHandler:
    """Interface for API call"""

    api_calls = 0

    def __init__(self, creds):
        self._creds = creds

    def make_api_call(self, **kwargs):
        """Make API call"""
        raise NotImplementedError


@request_handler(
        wait=float(os.environ.get("API_WAIT_TIME", 5)),
        backoff_factor=0.01,
        backoff_method='random'
    )
@retry_handler(
    exceptions=GoogleKnowledgeGraphQuotaException,
    total_tries=5,
    initial_wait=61,
    backoff_factor=1.2,
)
@retry_handler(exceptions=ServiceUnavailableException, total_tries=5, initial_wait=100)
class QueriesEndpoints(RequestHandler):
    """ GKG QueriesEndpoints SDK"""
    def __init__(self, client, config):
        self.client = client
        self.config = config

    def make_api_call(self, query: str, language: str):
        RequestHandler.api_calls += 1
        response_json = {}
        parent = self.client.common_location_path(
            project=self.config.get("project_id"), location=self.config.get("location")
        )
        request = ekg.SearchRequest(
            parent=parent,
            query=query,
            languages=[language],
            types=self.config.get("types"),
            limit=self.config.get("limit", 1),
        )
        try:
            response = self.client.search(request=request)
            response_json = MessageToDict(
                response._pb, including_default_value_fields=True
            )
        except Exception as err:
            if err.code == 429:
                raise GoogleKnowledgeGraphQuotaException(
                    f"GoogleKnowledgeGraph Quota Reached"
                    f"Status code: {err.code}, Reason: {err.reason}. "
                ) from err
            if err.code in [404, 500, 202]:
                raise ConnectionError(
                    f"Google Knowledge Graph API failed. "
                    f"Status code: {err.code}, Reason: {err.reason}."
                ) from err
            if err.code in [503]:
                raise ServiceUnavailableException(
                    f"Google Knowledge Graph API failed. "
                    f"Status code: {err.code}, Reason: {err.reason}."
                ) from err
            raise Exception(f"Unexpected error: {err}") from err
        return response_json


@request_handler(
        wait=float(os.environ.get("API_WAIT_TIME", 5)),
        backoff_factor=0.01,
        backoff_method='random'
    )
@retry_handler(
    exceptions=GoogleKnowledgeGraphQuotaException,
    total_tries=5,
    initial_wait=61,
    backoff_factor=1.2,
)
@retry_handler(exceptions=ServiceUnavailableException, total_tries=5, initial_wait=100)
class EnityIdsEndpoints(RequestHandler):
    """ GKG EnityIdsEndpoints SDK"""
    def __init__(self, client, config):
        self.client = client
        self.config = config

    def make_api_call(self, entity_id: str, language: str):
        RequestHandler.api_calls += 1
        response_json = {}
        parent = self.client.common_location_path(
            project=self.config.get("project_id"), location=self.config.get("location")
        )
        request = ekg.LookupRequest(
            parent=parent, ids=[entity_id], languages=[language]
        )
        try:
            response = self.client.lookup(request=request)
            response_json = MessageToDict(
                response._pb, including_default_value_fields=True
            )
        except Exception as err:
            if err.code == 429:
                raise GoogleKnowledgeGraphQuotaException(
                    f"GoogleKnowledgeGraph Quota Reached"
                    f"Status code: {err.code}, Reason: {err.reason}. "
                ) from err
            if err.code in [404, 500, 202]:
                raise ConnectionError(
                    f"Google Knowledge Graph API failed. "
                    f"Status code: {err.code}, Reason: {err.reason}."
                ) from err
            if err.code in [503]:
                raise ServiceUnavailableException(
                    f"Google Knowledge Graph API failed. "
                    f"Status code: {err.code}, Reason: {err.reason}."
                ) from err
            raise Exception(f"Unexpected error: {err}") from err
        return response_json
