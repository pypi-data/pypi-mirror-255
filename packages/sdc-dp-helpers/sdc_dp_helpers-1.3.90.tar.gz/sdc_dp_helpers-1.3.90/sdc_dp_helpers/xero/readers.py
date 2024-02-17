# pylint: disable=no-member,inconsistent-return-statements,wrong-import-order,broad-exception-raised,no-else-return,arguments-differ
from sdc_dp_helpers.api_utilities.file_managers import load_file
from sdc_dp_helpers.xero.xero_sdk import XeroAPI
from sdc_dp_helpers.base_readers import BaseReader


class XeroReader(BaseReader):
    """
        Xero reader
    """
    def __init__(self, config_path: str, creds_filepath: str):
        self.creds_path: str = creds_filepath
        self.config: dict = load_file(config_path, "yml")
        self.service = self._get_auth()

    def _get_auth(self):
        self.service = XeroAPI(
            config=self.config, creds_filepath=self.creds_path
        )
        return self.service

    def _query_handler(self):
        if self.config.get("modules"):
            for module in self.config.get("modules", []):
                data = self.service.fetch_modules(module), module
        if self.config.get("reports"):
            for report in self.config.get("reports", []):
                data = self.service.fetch_reports(report), report
        return data

    def run_query(self):
        payload, endpoint_name = self._query_handler()
        if payload:
            self.is_success()
            return payload
        else:
            self.not_success()
            print(f"No data for endpoint {endpoint_name}")
