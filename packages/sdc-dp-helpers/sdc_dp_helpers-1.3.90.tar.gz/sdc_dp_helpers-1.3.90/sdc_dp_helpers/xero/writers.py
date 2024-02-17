# pylint: disable=too-few-public-methods,unused-imports,line-too-long,too-many-arguments,arguments-differ

"""
    CUSTOM WRITER CLASS FOR XERO DATA
"""
# import os
import re
from typing import Union, List, Any, Dict, Tuple, Optional
from sdc_dp_helpers.base_writers import BaseWriter


class XeroWriter(BaseWriter):
    """
    Xero writer class
    """
    def __init__(
        self,
        bucket: str,
        folder_path: str,
        destination: str,
        configs: Optional[Dict[str, Any]] = None,
        clear_destination: bool = False
        ):
        self.current_destination: Union[str, None] = None
        super().__init__(
            bucket=bucket,
            folder_path=folder_path,
            destination=destination,
            configs=configs,
            clear_destination=clear_destination,
        )

    def verify_data(
        self, payload: Dict[str, Any]
    ) -> Tuple[str, Union[List[Dict[Any, Any]], Dict[Any, Any], Any]]:
        """verifies data before writting to destination also designs the destination file path

        Args:
            payload (Dict[str, Any]): expecting a dictionary having data, date and dimension

        Raises:
            KeyError: if we do not find the exact keys we expect from the payload
            TypeError: if provided data object is not a list

        Returns:
            Tuple[str, Union[List[Dict[Any, Any]], Dict[Any, Any], Any]]: full destination path and
                                                                          data to be written
        """
        # confirm the payload keys are matching accurately with what is expected
        if not {"data", "date", "endpoint", "trackingCategoryId", "tenant_name"}.issubset(set(payload.keys())):
            raise KeyError("invalid payload expecting: data, date, endpoint, trackingCategoryId, tenant_name")

        if not isinstance(payload["data"], list):
            raise TypeError("invalid data passed: expected List[Dict[Any,Any]]")

        if not re.search(r"\d{4}\-\d{2}\-\d{2}", payload["date"]):
            raise ValueError(
                "Invalid date format for partitioning expected: 'YYYY-mm-dd'"
            )

        _data: list = payload["data"]
        _date: str = payload["date"].replace("-", "")
        _endpoint: str= payload['endpoint']
        _tracking_categoryid=payload['trackingCategoryId']
        _tenant_name = payload['tenant_name']
        if _tracking_categoryid:
            write_path = f"{self.folder_path}/{_endpoint}/{_tenant_name}/{_tracking_categoryid}/{_date}"
        else:
            write_path=f"{self.folder_path}/{_endpoint}/{_tenant_name}/{_date}"
        return write_path, _data
