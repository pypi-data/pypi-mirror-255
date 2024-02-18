"""Serialization and Deserialization of Git Logs
"""

from typing import List, Any
import json
from datetime import datetime, date

from gitaudit.git.change_log_entry import ChangeLogEntry

COMMIT_DATE = "commit_date"


def entry_default_encoder(obj: Any) -> Any:
    """Default Encoder for non serializable datatypes

    Args:
        obj (Any): any data from dict

    Returns:
        Any: serialized dict entry
    """
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()

    return None


def entry_object_hook_decoder(obj: dict) -> dict:
    """Hook for object decoding. Decodes non-serializable datatypes

    Args:
        obj (dict): full object (dict)

    Returns:
        dict: Deserialized dict
    """
    if COMMIT_DATE in obj:
        obj[COMMIT_DATE] = datetime.fromisoformat(obj[COMMIT_DATE])
    return obj


def log_to_dict(log: List[ChangeLogEntry]) -> List[dict]:
    """ChangeLogEntry log to dict log

    Args:
        log (List[ChangeLogEntry]): Change log entry log
        exclude_defaults (bool, optional): Exlude value that have default values. Defaults to True.

    Returns:
        List[dict]: Dict log
    """
    return list(map(lambda x: x.to_save_dict(), log))


def log_to_json(log: List[ChangeLogEntry], indent=None):
    """Change log file to json string

    Args:
        log (List[ChangeLogEntry]): Change log entry log
        file_path (str): file path
    """
    log_dict = log_to_dict(log)

    return json.dumps(
        obj=log_dict,
        default=entry_default_encoder,
        indent=indent,
    )


def save_log_to_file(log: List[ChangeLogEntry], file_path: str, indent=None):
    """Save change log to file

    Args:
        log (List[ChangeLogEntry]): Change log entry log
        file_path (str): file path
    """
    log_dict = log_to_dict(log)

    with open(file_path, "w", encoding="utf-8") as file_p:
        json.dump(
            obj=log_dict,
            fp=file_p,
            default=entry_default_encoder,
            indent=indent,
        )


def load_log_from_file(file_path: str) -> List[ChangeLogEntry]:
    """Load change log from file

    Args:
        file_path (str): file path

    Returns:
        List[ChangeLogEntry]: Change log entry log
    """
    with open(file_path, "r", encoding="utf-8") as file_p:
        log_dict = json.load(
            fp=file_p,
            object_hook=entry_object_hook_decoder,
        )
    return ChangeLogEntry.list_from_objects(log_dict)
