import argparse
import copy
import json
from datetime import datetime


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def fetch_secret(hub, name: str, **kwargs):
    if kwargs.get("simulate", False):
        return "secret"
    return hub.read(name)


class Pipeline:
    def __init__(self, name: str, _for: str, **kwargs):
        self.name = name
        self._for = _for
        self.partition = None
        self.is_success = True
        self.data = None
        self.steps = []
        self.raise_exceptio = kwargs.get("raise_exception", False)

    def step(self, name: str, func) -> "Pipeline":
        if self.is_success is False:
            return self

        try:
            self.data = func(self)
            self.steps.append(
                {
                    "name": name,
                    "is_success": True,
                }
            )
        except Exception as e:
            self.is_success = False
            self.steps.append(
                {
                    "name": name,
                    "is_success": False,
                    "exception": e,
                }
            )
            if self.raise_exceptio:
                raise e
        return self

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "for": self._for,
            "partition": self.partition,
            "is_success": self.is_success,
            "data": self.data,
            "steps": self.steps,
        }

    @staticmethod
    def create_from(pipeline: "Pipeline") -> "Pipeline":
        p = Pipeline(
            name=pipeline.name,
            _for=pipeline._for,
            raise_exception=pipeline.raise_exceptio,
        )
        p.is_success = pipeline.is_success
        p.data = copy.copy(pipeline.data)
        p.steps = copy.copy(pipeline.steps)
        return p

    def __repr__(self) -> str:
        return f"Pipeline {json.dumps(self.__dict__, indent=2, default=str)})"


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        msg = f"Not a valid date: '{s}'."
        raise argparse.ArgumentTypeError(msg)  # noqa B904
