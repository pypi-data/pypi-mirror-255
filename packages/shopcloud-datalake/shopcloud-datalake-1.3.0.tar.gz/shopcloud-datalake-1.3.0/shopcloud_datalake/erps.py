import concurrent.futures
import io
import json
from abc import ABC, abstractmethod
from typing import Tuple

import pandas as pd
import requests
import urllib3
from tqdm import tqdm

from . import managers

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class APIError(Exception):
    def __init__(self, response: requests.Response, **kwargs) -> None:
        self.data = kwargs.get("data")
        self.response = response
        super().__init__(response.text)

    def __repr__(self) -> str:
        data = "" if self.data is None else f" {self.data}"
        return f"APIError {self.response.status_code} {self.response.text}{data}"


class SQLError(Exception):
    def __init__(self, data: dict) -> None:
        self.data = data
        super().__init__()


class AbstractErpAdapter(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def fetch(self, query: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def paginated(
        self, query: str, order_by: str, **kwargs
    ) -> Tuple[pd.DataFrame, int]:
        pass


class SageAdapter(AbstractErpAdapter):
    NAME = "sage"

    def __init__(self, endpoint: str, api_token: str, **kwargs) -> None:
        self.endpoint = endpoint
        self.api_token = api_token
        self.max_workers = kwargs.get("max_workers", 4)
        self.timeout = 120
        self.limit = kwargs.get("limit")
        if self.limit is None:
            self.limit = 5000
        else:
            self.limit = int(self.limit)

    def fetch(self, query: str, **kwargs) -> pd.DataFrame:
        data = json.dumps({"query": query})
        response = requests.post(
            url=f"https://{self.endpoint}/api/Sql",
            headers={
                "Authorization": f"Basic {self.api_token}",
                "Content-Type": "application/json; charset=utf-8",
                "X-Test-Type": kwargs.get("x_test_type", "sql"),
            },
            verify=False,
            data=data,
            timeout=self.timeout,
        )

        if not (200 <= response.status_code <= 299):
            raise APIError(response, data=data)

        content = response.content.decode("utf-8")
        if '{"error":' in content:
            data = json.loads(content)
            if isinstance(data, dict) and "error" in data:
                raise SQLError(data)

        try:
            return pd.read_csv(io.StringIO(content), sep=";", dtype="object")
        except pd.errors.EmptyDataError:
            return pd.DataFrame()

    def paginated(
        self, query: str, order_by: str, **kwargs
    ) -> Tuple[pd.DataFrame, int]:
        df = self.fetch(f"SELECT COUNT(*) AS total FROM ({query}) AS data")
        if df.empty:
            return df, 0
        total = int(df.iloc[0]["total"])

        pages = [
            f"SELECT * FROM ({query}) AS data ORDER BY {order_by} OFFSET {offset} ROWS FETCH NEXT {self.limit} ROWS ONLY"
            for offset in range(0, total, self.limit)
        ]
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            pages = list(
                tqdm(executor.map(self.fetch, pages), total=len(pages), disable=True)
            )
        df = pd.concat(pages)
        return df, total


class ErpAdapterManager(managers.AbstractAdapterManager):
    def get(self, name: str, **kwargs):
        a = self.datas.get(name)
        if a is not None:
            return a

        if name == SageAdapter.NAME:
            config = {
                **{
                    "request_page_limit": 5000,
                    "max_workers": 4,
                },
                **self.config,
            }
            endpoint = self.hub.read(
                "talk-point/app-shopcloud-analytics/erp/sage/endpoint"
            )
            api_token = self.hub.read(
                "talk-point/app-shopcloud-analytics/erp/sage/api-token"
            )
            a = SageAdapter(
                endpoint=endpoint,
                api_token=api_token,
                max_workers=config.get("max_workers", 4),
                limit=config.get("request_page_limit", 5000),
                debug=self.debug,
            )
            self.datas[name] = a
            return a
        else:
            raise NotImplementedError(f"Adapter {name} not implemented")
