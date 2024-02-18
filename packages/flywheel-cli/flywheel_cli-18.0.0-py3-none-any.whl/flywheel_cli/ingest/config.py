"""Provides config classes."""

import binascii
import json
import logging
import math
import os
import re
import socket
import tempfile
import zipfile
import zlib
from typing import Any, List, Optional, Type, TypeVar, Union, Dict

from pydantic import field_validator, model_validator, BaseModel, validator, Field
from pydantic.fields import ModelPrivateAttr
from ruamel.yaml import YAML, YAMLError

from .. import config as root_config
from .. import util, walker
from . import errors
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_CONFIG_PATH = os.path.join(root_config.CONFIG_DIRPATH, "cli.yml")
INGEST_CONFIG_PATH = os.path.join(root_config.CONFIG_DIRPATH, "ingest.yaml")
UUID_REGEX = (
    "[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}"
)
INGEST_OPERATION_REF_REGEX = re.compile(
    f"(?P<host>.*)/ingests/(?P<ingest_id>{UUID_REGEX})"
)
GROUP_ID_REGEX = re.compile("^[0-9a-z][0-9a-z.@_-]{0,30}[0-9a-z]$")
MAX_DEFAULT_JOBS = 4

log = logging.getLogger(__name__)


class BaseConfig(BaseSettings):
    """Base config"""

    model_config = SettingsConfigDict(extra="ignore")

    @field_validator("*", mode="before")
    @classmethod
    def validate_bool_values(cls, value, field):
        if cls.model_fields[field.field_name].annotation == bool:
            if isinstance(value, bool):
                return value
            val = str(value)
            if val == "1" or val.lower() == "true":
                return True
            return False
        return value


C = TypeVar("C", bound=BaseConfig)


def read_config_file(filepath):
    """Read data from config file"""
    if not os.path.exists(filepath):
        return None
    file_extension = filepath.rsplit(".", maxsplit=1)[-1]
    if file_extension in ("yml", "yaml"):
        try:
            yaml = YAML()
            with open(filepath, encoding="utf-8") as config_file:
                config = yaml.load(config_file)
        except (IOError, YAMLError) as exc:
            raise ConfigError(f"Unable to parse YAML config file: {exc}") from exc
    elif file_extension == "json":
        try:
            with open(filepath, encoding="utf-8") as json_file:
                config = json.load(json_file)
        except (IOError, json.decoder.JSONDecodeError) as exc:
            raise ConfigError(f"Unable to parse JSON file: {exc}") from exc
    else:
        raise ConfigError("Only YAML and JSON files are supported")
    return config


def load_config(cls: Type[C], args, defaults) -> C:
    """Load values from namespace and config file"""
    config_from_file: Dict[str, Any] = {}

    def load_value(snake_name):
        # try get the value from arguments first
        # then from the loaded config file
        # use any not-None value as valid value
        value = getattr(args, snake_name, None)
        default_value = defaults.get(snake_name)

        # we've removed the default value from the argparse argument,
        # so if the value is not-None the value was set on the command line
        if value is not None:
            return value

        value = config_from_file.get(snake_name)
        if value is not None:
            return value

        dash_name = snake_name.replace("_", "-")
        value = config_from_file.get(dash_name)
        if value is not None:
            return value

        return default_value

    config_filepath = getattr(args, "config_file", None) or DEFAULT_CONFIG_PATH
    config_filepath = os.path.expanduser(config_filepath)
    config_from_file = {}
    if not getattr(args, "no_config", None):
        config_from_file = read_config_file(config_filepath) or {}

    values = {}
    for name, val in cls.model_fields.items():
        snake_name = name
        value = load_value(snake_name)
        # only add values which are not None to let BaseSettings load them
        # from environment variables
        if value is not None:
            values[snake_name] = value

    return cls(**values)


class GeneralConfig(BaseConfig):
    """General configuration"""

    config_file: str = DEFAULT_CONFIG_PATH
    no_config: bool = False

    assume_yes: bool = False
    ca_certs: Optional[str] = None
    timezone: Optional[str] = None
    quiet: bool = False
    debug: bool = False
    verbose: bool = False

    @staticmethod
    def get_api_key():
        """Load api-key from config"""
        config = util.load_auth_config()
        if not config and config.get("key"):
            raise Exception("Not logged in, please login using `fw login`")
        return config["key"]

    def configure_ca_certs(self):
        """Configure ca-certs"""
        if self.ca_certs is not None:
            # Monkey patch certifi.where()
            import certifi

            certifi.where = lambda: self.ca_certs  # type: ignore

    def configure_timezone(self):
        """Configure timezone"""
        if self.timezone is not None:
            # Validate the timezone string
            import flywheel_migration
            import pytz

            try:
                tz = pytz.timezone(self.timezone)
            except pytz.exceptions.UnknownTimeZoneError as exc:
                raise ConfigError(f"Unknown timezone: {self.timezone}") from exc

            # Update the default timezone for flywheel_migration and util
            util.DEFAULT_TZ = tz
            flywheel_migration.util.DEFAULT_TZ = tz

            # Also set in the environment
            os.environ["TZ"] = self.timezone

    def startup_initialize(self):
        """Execute configure methods, this should be only called once, when cli
        starts."""
        if os.environ.get("FW_DISABLE_LOGS") != "1":
            root_config.Config.configure_logging(self)
        self.configure_ca_certs()
        self.configure_timezone()

    @field_validator("config_file")
    @classmethod
    def validate_config_file(cls, val):
        """Validate that config_file exists"""
        if val:
            if val != DEFAULT_CONFIG_PATH and not os.path.exists(val):
                raise ConfigError(f"The config file path '{val}' does not exist")
        return val

    @model_validator(mode="before")
    @classmethod
    def validate_mutually_exclusive(cls, values):
        """Validate exclusive groups"""
        if values.get("config_file", False) and values.get("no_config", False):
            raise ValueError("--config-file not allowed with argument --no-config")
        if values.get("debug", False) and values.get("quiet", False):
            raise ValueError("--debug not allowed with argument --quiet")

        return values


class ManageConfig(BaseConfig):
    """Manage ingest configuration"""

    ingest_url: Optional[Union[str, dict]] = None

    @property
    def cluster(self):
        """Cluster"""
        return self.ingest_url.get("cluster")

    @property
    def ingest_id(self):
        """Ingest id"""
        return self.ingest_url.get("ingest_id")

    @field_validator("ingest_url", mode="before")
    @classmethod
    def validate_ingest_url(cls, val):
        """Get the ingest operation url from the config file if not provided."""
        ingest_url = val
        if not ingest_url:
            try:
                config = read_config_file(os.path.expanduser(INGEST_CONFIG_PATH)) or {}
            except ConfigError:
                ingest_url = None
            else:
                ingest_url = config.get("ingest_operation_url")
        if not ingest_url:
            raise ValueError(
                "Couldn't determine the ingest URL, probably it was started on a "
                "different machine or by a different user. Please specify the ingest "
                "URL as a positional argument."
            )
        if isinstance(ingest_url, dict):
            if "cluster" not in ingest_url or "ingest_id" not in ingest_url:
                raise ValueError(
                    "'ingest_url' does not contain 'cluster' and/or 'ingest_id'"
                )
            return ingest_url
        match = INGEST_OPERATION_REF_REGEX.match(ingest_url)
        if not match:
            raise ValueError(
                "The provided url should have the following format: "
                "<cluster_url>/ingests/<ingest_id>"
            )
        return {
            "cluster": match.group("host"),
            "ingest_id": match.group("ingest_id"),
        }


class ClusterConfig(BaseConfig):
    """Cluster ingest config"""

    cluster: Optional[str] = None
    follow: bool = False

    def save_ingest_operation_url(self, ingest_id):
        """Save ingest operation url to the ingest config file.
        It makes possible to use the ingest manager subcommand like `ingest follow`
        without parameters.
        """
        if not self.cluster:
            raise ConfigError(
                "Saving ingest operation url only supported when using ingest cluster"
            )
        # Ensure directory exists
        config_dir = os.path.dirname(INGEST_CONFIG_PATH)
        os.makedirs(config_dir, exist_ok=True)
        ingest_operation_url = f"{self.cluster}/ingests/{ingest_id}"
        with open(INGEST_CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml = YAML()
            yaml.dump({"ingest_operation_url": ingest_operation_url}, f)
        return ingest_operation_url


class SubjectConfig(BaseModel):
    """Subject configuration schema"""

    code_serial: int = 0
    code_format: str
    map_keys: List[str]


class IngestConfig(BaseConfig):
    """Ingest configuration"""

    src_fs: str
    symlinks: bool = False
    include_dirs: List[str] = []
    exclude_dirs: List[str] = []
    include: List[str] = []
    exclude: List[str] = []
    compression_level: int = zlib.Z_DEFAULT_COMPRESSION
    ignore_unknown_tags: bool = False
    encodings: List[str] = []
    de_identify: bool = False
    deid_profile: str = "minimal"
    deid_profiles: List[Any] = []
    skip_existing: bool = False
    no_audit_log: bool = False
    subject_config: Optional[SubjectConfig] = None
    load_subjects: Optional[str] = None
    max_retries: int = 3
    assume_yes: bool = False
    detect_duplicates: bool = False
    copy_duplicates: bool = False
    require_project: bool = False
    fw_walker_api_key: Optional[str] = None
    enable_project_files: bool = False
    detect_duplicates_project: List[str] = []
    force_scan: bool = False
    detect_duplicates_override: List[str] = []
    repack: bool = False
    zip_single_dicom: bool = False
    strict_uid: bool = False

    # resolved project ids
    detect_duplicates_project_ids: List[str] = []
    deid_is_from_server: bool = False

    @field_validator("compression_level")
    @classmethod
    def validate_compression_level(cls, val):
        """Validate compression level."""
        # valid -1 - 9
        if val not in range(-1, 10):
            raise ValueError("Compression level needs to be between 0-9")
        return val

    @model_validator(mode="after")
    @classmethod
    def validate_detect_duplicates(cls, values):
        """Set detect_duplicates flag if copy_duplicates is set"""
        if values.copy_duplicates or values.detect_duplicates_project:
            values.detect_duplicates = True

        if values.detect_duplicates_project_ids is None:
            values.detect_duplicates_project_ids = []

        if values.repack:
            values.include = ["*.zip", "*.ZIP"]

        return values

    @field_validator("detect_duplicates_override")
    @classmethod
    def validate_detect_duplicates_override(cls, val):
        """Check if override error codes exist."""
        for error_code in val:
            if not error_code.startswith("DD"):
                raise ValueError("Detect duplicate error codes starts with DD")
            for errors_item in errors.__dict__.values():
                if (
                    hasattr(errors_item, "code")
                    and isinstance(errors_item.code, str)
                    and errors_item.code.startswith("DD")
                    and error_code == errors_item.code
                ):
                    break
            else:
                raise ValueError(f"{error_code} doesn't exist.")
        return val

    def create_walker(self, **kwargs):
        """Create walker"""
        for key in ("include", "exclude", "include_dirs", "exclude_dirs"):
            kwargs[key] = util.merge_lists(kwargs.get(key, []), getattr(self, key, []))
        kwargs.setdefault("follow_symlinks", self.symlinks)

        kwargs["fw_walker_api_key"] = self.fw_walker_api_key
        kwargs["zip_walker"] = self.repack

        return walker.create_walker(self.src_fs, **kwargs)

    def register_encoding_aliases(self):
        """Register common encoding aliases"""
        import encodings

        for encoding_spec in self.encodings:
            key, _, value = encoding_spec.partition("=")
            encodings.aliases.aliases[key.strip().lower()] = value.strip().lower()

    def get_compression_type(self):
        """Returns compression type"""
        if self.compression_level == 0:
            return zipfile.ZIP_STORED
        return zipfile.ZIP_DEFLATED


class ReporterConfig(BaseConfig):
    """Follow ingest configuration"""

    assume_yes: bool = False
    verbose: bool = False
    refresh_interval: int = 10
    save_audit_logs: Optional[str] = None
    save_deid_logs: Optional[str] = None
    save_subjects: Optional[str] = None


class WorkerConfig(BaseConfig):
    """Ingest worker configuration"""

    db_url: Optional[str] = None
    sleep_time: int = 1
    jobs: int = max(
        1, min(math.floor(os.cpu_count() / 2), MAX_DEFAULT_JOBS)  # type: ignore
    )
    max_tempfile: int = 50
    buffer_size: int = 65536
    worker_name: str = socket.gethostname()
    # kubernetes default termination grace period is 30 seconds
    # keep it lower in the worker to have time to set ingest/task status
    # if it can't complete the task in time
    termination_grace_period: int = 15

    @field_validator("db_url")
    @classmethod
    def db_required(cls, val):
        """Validate that database connection string is not None"""
        if not val:
            random_part = binascii.hexlify(os.urandom(16)).decode("utf-8")
            filepath = os.path.join(
                tempfile.gettempdir(), f"flywheel_cli_ingest_{random_part}.db"
            )
            return f"sqlite:///{filepath}"
        return val


# Ingest strategy configs


class DicomConfig(BaseConfig):
    """Config class for dicom ingest strategy"""

    strategy_name: str = Field("dicom")
    group: str
    project: str
    subject: Optional[str] = None
    session: Optional[str] = None

    @field_validator("strategy_name")
    @classmethod
    def validate_strategy_name(cls, val):
        """Validate strategy name"""
        if val != "dicom":
            raise ValueError("Invalid strategy name")
        return val

    @field_validator("group")
    @classmethod
    def validate_group_id(cls, val):
        """Validate group id"""
        try:
            util.group_id(val)
        except TypeError as exc:
            raise ValueError(exc)
        return val


class FolderConfig(BaseConfig):
    """Config class for folder import strategy"""

    strategy_name: str = "folder"
    group: Optional[str] = None
    project: Optional[str] = None
    dicom: str = "dicom"
    pack_acquisitions: Optional[bool] = None
    root_dirs: int = 0
    no_subjects: bool = False
    no_sessions: bool = False
    group_override: Optional[str] = None
    project_override: Optional[str] = None

    @field_validator("strategy_name")
    @classmethod
    def validate_strategy_name(cls, val):
        """Validate strategy name"""
        if val != "folder":
            raise ValueError("Invalid strategy name")
        return val

    @field_validator("group")
    @classmethod
    def validate_group(cls, val):
        """Validate group id"""
        if val:
            return util.group_id(val)
        return val

    @field_validator("group_override")
    @classmethod
    def validate_group_override(cls, val):
        """Validate group id"""
        if val:
            return util.group_id(val)
        return val

    @model_validator(mode="before")
    @classmethod
    def validate_mutually_exclusive(cls, values):
        """Validate exclusive groups"""
        if values.get("no_subjects", False) and values.get("no_sessions", False):
            raise ValueError("--no-subjects not allowed with argument --no-sessions")

        values.setdefault("group_override", values.get("group"))
        values.setdefault("project_override", values.get("project"))

        return values


class TemplateConfig(BaseConfig):
    """Template ingest strategy configuration"""

    strategy_name: str = "template"
    template: Union[str, List]
    group: Optional[str] = None
    project: Optional[str] = None
    no_subjects: bool = False
    no_sessions: bool = False
    group_override: Optional[str] = None
    project_override: Optional[str] = None
    set_var: List[str] = []

    @field_validator("strategy_name")
    @classmethod
    def validate_strategy_name(cls, val):
        """Validate strategy name"""
        if val != "template":
            raise ValueError("Invalid strategy name")
        return val

    @field_validator("group")
    @classmethod
    def validate_group(cls, val):
        """Validate group id"""
        if val:
            return util.group_id(val)
        return val

    @field_validator("group_override")
    @classmethod
    def validate_group_override(cls, val):
        """Validate group id"""
        if val:
            return util.group_id(val)
        return val

    @field_validator("template")
    @classmethod
    def validate_template(cls, val):
        """Load template from file if a valid path was passed"""
        if isinstance(val, str) and os.path.isfile(val):
            val = read_config_file(val)

        return val

    @model_validator(mode="before")
    @classmethod
    def validate_mutually_exclusive(cls, values):
        """Validate exclusive groups"""
        if values.get("no_subjects", False) and values.get("no_sessions", False):
            raise ValueError("--no-subjects not allowed with argument --no-sessions")

        values.setdefault("group_override", values.get("group"))
        values.setdefault("project_override", values.get("project"))

        return values


class ProjectConfig(BaseConfig):
    """Project ingest strategy configuration"""

    # src_fs is only a technical field here, to be able to create default group/project
    # see in default_group_project class method.
    src_fs: str
    strategy_name: str = "project"
    group: str
    project: str
    no_metadata: bool = False
    deid_log_exists: bool = False

    @model_validator(mode="before")
    @classmethod
    @classmethod
    def default_group_project(cls, values):
        """Set default group/project derived from the source path."""
        if not values.get("src_fs"):
            raise ValueError("src_fs can't be None")

        src_group, src_project = values.get("src_fs").replace("fw://", "").split("/")
        if not values.get("group"):
            values["group"] = src_group

        if not values.get("project"):
            values["project"] = src_project

        return values

    @field_validator("group")
    @classmethod
    @classmethod
    def validate_group(cls, val):
        """Validate group id"""
        if val:
            return util.group_id(val)
        return val


class BidsConfig(BaseConfig):
    """Config class for dicom ingest strategy"""

    strategy_name: str = "bids"
    folder: str
    group: str
    project: Optional[str] = None
    subject: Optional[str] = None
    session: Optional[str] = None

    @field_validator("group")
    @classmethod
    def validate_group_id(cls, val):
        """Validate group id"""
        try:
            util.group_id(val)
        except TypeError as exc:
            raise ValueError(exc)
        return val


StrategyConfig = Union[DicomConfig, FolderConfig, TemplateConfig, ProjectConfig]


class ConfigError(ValueError):
    """ConfigError"""
