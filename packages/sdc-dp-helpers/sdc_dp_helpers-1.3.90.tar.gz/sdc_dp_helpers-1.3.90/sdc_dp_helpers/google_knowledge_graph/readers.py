"""
    CUSTOM READER CLASSES
        - Class which manages writer tasks like
        auth, write metadata, write file, create dir structure
"""
# pylint: disable=no-member,too-many-locals,too-many-arguments,broad-except,too-few-public-methods,arguments-differ,line-too-long,broad-exception-raised,inconsistent-return-statements
from datetime import datetime

from google.oauth2 import service_account
from google.cloud import enterpriseknowledgegraph as ekg
from sdc_dp_helpers.google_knowledge_graph.gkg_sdk import EnityIdsEndpoints, QueriesEndpoints

from sdc_dp_helpers.api_utilities.file_managers import load_file
from sdc_dp_helpers.api_utilities.data_managers import multiple_regex_replace
from sdc_dp_helpers.base_readers import BaseReader


class GoogleKnowledgeGraphReader(BaseReader):
    """Google Knowledge Graph Class"""

    def __init__(self, secrets_filepath: str, config_filepath: str):
        self.secrets: str = secrets_filepath
        self.config: dict = load_file(config_filepath)
        self.client = self._get_auth()
        self.dataset: list = []
        self.success = []
        self.api_calls = 0

    def _get_auth(self):
        """
        Get our credentials initialised above and use those to get client

        """
        credentials = service_account.Credentials.from_service_account_file(
            self.secrets
        )
        client = ekg.EnterpriseKnowledgeGraphServiceClient(credentials=credentials)
        return client

    def format_payload(self, payload, query, language, date, entity_id):
        if payload:
            query_partition: str = self.query_partition(query, language)
            payload.update(
                {
                    "date": date,
                    "query": query,
                    "language": language,
                    "query_partition": query_partition,
                    "entity_id": entity_id,
                }
            )
            self.is_success()
            print(f"Got data for query:'{query}' language:'{language}' on '{date}'")
        if not payload:
            self.not_success()
            print(f"No data for query:'{query}' language:'{language}' on '{date}'")
        return payload

    def get_data(self, endpoints, date, results):
        if endpoints[0] == "entity_ids":
            for query, entity_language in endpoints[1].items():
                languages = list(entity_language[0].values())[0]
                entity_id = list(entity_language[0].keys())[0]
                for language in languages:
                    payload = EnityIdsEndpoints(
                        client=self.client, config=self.config
                    ).make_api_call(entity_id, language)
                    payload = self.format_payload(
                        payload, query, language, date, entity_id
                    )
                    if payload:
                        results.append(payload)
        if endpoints[0] == "queries":
            for query, languages in endpoints[1].items():
                for language in languages:
                    entity_id = None
                    payload = QueriesEndpoints(
                        client=self.client, config=self.config
                    ).make_api_call(query, language)
                    payload = self.format_payload(
                        payload, query, language, date, entity_id
                    )
                    if payload:
                        results.append(payload)
        return results

    def query_partition(self, query: str, language: str = None) -> str:
        """Helper to get the query partition string
        :query: "string",
        :language:"string"}
        :returns: query_partition - str
        """
        query = query.strip()
        query_partition = multiple_regex_replace(
            query, {".": "_dot_", " ": "_space_", "+": "_plus_"}
        )
        if language:
            query_partition = f"{query_partition}_lang_{language}"

        return query_partition

    def _query_handler(self):
        results=[]
        date = datetime.strftime(datetime.now(), "%Y-%m-%d")
        for endpoints in self.config["endpoints"].items():
            results = self.get_data(endpoints, date, results)
        if results:
            return {"date": date, "data": results}
        self.dataset = results

    def run_query(self):
        output = self._query_handler()
        return output
