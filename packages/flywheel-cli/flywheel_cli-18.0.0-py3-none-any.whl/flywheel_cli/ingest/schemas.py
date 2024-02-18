"""Pydantic ingest input and output schemas"""

import datetime
import enum
import typing as t
import uuid

from pydantic import (
    field_validator,
    model_validator,
    ConfigDict,
    BaseModel,
    Field,
    root_validator,
)

from .. import util
from . import config as cfg


class Schema(BaseModel):
    """Common base configured to play nice with sqlalchemy"""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class Enum(enum.Enum):
    """Extended Enum with easy item lookup by instance, name or value"""

    @classmethod
    def get_item(cls, info: t.Any) -> "Enum":
        """Return enum item for given instance, name or value"""
        for item in cls:
            if info in (item, item.name, item.value):
                return item
        raise ValueError(f"Invalid {cls.__name__} {info}")

    @classmethod
    def has_item(cls, info: t.Any) -> bool:
        """Return True if info is a valid enum instance, name or value"""
        try:
            cls.get_item(info)
        except ValueError:
            return False
        return True


class Status(Enum):
    """Status enum with transition validation and terminality check"""

    @staticmethod
    def transitions():
        """Define allowed status transitions"""
        raise NotImplementedError

    @classmethod
    def validate_transition(cls, old, new) -> None:
        """Raise ValueError if old -> new is not a valid status transition"""
        old = cls.get_item(old).value if old else None
        new = cls.get_item(new).value
        if old and new not in cls.transitions()[old]:
            # NOTE allowing any status transition from old=None facilitates tests
            raise ValueError(f"Invalid {cls.__name__} transition {old} -> {new}")

    @classmethod
    def is_terminal(cls, info) -> bool:
        """Return True if 'has_item(info)' and the status has no transitions"""
        if cls.has_item(info):
            status = cls.get_item(info).value
            return cls.transitions()[status] == set()
        return False


# Ingests


class IngestStatus(str, Status):
    """Ingest status"""

    created = "created"
    configuring = "configuring"
    scanning = "scanning"
    resolving = "resolving"
    detecting_duplicates = "detecting_duplicates"
    in_review = "in_review"
    preparing = "preparing"
    preparing_sidecar = "preparing_sidecar"
    uploading = "uploading"
    finalizing = "finalizing"
    finished = "finished"
    failed = "failed"
    aborting = "aborting"
    aborted = "aborted"

    @staticmethod
    def transitions():
        """Define allowed transitions"""
        return {
            None: {"created"},
            "created": {"configuring", "aborting"},
            "configuring": {"scanning", "failed", "aborting"},
            "scanning": {"resolving", "failed", "aborting"},
            "resolving": {"detecting_duplicates", "in_review", "failed", "aborting"},
            "detecting_duplicates": {"in_review", "failed", "aborting"},
            "in_review": {"preparing", "aborting"},
            "preparing": {"uploading", "preparing_sidecar", "failed", "aborting"},
            "preparing_sidecar": {"uploading", "failed", "aborting"},
            "uploading": {"finalizing", "failed", "aborting"},
            "finalizing": {"finished", "failed", "aborting"},
            "finished": set(),
            "failed": set(),
            "aborting": {"aborted", "failed"},
            "aborted": set(),
        }


class IngestInAPI(Schema):
    """Ingest input schema for API"""

    config: cfg.IngestConfig
    strategy_config: cfg.StrategyConfig


class BaseIngestOut(Schema):
    """Base ingest output schema"""

    id: t.Optional[uuid.UUID] = None
    label: t.Optional[str] = None
    fw_host: t.Optional[str] = None
    fw_user: t.Optional[str] = None
    config: t.Optional[cfg.IngestConfig] = None
    strategy_config: t.Optional[cfg.StrategyConfig] = None
    status: t.Optional[IngestStatus] = None
    history: t.Optional[t.List[t.Tuple[IngestStatus, int]]] = None
    created: t.Optional[datetime.datetime] = None


class IngestOutAPI(BaseIngestOut):
    """Ingest output schema for API"""


class IngestOut(BaseIngestOut):
    """Ingest output schema w/ api-key"""

    api_key: str


# Tasks


class TaskType(str, Enum):
    """Task type enum"""

    configure = "configure"
    scan = "scan"
    extract_uid = "extract_uid"
    resolve = "resolve"  # singleton
    detect_duplicates = "detect_duplicates"  # singleton
    prepare_sidecar = "prepare_sidecar"  # singleton
    prepare = "prepare"  # singleton
    upload = "upload"
    finalize = "finalize"  # singleton

    @classmethod
    def ingest_status(cls, info) -> IngestStatus:
        """Get the associated ingest status of a task type"""
        status = cls.get_item(info).value
        task_type_ingest_status_map = {
            "configure": IngestStatus.configuring,
            "scan": IngestStatus.scanning,
            "extract_uid": IngestStatus.scanning,
            "resolve": IngestStatus.resolving,
            "detect_duplicates": IngestStatus.detecting_duplicates,
            "prepare_sidecar": IngestStatus.preparing_sidecar,
            "prepare": IngestStatus.preparing,
            "upload": IngestStatus.uploading,
            "finalize": IngestStatus.finalizing,
        }
        return task_type_ingest_status_map[status]


class TaskStatus(str, Status):
    """Task status enum"""

    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"

    @staticmethod
    def transitions():
        """Define allowed transitions"""
        return {
            None: {"pending"},
            "pending": {"running", "canceled"},  # cancel via ingest fail/abort
            "running": {"completed", "pending", "failed"},  # retry to pending
            "completed": set(),
            "failed": set(),  # NOTE this will get trickier with user retries
            "canceled": set(),
        }


class TaskIn(Schema):
    """Task input schema"""

    type: TaskType
    item_id: t.Optional[uuid.UUID] = None
    context: t.Optional[dict] = None
    status: TaskStatus = TaskStatus.pending


class TaskOut(TaskIn):
    """Task output schema"""

    id: uuid.UUID
    ingest_id: uuid.UUID
    status: TaskStatus
    history: t.List[t.Tuple[TaskStatus, int]]
    worker: t.Optional[str] = None
    error: t.Optional[str] = None
    created: datetime.datetime
    retries: int
    completed: int = 0  # completed work unit
    total: int = 0  # total number of work unit


# Containers


class SourceContainerContext(Schema):
    """Source container context schema, generally comes from the template/cli
    args/scanners"""

    id: t.Optional[str] = Field(None, alias="_id")
    label: t.Optional[str] = None
    info: t.Optional[t.Dict[str, t.Any]] = None
    uid: t.Optional[str] = None
    timestamp: t.Optional[datetime.datetime] = None
    timezone: t.Optional[str] = None

    age: t.Optional[int] = None
    weight: t.Optional[float] = None
    operator: t.Optional[str] = None
    cohort: t.Optional[str] = None
    mlset: t.Optional[str] = None
    ethnicity: t.Optional[str] = None
    firstname: t.Optional[str] = None
    lastname: t.Optional[str] = None
    race: t.Optional[str] = None
    sex: t.Optional[str] = None
    type: t.Optional[str] = None
    tags: t.Optional[t.List[str]] = None
    species: t.Optional[str] = None
    strain: t.Optional[str] = None

    @model_validator(mode="after")
    def id_or_label_provided(cls, values):
        """Verify that id or label is specified"""
        if not (values.id or values.label):
            raise ValueError("_id or label is required field")
        return values

    @field_validator("label")
    @classmethod
    def sanitize_label(cls, v):
        """Sanitize label validator"""
        if not v:
            return v
        return util.sanitize_filename(v)


class SourceSubjectContext(SourceContainerContext):
    """Source subject context schema, generally comes from the template/cli
    args/scanners"""

    @model_validator(mode="before")
    @classmethod
    def id_or_label_provided(cls, values):
        """Verify that id or label is specified"""
        if not (values.get("_id") or values.get("label")):
            raise ValueError(
                "_id or label is required field. Use the --subject flag to specify "
                "label"
            )
        return values


class SourceSessionContext(SourceContainerContext):
    """Source session context schema, generally comes from the template/cli
    args/scanners"""

    @model_validator(mode="before")
    @classmethod
    def id_or_label_provided(cls, values):
        """Verify that id or label is specified"""
        if not (values.get("_id") or values.get("label")):
            raise ValueError(
                "_id or label is required field. Use the --session flag to specify "
                "label"
            )
        return values


class DestinationContainerContext(Schema):
    """Destination container context, represents an existing container in flywheel"""

    id: str = Field(..., alias="_id")
    label: t.Optional[str] = None
    info: t.Optional[t.Dict[str, t.Any]] = None
    uid: t.Optional[str] = None
    files: t.List[str] = []


class ContainerLevel(int, Enum):
    """Container level enum (int for simple ordering)"""

    group = 0
    project = 1
    subject = 2
    session = 3
    acquisition = 4


class Container(Schema):
    """Container schema"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    parent_id: t.Optional[uuid.UUID] = None
    path: str
    level: ContainerLevel
    src_context: SourceContainerContext
    dst_context: t.Optional[DestinationContainerContext] = None
    dst_path: t.Optional[str] = None
    existing: t.Optional[bool] = False
    error: t.Optional[bool] = False
    sidecar: t.Optional[bool] = False
    files_cnt: t.Optional[int] = None
    bytes_sum: t.Optional[int] = None
    dd_files: t.Optional[t.Dict[str, t.List[str]]] = None


# Items


class ItemType(str, Enum):
    """Ingest item type enum"""

    file = "file"
    packfile = "packfile"


class Error(Schema):
    """Item error schema"""

    item_id: t.Optional[uuid.UUID] = None
    task_id: t.Optional[uuid.UUID] = None
    filepath: t.Optional[str] = None
    code: str
    message: t.Optional[str] = None
    conflict_path: t.Optional[str] = None


class PackfileContext(Schema):
    """Packfile context schema"""

    type: str
    name: t.Optional[str] = None
    flatten: bool = False
    zip: bool = True


class ItemContext(Schema):
    """Item context schema"""

    group: SourceContainerContext
    project: SourceContainerContext
    subject: t.Optional[SourceSubjectContext] = None
    session: t.Optional[SourceSessionContext] = None
    acquisition: t.Optional[SourceContainerContext] = None
    packfile: t.Optional[PackfileContext] = None


class Item(Schema):
    """Item schema"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    container_id: t.Optional[uuid.UUID] = None
    dir: str
    type: ItemType
    files: t.List[str]
    filename: str
    safe_filename: t.Optional[str] = None
    files_cnt: int
    bytes_sum: int
    context: ItemContext
    existing: t.Optional[bool] = False
    skipped: t.Optional[bool] = False
    fw_metadata: t.Optional[t.Dict[str, t.Any]] = None
    existing_in: t.Optional[str] = None

    @model_validator(mode="after")
    def validate_item_type(cls, values):
        """
        Validate that the item type is correct:
            - if files list contains more than one file the type has to be packfile
        """
        if len(values.files) > 1 and values.type == ItemType.file:
            raise ValueError("Found multiple files, type needs to be packfile")
        return values

    @field_validator("filename")
    @classmethod
    def sanitize_filename(cls, v):
        """Sanitize filename validator"""
        return util.sanitize_filename(v)


class FWContainerMetadata(Schema):
    """FWContainerMetadata class"""

    path: str
    content: t.Dict[str, t.Any]


class ItemWithContainerPath(Schema):
    """Ingest item with container path for detect duplicates task"""

    id: uuid.UUID
    dir: str
    filename: str
    existing: t.Optional[bool] = None
    existing_in: t.Optional[str] = None
    container_path: t.Optional[str] = None


class ItemWithErrorCount(Schema):
    """Ingest item with error count for prepare task"""

    id: uuid.UUID
    existing: t.Optional[bool] = None
    error_cnt: int = 0
    container_error: t.Optional[bool] = None
    container_path: t.Optional[str] = None


# Ingest stats


class StageCount(Schema):
    """Work unit completed/total counts"""

    completed: int = 0
    total: int = 0


class StageProgress(Schema):
    """Work unit counts by ingest status"""

    configuring: StageCount = StageCount()
    scanning: StageCount = StageCount()
    resolving: StageCount = StageCount()
    detecting_duplicates: StageCount = StageCount()
    preparing: StageCount = StageCount()
    preparing_sidecar: StageCount = StageCount()
    uploading: StageCount = StageCount()
    finalizing: StageCount = StageCount()


class StatusCount(Schema):
    """Counts by status"""

    scanned: int = 0
    pending: int = 0
    running: int = 0
    failed: int = 0
    canceled: int = 0
    completed: int = 0
    skipped: int = 0
    finished: int = 0
    total: int = 0


class Progress(Schema):
    """Ingest progress with scan task and import- item/file/byte counts by status"""

    scans: StatusCount = StatusCount()
    items: StatusCount = StatusCount()
    files: StatusCount = StatusCount()
    bytes: StatusCount = StatusCount()
    stages: StageProgress = StageProgress()


class ErrorSummary(Schema):
    """Ingest error summary"""

    code: str
    message: str
    description: t.Optional[str] = None
    count: int


class Summary(Schema):
    """Ingest scan summary with hierarchy node and file counts"""

    groups: int = 0
    projects: int = 0
    subjects: int = 0
    sessions: int = 0
    acquisitions: int = 0
    files: int = 0
    packfiles: int = 0
    warnings: t.Optional[t.List[ErrorSummary]] = None
    errors: t.Optional[t.List[ErrorSummary]] = None


class TaskError(Schema):
    """Ingest task error"""

    task: uuid.UUID
    type: TaskType
    code: str
    message: str


class Report(Schema):
    """Final ingest report with status, elapsed times and list of errors"""

    status: IngestStatus
    elapsed: t.Dict[IngestStatus, int]
    errors: t.List[TaskError]
    warnings: t.List[TaskError]


# Review


class ReviewChange(Schema):
    """Review change"""

    path: str
    skip: t.Optional[bool] = None
    context: t.Optional[dict] = None


ReviewIn = t.List[ReviewChange]


# Logs


class AuditLogOut(Schema):
    """Audit log output schema"""

    id: uuid.UUID
    dir: str
    filename: str
    src_path: t.Optional[str] = None
    dst_path: t.Optional[str] = None
    existing: t.Optional[bool] = None
    skipped: t.Optional[bool] = None
    files_cnt: t.Optional[int] = None
    status: t.Optional[TaskStatus] = None
    error_code: t.Optional[str] = None
    error_message: t.Optional[str] = None
    container_error: t.Optional[bool] = None
    conflict_path: t.Optional[str] = None


class DeidLogIn(Schema):
    """Deid log input schema"""

    src_path: str
    tags_before: dict
    tags_after: dict


class DeidLogOut(DeidLogIn):
    """De-id log output schema"""

    id: uuid.UUID
    created: datetime.datetime


class SubjectOut(Schema):
    """Subject output schema"""

    code: str
    map_values: t.List[str]


# UID


class UIDIn(Schema):
    """UID input schema"""

    item_id: uuid.UUID
    filename: str
    study_instance_uid: str
    series_instance_uid: str
    sop_instance_uid: str
    acquisition_number: t.Optional[str] = None
    session_container_id: t.Optional[uuid.UUID] = None
    acquisition_container_id: t.Optional[uuid.UUID] = None

    @root_validator(pre=True)
    @classmethod
    def uid_validator(cls, values):
        if not isinstance(values, dict):
            values = values.__dict__
        acq = values.pop("acquisition_number", None)
        if acq:
            try:
                values["acquisition_number"] = str(int(str(acq)))
            except ValueError:
                values["acquisition_number"] = "0"
        return values


class UIDOut(UIDIn):
    """UID output schema"""

    id: uuid.UUID


class ItemWithUIDs(Schema):
    """Ingest item with UIDs"""

    item: Item
    uids: t.List[UIDIn]


class DetectDuplicateItem(Schema):
    """DetectDuplicateItem used in find_all_item_with_uid to return lightweight
    objects"""

    id: uuid.UUID
    item_id: uuid.UUID
    session_container_id: t.Optional[uuid.UUID] = None
    acquisition_container_id: t.Optional[uuid.UUID] = None
    study_instance_uid: t.Optional[str] = None
    series_instance_uid: t.Optional[str] = None


# Others


class ReportETA(Schema):
    """ETA report schema"""

    eta: int
    report_time: int
    finished: int
    total: int


class ContainerID(Schema):
    """Container ID for Item"""

    id: uuid.UUID
    container_id: uuid.UUID


class TaskStat(Schema):
    """TaskStat"""

    type: t.Optional[str] = None
    ingest_id: t.Optional[uuid.UUID] = None
    id: t.Optional[uuid.UUID] = None
    pending: int = 0
    running: int = 0
    failed: int = 0
    canceled: int = 0
    completed: int = 0
    total: int = 0


class ItemStat(Schema):
    """ItemStat"""

    type: t.Optional[str] = None
    ingest_id: t.Optional[uuid.UUID] = None
    id: t.Optional[uuid.UUID] = None
    total: int = 0
    completed: int = 0
    skipped: int = 0
    bytes_sum: int = 0
