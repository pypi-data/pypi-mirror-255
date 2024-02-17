"""CUSTOM MODULE TO WRITE ZOHO RECRUIT DATA"""
# pylint: disable=too-few-public-methods, too-many-arguments
from typing import Union, List, Any, Dict, Tuple, Optional
from sdc_dp_helpers.base_writers import BaseWriter


class OneSignalWriter(BaseWriter):
    """WRITER FOR ZOHO RECRUIT DATA"""

    def __init__(
        self,
        bucket: str,
        folder_path: str,
        destination: str,
        configs: Optional[Dict[str, Any]] = None,
        clear_destination: bool = False,
    ):
        self.success: List[bool] = []
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
        """
        if not {"data", "date"}.issubset(set(payload.keys())):
            raise KeyError("invalid payload expecting: data, date")

        if not isinstance(payload["data"], list):
            raise TypeError("invalid data passed: expected List[Dict[Any,Any]]")

        try:
            int(payload["date"])
        except ValueError as exc:
            raise ValueError(
                f"wrong date value expected integer: {payload['date']}"
            ) from exc

        data: list = payload["data"]
        date: str = payload["date"]
        base_path = self.folder_path.rsplit("/", maxsplit=1)[0]
        brand_name = self.folder_path.rsplit("/", maxsplit=1)[1]

        write_path: str = f"{base_path}/date={date}/brand={brand_name}/{date}"

        return write_path, data
