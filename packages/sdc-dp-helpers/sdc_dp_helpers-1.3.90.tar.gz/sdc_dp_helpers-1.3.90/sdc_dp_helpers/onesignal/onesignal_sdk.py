"""SDK MODULE FOR ONESIGNAL"""
# pylint: disable=arguments-differ,too-few-public-methods,too-many-arguments
import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Generator, Union
from datetime import datetime
import requests
from sdc_dp_helpers.api_utilities.retry_managers import request_handler, retry_handler
from sdc_dp_helpers.api_utilities.file_managers import parse_zip_to_csv
from sdc_dp_helpers.api_utilities.date_managers import date_string_handler


class AuthenticationError(Exception):
    """class for Authentication Errors"""


class HTTP500InternalServerError(Exception):
    """class to handle Internal Server Error 500"""


class NoDownloadYetError(Exception):
    """class for handling no download ready yet"""


class ExistingScheduledDownloadError(Exception):
    """Error raised if there exists a scheduled download"""


class CSVExportCreationError(Exception):
    """Error raised when we fail to create bulk job and get back a None"""


class ViewNotificationsDownloadError(Exception):
    """Error for view notifications data download"""


class APICallHandler(ABC):
    """Base class for API Calls"""

    def __init__(self, creds: dict):
        self.creds = creds
        self._header = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Basic {self.creds['api_key']}",
            "User-Agent": "Mozilla/5.0",
        }

    @abstractmethod
    def api_call(self, **kwargs):
        """_summary_
        Raises:
            NotImplementedError: needs to be implemented for all child classes
        """
        raise NotImplementedError


class CreateBulkDownload(APICallHandler):
    """Class for Creating Bulk Doanload"""

    @retry_handler(
        HTTP500InternalServerError, total_tries=3, initial_wait=61, backoff_factor=1.2
    )
    @retry_handler(ConnectionError, total_tries=3, initial_wait=32, backoff_factor=1.2)
    @retry_handler(
        ExistingScheduledDownloadError, total_tries=10, initial_wait=2, backoff_factor=2
    )
    def api_call(self, session: requests.Session) -> Dict[str, str]:
        _app_id: str = self.creds["app_id"]
        url = f"https://onesignal.com/api/v1/players/csv_export?app_id={_app_id}"
        try:
            response = session.post(url=url, headers=self._header, timeout=61)
            response.raise_for_status()
            return response.json()

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.ConnectTimeout,
        ) as exc:
            raise ConnectionError(exc) from exc

        except requests.exceptions.HTTPError as exc:
            raise HTTP500InternalServerError(exc) from exc

        except requests.exceptions.RequestException as exc:
            if "Please include a case-sensitive header of Authorization" in str(
                response.json()
            ):
                raise AuthenticationError(
                    "Please check the credentials used to make api call"
                ) from exc
            if "User already running another CSV export." in str(response.json()):
                print("Got into the down scheduled part")
                raise ExistingScheduledDownloadError(response.json()) from exc

            raise exc


class FetchBulkDownload(APICallHandler):
    """Class to fetch the generated bulk download"""

    @retry_handler(
        HTTP500InternalServerError, total_tries=3, initial_wait=61, backoff_factor=1.2
    )
    # we wait maximum 30 minutes for download to be ready otherwise we just raise an error
    @retry_handler(NoDownloadYetError, total_tries=10, initial_wait=2, backoff_factor=2)
    @retry_handler(ConnectionError, total_tries=3, initial_wait=32, backoff_factor=2)
    def api_call(self, session: requests.Session, url: str):
        """call for downloading the prepared csv export"""
        try:
            response = session.get(url=url, timeout=61)
            response.raise_for_status()
            return response.content
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.ConnectTimeout,
        ) as exc:
            raise ConnectionError(exc) from exc

        except requests.exceptions.HTTPError as exc:
            if response.status_code == 404:
                raise NoDownloadYetError(exc) from exc
            raise HTTP500InternalServerError(exc) from exc

        except requests.exceptions.RequestException as exc:
            if response.status_code == 404:
                raise NoDownloadYetError(exc) from exc
            raise exc


class ViewNotificationsDownload(APICallHandler):
    """class for fetching view notifications"""

    @retry_handler(
        HTTP500InternalServerError, total_tries=3, initial_wait=61, backoff_factor=1.2
    )
    @retry_handler(ConnectionError, total_tries=3, initial_wait=61, backoff_factor=1.2)
    @request_handler(
        wait=int(os.environ.get("API_WAIT_TIME", 5)),
        backoff_factor=0.01,
        backoff_method="random",
    )
    def api_call(
        self, session: requests.Session, limit: int, offset: int
    ) -> Tuple[bool, Dict[Any, Any]]:
        """
        Handles the view notification request attempt.
        """
        _app_id: str = self.creds["app_id"]
        url = f"https://onesignal.com/api/v1/notifications?app_id={_app_id}"
        more_records = False
        try:
            response = session.get(
                url=url,
                headers=self._header,
                params={"limit": limit, "total_count": "true", "offset": offset},
                timeout=61,
            )
            response.raise_for_status()
            results = response.json()
            total_records: int = int(results.get("total_count", 0))
            if total_records >= offset:
                more_records = True

            return more_records, results
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.ConnectTimeout,
        ) as exc:
            raise ConnectionError(exc) from exc

        except requests.exceptions.HTTPError as exc:
            raise HTTP500InternalServerError(exc) from exc

        except requests.exceptions.RequestException as exc:
            if "Please include a case-sensitive header of Authorization" in str(
                response.json()
            ):
                raise AuthenticationError(
                    "Please check the credentials used to make api call"
                ) from exc
            raise exc


class OneSignalHandler:
    """class to do the data pull"""

    def __init__(self, creds: dict, configs: dict):
        self.creds = creds
        self.session = requests.Session()
        self.configs = configs
        self.file_size_limit: int = self.configs.get("file_size_limit", 500000)

    def fetch_data(self) -> Generator[Dict[Any, Any], None, None]:
        """Method to fetch the data from source"""
        raise NotImplementedError


class ViewNotificationsHandler(OneSignalHandler):
    """Fetch View Notifications"""

    def __init__(self, creds: dict, configs: dict):
        self.offset: int = 0
        self.api_call_limit: int = configs.get("api_call_limit", 2000)
        super().__init__(creds=creds, configs=configs)

    def format_date(
        self, date_value: Union[str, None], result: dict
    ) -> Union[str, None]:
        """process date from int to YYYY-mm-dd"""
        if date_value is None:
            date_value = result.get("queued_at")
        if date_value is None:
            return None
        return datetime.fromtimestamp(int(date_value)).strftime("%Y%m%d")

    def check_limit_reached(
        self,
        partition_dataset: Dict[Any, Any],
        results: List[dict],
        startdate: int,
        enddate: int,
        more_records: bool = True,
    ) -> Tuple[bool, Dict]:
        """method to check if we have reached the end of api call

        Args:
            partition_dataset (Dict[Any, Any]): data_dictionary
            results (dict): results dictionary
            startdate (int): end date to when to stop api call
            enddate (int): end date to when to stop api call
            more_records (True): chec if we have reached end of api call

        Returns:
            Tuple[Dict, bool]: more records and the data dictionary
        """
        exit_condition: List[bool] = []
        for result in results:
            queued_at = result.get("queued_at")
            queued_at_date_str = self.format_date(queued_at, result)
            if queued_at_date_str is None or int(queued_at_date_str) > enddate:
                continue
            if int(queued_at_date_str) < startdate:
                exit_condition.append(True)
            else:
                result["completed_at_date"] = self.format_date(
                    result.get("completed_at"), result
                )
                result["queued_at_date"] = queued_at_date_str
                result["app_id"] = self.creds["app_id"]
                partition_dataset.setdefault(queued_at_date_str, []).append(result)

        if any(exit_condition) or self.api_call_limit <= 0:
            more_records = False

        return more_records, partition_dataset

    def fetch_data(self):
        """fecth data method"""
        # gather data per offset given the set of limits
        limit = self.configs.get("limit", 50)
        api_call_handler: APICallHandler = ViewNotificationsDownload(creds=self.creds)
        more_records: bool = True
        startdate: int = int(
            date_string_handler(self.configs.get("start_date", "2_days_ago")).strftime(
                "%Y%m%d"
            )
        )
        enddate: int = int(
            date_string_handler(self.configs.get("end_date", "today")).strftime(
                "%Y%m%d"
            )
        )
        print(f"working with startdate: {startdate} enddate {enddate}")
        partition_dataset: Dict[Any, Any] = {}
        while more_records:
            response = api_call_handler.api_call(
                session=self.session, limit=limit, offset=self.offset
            )
            if response is None:
                print("No data for view notifications")
            more_records, results = response[0], response[1]
            notifications = results.get("notifications")
            if notifications is not None and isinstance(notifications, list):
                more_records, partition_dataset = self.check_limit_reached(
                    partition_dataset, notifications, startdate, enddate, more_records
                )
                print(f"At offset {self.offset} of {results.get('total_count')}")

            self.offset += limit
            self.api_call_limit -= 1
            print(f"api call limit {self.api_call_limit}")

        if not partition_dataset:
            print("No view notifications data")
            return

        for date, date_dataset in partition_dataset.items():
            yield {"date": date, "data": date_dataset}


class CSVExportHandler(OneSignalHandler):
    """Class to make the CSV Export Job"""

    @staticmethod
    def add_created_at_date(row) -> Dict[Any, Any]:
        """function to add created_at_date"""
        try:
            row["created_at_date"] = str(
                datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S").date()
            ).replace("-", "")
        except ValueError:
            row["created_at_date"] = str(
                datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S.%f").date()
            ).replace("-", "")
        return row

    def fetch_data(self):
        """fetch data method for csv export"""
        bulk_creator: APICallHandler = CreateBulkDownload(creds=self.creds)
        api_call_handler: APICallHandler = FetchBulkDownload(creds=self.creds)
        bulk_job: Dict[str, str] = bulk_creator.api_call(self.session)
        if (bulk_job is None) or not isinstance(bulk_job, dict):
            raise CSVExportCreationError(
                f"Failed to create bulk job for {self.creds['app_id']}"
            )
        csv_file_url = bulk_job.get("csv_file_url")
        if csv_file_url is not None and isinstance(csv_file_url, str):
            print(f"created_job app_id: {self.creds['app_id']}: {bulk_job}")
            response = api_call_handler.api_call(self.session, url=csv_file_url)
            partition_dataset: Dict[Any, Any] = {}
            results = parse_zip_to_csv(response=response, file_type="gzip")
            if not results:
                print(f"No data for csv export for appi_id {self.creds['app_id']}")
                sys.exit(0)
            for result in results:
                result["app_id"] = self.creds["app_id"]  # inject app_id as metadata
                result = self.add_created_at_date(result)  # add created_at_date
                date_value = result.get("created_at_date")
                if date_value is not None:
                    partition_dataset.setdefault(date_value, []).append(result)

            for date, date_dataset in partition_dataset.items():
                yield {"date": date, "data": date_dataset}


class OneSignalHandlerFactory:
    """Factory to get us the Handler"""

    def get_endpoint_handler(self, creds: dict, configs: dict) -> OneSignalHandler:
        """Gets Us the Endpoint Hanlder to Use"""
        endpoint_handlers = {
            "csv_export": CSVExportHandler,
            "view_notifications": ViewNotificationsHandler,
        }

        return endpoint_handlers[configs["endpoint"]](creds=creds, configs=configs)
