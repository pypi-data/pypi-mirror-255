# pylint: disable=too-few-public-methods,unused-imports,attribute-defined-outside-init,broad-exception-raise,trailing-whitespace,line-too-long,no-member,broad-exception-raised,bare-except
import json
import ast
import os
import requests
#from oauth2 import *
from xero import Xero
from xero.auth import OAuth2Credentials
from xero.exceptions import XeroForbidden
from sdc_dp_helpers.api_utilities.retry_managers import request_handler, retry_handler



def date_filter_helper(from_date: str, to_date: str, filter_field: str = None) -> str:
    """
    Custom implementation of date filters borrowed from:
    https://github.com/ClaimerApp/pyxero/blob/master/xero/basemanager.py
    """
    if not from_date:
        raise ValueError("No from_date set")

    # common date_field inside of the accounts and contacts modules is UpdatedDateUTC
    filter_field = "UpdatedDateUTC" if not filter_field else filter_field
    api_filter = filter_field + ">=DateTime(" + ",".join(from_date.split("-")) + ")"
    if to_date:
        api_filter = (
            api_filter
            + "&&"
            + filter_field
            + "<=DateTime("
            + ",".join(to_date.split("-"))
            + ")"
        )
    # end if
    return api_filter

class XeroQuotaException(Exception):
    """Class for Xero  Quota Exception"""

class Authenticator:
    """
    Xero authentication and token refresh
    """
    def __init__(self, config, creds_filepath):
        self.creds_path: str = creds_filepath
        self.config: dict = config

    def token_isvalid(self, creds: OAuth2Credentials) -> bool:
        if not isinstance(creds, OAuth2Credentials):
            raise TypeError("creds is not an object of type OAuth2Credentials")

        return creds.get_tenants()[0]["tenantId"] is not None

    def get_auth_token(self) -> OAuth2Credentials:
        """
        Consumes the client id and the previous auth processes refresh token.
        This returns an authentication token that will last 30 minutes
        to make queries the minute it is used. Or it will expire in 60 days of no use.
        The newly generated last refresh token now needs token stored for
        next use.
        PS: we receive and save the auth_token in a local dir supplied by the encapsulating project
        we never interact with s3 from inside of this class
        """
        self.client_id = self.config.get("client_id", None)
        if not self.client_id:
            raise ValueError("No client_id set")
        if (not self.client_id) or (len(self.client_id) != 32):
            raise ValueError("Invalid client_id")

        with open(self.creds_path, "r") as token_file:
            auth_token = ast.literal_eval(token_file.read())

        auth_creds = OAuth2Credentials(
            self.client_id, client_secret="", token=auth_token
        )
        return self.refresh_auth_token(auth_creds)

    def refresh_auth_token(self, auth_creds: OAuth2Credentials) -> OAuth2Credentials:
        cred = {
            "grant_type": "refresh_token",
            "refresh_token": auth_creds.token["refresh_token"],  #
            "client_id": self.config.get("client_id", None),
        }
        response = requests.post(
            "https://identity.xero.com/connect/token", cred, timeout=30
        )
        auth_token = response.json()
        # print("response:", auth_token)
        # print("auth keys", auth_token.keys())
        err_message = auth_token.get("error")
        if err_message:
            raise Exception(err_message)

        # print("Writing new Xero token to path: ", self.creds_path)
        with open(self.creds_path, "w") as outfile:
            outfile.write(json.dumps(auth_token))

        auth_creds = OAuth2Credentials(
            self.client_id, client_secret="", token=auth_token
        )
        if not self.token_isvalid(auth_creds):
            raise XeroForbidden(
                f"Error while trying to authenticate the refreshed token: {str(auth_creds)}"
            )
        return auth_creds

class XeroAPI:
    """
    Class for making Xero API calls
    """
    def __init__(self, config, creds_filepath):
        self.creds_path: str = creds_filepath
        self.config: dict = config
        self.authenticator = Authenticator(config=self.config ,creds_filepath=self.creds_path)
        #self.auth_token = self.authenticator.get_auth_token()

    @request_handler(
        wait=int(os.environ.get("REQUEST_WAIT_TIME", 0.1)),
        backoff_factor=float(os.environ.get("REQUEST_BACKOFF_FACTOR", 0.01)),
        backoff_method=os.environ.get("REQUEST_BACKOFF_METHOD", 0.01),
    )
    @retry_handler(exceptions=XeroQuotaException, total_tries=5, initial_wait=5)
    def fetch_report(self, request_params):
       
        auth_token = self.authenticator.get_auth_token()
        headers = {
            "Authorization": "Bearer " + auth_token.token["access_token"],
            "Xero-Tenant-Id": self.config["tenant_id"],
            "Accept": "application/json",
        }
        params = {
            "fromDate": self.config["start_date"],
            "toDate": self.config["end_date"],
        }
        if request_params["tracking_category"]:
            params.update(
                {
                    "trackingCategoryID": request_params["tracking_category"][
                        "TrackingCategoryID"
                    ]
                }
            )
        if request_params["TrackingOptionID"]:
            params.update({"TrackingOptionID": request_params["TrackingOptionID"]})

        if "contactId" in request_params.keys():
            params.update({"contactId": request_params["contactId"]})
        try:
            response = requests.get(
                "https://api.xero.com/api.xro/2.0/Reports/" + request_params["report_name"],
                params=params,
                headers=headers,
                timeout=30,
            )
            report = json.loads(
                    response.text.replace("\r", "").replace("\n", "").strip("'<>() "))
        except Exception as err:
            if int(response.status_code) == 429:
                os.environ['API_WAIT_TIME'] = str(10)
                raise XeroQuotaException(
                    f"Xero Quota Reached"
                    f"Status code: {err.code}, Reason: {err.reason}. "
                ) from err
            raise Exception(f"Unexpected error: {err}") from err
        return json.dumps(report)

    def format_values(self, report, option_id):
        for row in range(len(report["Reports"][0]["Rows"])):
            try:
                for row in report["Reports"][0]["Rows"][row]["Rows"]:
                    for cells in row["Cells"]:
                        cells["Attributes"][0].update({"type": row["Cells"][0]["Value"]})
            except:
                pass
        report["TrackingOptionID"] = option_id["TrackingOptionID"]
        report["TrackingOptionName"] = option_id["Name"]
        report["tenantId"] = self.config.get("tenant_id")
        return report
    def fetch_reports(self, report_name) -> dict:
        """
        Loops through reports in the config to pull each of them
        """
        data_set = {}
        if report_name not in [
            "BalanceSheet",
            "ProfitAndLoss",
            "AgedPayablesByContact",
            "AgedReceivablesByContact",
        ]:
            raise ValueError(report_name + " is not supported or does not exist.")

        auth_token = self.authenticator.get_auth_token()

        auth_token.tenant_id = self.config.get("tenant_id")

        xero_obj = Xero(auth_token)
        trackingcategories = (
            i for i in xero_obj.trackingcategories.all() if i is not None
        )
        trackingcategories_ ={}
        for tracking_category in trackingcategories:
            option_data = []
            for option_id in tracking_category["Options"]:
                request_params = {
                    "report_name": report_name,
                    "tracking_category": tracking_category,
                    "TrackingOptionID": option_id["TrackingOptionID"],
                }
                if report_name in ["BalanceSheet", "ProfitAndLoss"]:
                    file_name = (
                        report_name + "_" + tracking_category["TrackingCategoryID"]
                    )
                    result = self.fetch_report(request_params)
                    result = json.loads(result)
                    result = self.format_values(result, option_id)
                    option_data.append(result)

                elif report_name in [
                    "AgedPayablesByContact",
                    "AgedReceivablesByContact",
                ]:
                    for contact in xero_obj.contacts.filter(
                        raw="AccountNumber!=null",
                        AccountNumber__startswith="999999",
                    ):
                        request_params.update({"contactId": contact["ContactID"]})
                        file_name = (
                            report_name
                            + "_"
                            + tracking_category["TrackingCategoryID"]
                            + "_"
                            + contact["ContactID"]
                        )

                        result = self.fetch_report(request_params)
                        result = json.loads(result)
                        result = self.format_values(result, option_id)
                        option_data.append(result)
            trackingcategories_[tracking_category["Name"]]=tracking_category
            option_data.append(trackingcategories_)
            result = {
                "endpoint":report_name,
                "tenant_name":self.config["tenant_name"],
                "trackingCategoryId": tracking_category["TrackingCategoryID"],
                "data": option_data,
                "date": self.config["end_date"]}

            if option_data and option_data is not None:
                data_set.update({file_name: result})
        return data_set
    
    @request_handler(
        wait=int(os.environ.get("REQUEST_WAIT_TIME", 0.1)),
        backoff_factor=float(os.environ.get("REQUEST_BACKOFF_FACTOR", 0.01)),
       backoff_method=os.environ.get("REQUEST_BACKOFF_METHOD", 0.01),
    )
    def run_request(self, xero_client, api_object, request):
        """
        Run the API request that consumes a request payload and site url.
        This separates the request with the request handler from the rest of the logic.
        """
        # To Do Handle API Errors
        api_call = getattr(xero_client, api_object)
        # XeroRateLimitExceeded
        return api_call.filter(
            raw=date_filter_helper(request["from_date"], request["to_date"]),
            page=request["page"],
        )

    def fetch_modules(self,module)-> dict:
        """
        Consumes a .yaml config file and loops through the date and url
        to return relevant data from Xero API.
        """
        auth_token = self.authenticator.get_auth_token()
        auth_token.tenant_id =  self.config["tenant_id"]
        xero = Xero(auth_token)
        data_set = {}
        if module not in [
            "contacts",
            "accounts",
            "invoices",
            "banktransactions",
            "manualjournals",
            "purchaseorders",
        ]:
            raise ValueError(module + " is not supported or does not exist.")
        data_set[module] = []
        prev_response = None
        page = 1
        while True:
            response = self.run_request(
                xero_client=xero,
                api_object=module,
                request={
                    "from_date": self.config.get("from_date"),
                    "to_date": self.config.get("to_date"),
                    "page": page,
                },
            )
            if len(response) < 1:
                print("Request returned empty payload. breaking...")
                break
            if response == prev_response:
                print("Request returned copy of last payload. breaking...")
            data_set[module] += [
                json.loads(
                    json.dumps(response_obj, indent=4, sort_keys=True, default=str)
                )
                for response_obj in response
            ]
            # ensure the token is still fresh
            auth_token = self.get_auth_token()
            prev_response = response
            page += 1
        return data_set
