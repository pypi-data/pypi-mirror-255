import time
import json
import os

from enum import Enum
from typing import Any, Dict, Optional
from logger.bcolors import BColors
from logger.tabular_log import format_as_table


class LogLevels(Enum):
    DEBUG = "DEBUG"
    WARN = "WARN"
    ERROR = "ERROR"


class Logger:
    def __init__(self, test_mode: bool = True) -> None:
        self.req_id: Optional[Any] = 1
        self.application_name: Optional[str] = "Unknown"
        self.application_version: Optional[str] = "0.0.0"
        self.environment: Optional[str] = "Development"
        self.environment_modifier: Optional[str] = None
        self.logs: list[Dict[str, Any]] = []
        self.warning_detected: bool = False
        self.error_detected: bool = False
        self.test_mode: bool = test_mode

    def set_mode(self, test_mode: bool) -> None:
        self.test_mode = test_mode

    def debug(self, msg: str, header: bool = False) -> None:
        color = BColors.HEADER if header else BColors.OK_BLUE
        self._write_log(level=LogLevels.DEBUG, msg=msg, clr=color)

    def warning(self, msg: str) -> None:
        self._write_log(level=LogLevels.WARN, msg=msg, clr=BColors.WARNING)
        self.warning_detected = True

    def error(self, msg: str) -> None:
        self._write_log(level=LogLevels.ERROR, msg=msg, clr=BColors.FAIL)
        self.error_detected = True

    def _write_log(self, level: LogLevels, msg: str, clr: str = BColors.OK_BLUE) -> None:
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        log_entry = self._create_log_entry(level.value, msg, timestamp)
        formatted_entry = self._format_log_entry(log_entry)
        print(f"{clr}{formatted_entry}{BColors.RESET}")
        with open('logfile.log', 'a', encoding="utf-8") as f:
            print(formatted_entry, file=f)
        self.logs.append(log_entry)

    def _create_log_entry(self, level: str, msg: str, timestamp: str) -> Dict[str, Any]:
        return {
            "timestamp": timestamp,
            "req_id": self.req_id,
            "level": level,
            "msg": msg,
            "appName": self.application_name,
            "appVersion": self.application_version,
            "env": self.environment,
            "envModifier": self.environment_modifier,
            "severity": level,
            "correlationId": self.req_id
        }

    def _format_log_entry(self, log_entry: Dict[str, Any]) -> str:
        if self.test_mode:
            return format_as_table(log_entry)
        else:
            return json.dumps(log_entry, separators=(',', ':'))
