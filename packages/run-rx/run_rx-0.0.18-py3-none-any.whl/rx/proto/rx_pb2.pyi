from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
EAGAIN: StatusCode
INVALID: StatusCode
MOVED: StatusCode
NOT_FOUND: StatusCode
OK: StatusCode
SUBSCRIPTION_REQUIRED: StatusCode
UNAUTHORIZED: StatusCode
UNKNOWN: StatusCode

class CommitFinishRequest(_message.Message):
    __slots__ = ["workspace_id"]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    def __init__(self, workspace_id: _Optional[str] = ...) -> None: ...

class CommitFinishResponse(_message.Message):
    __slots__ = ["image", "result"]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    image: Image
    result: Result
    def __init__(self, result: _Optional[_Union[Result, _Mapping]] = ..., image: _Optional[_Union[Image, _Mapping]] = ...) -> None: ...

class CommitStreamRequest(_message.Message):
    __slots__ = ["name", "organization", "workspace_id"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    organization: str
    workspace_id: str
    def __init__(self, workspace_id: _Optional[str] = ..., organization: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class CommitStreamResponse(_message.Message):
    __slots__ = ["push_progress", "result"]
    PUSH_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    push_progress: DockerImageProgress
    result: Result
    def __init__(self, result: _Optional[_Union[Result, _Mapping]] = ..., push_progress: _Optional[_Union[DockerImageProgress, _Mapping]] = ...) -> None: ...

class Delta(_message.Message):
    __slots__ = ["add_dir", "add_path", "remove_path"]
    ADD_DIR_FIELD_NUMBER: _ClassVar[int]
    ADD_PATH_FIELD_NUMBER: _ClassVar[int]
    REMOVE_PATH_FIELD_NUMBER: _ClassVar[int]
    add_dir: _containers.RepeatedScalarFieldContainer[str]
    add_path: _containers.RepeatedScalarFieldContainer[str]
    remove_path: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, add_path: _Optional[_Iterable[str]] = ..., add_dir: _Optional[_Iterable[str]] = ..., remove_path: _Optional[_Iterable[str]] = ...) -> None: ...

class DockerImageProgress(_message.Message):
    __slots__ = ["current", "id", "status", "total"]
    CURRENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    current: int
    id: str
    status: str
    total: int
    def __init__(self, id: _Optional[str] = ..., status: _Optional[str] = ..., total: _Optional[int] = ..., current: _Optional[int] = ...) -> None: ...

class Environment(_message.Message):
    __slots__ = ["image", "remote"]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    image: Image
    remote: Remote
    def __init__(self, remote: _Optional[_Union[Remote, _Mapping]] = ..., image: _Optional[_Union[Image, _Mapping]] = ...) -> None: ...

class ExecRequest(_message.Message):
    __slots__ = ["argv", "cwd", "rsync_source", "stdin", "workspace_id"]
    ARGV_FIELD_NUMBER: _ClassVar[int]
    CWD_FIELD_NUMBER: _ClassVar[int]
    RSYNC_SOURCE_FIELD_NUMBER: _ClassVar[int]
    STDIN_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    argv: _containers.RepeatedScalarFieldContainer[str]
    cwd: str
    rsync_source: RsyncSource
    stdin: bytes
    workspace_id: str
    def __init__(self, workspace_id: _Optional[str] = ..., argv: _Optional[_Iterable[str]] = ..., rsync_source: _Optional[_Union[RsyncSource, _Mapping]] = ..., cwd: _Optional[str] = ..., stdin: _Optional[bytes] = ...) -> None: ...

class ExecResponse(_message.Message):
    __slots__ = ["execution_id", "exit_code", "output_files", "result", "stderr", "stdout"]
    EXECUTION_ID_FIELD_NUMBER: _ClassVar[int]
    EXIT_CODE_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FILES_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    STDERR_FIELD_NUMBER: _ClassVar[int]
    STDOUT_FIELD_NUMBER: _ClassVar[int]
    execution_id: str
    exit_code: int
    output_files: _containers.RepeatedScalarFieldContainer[str]
    result: Result
    stderr: bytes
    stdout: bytes
    def __init__(self, result: _Optional[_Union[Result, _Mapping]] = ..., execution_id: _Optional[str] = ..., stdout: _Optional[bytes] = ..., stderr: _Optional[bytes] = ..., output_files: _Optional[_Iterable[str]] = ..., exit_code: _Optional[int] = ...) -> None: ...

class Execution(_message.Message):
    __slots__ = ["cmd", "end_ts", "start_ts"]
    CMD_FIELD_NUMBER: _ClassVar[int]
    END_TS_FIELD_NUMBER: _ClassVar[int]
    START_TS_FIELD_NUMBER: _ClassVar[int]
    cmd: str
    end_ts: int
    start_ts: int
    def __init__(self, cmd: _Optional[str] = ..., start_ts: _Optional[int] = ..., end_ts: _Optional[int] = ...) -> None: ...

class GeneratedConfig(_message.Message):
    __slots__ = ["config", "human_env_name", "image_decision", "unrecognized_tools"]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    HUMAN_ENV_NAME_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DECISION_FIELD_NUMBER: _ClassVar[int]
    UNRECOGNIZED_TOOLS_FIELD_NUMBER: _ClassVar[int]
    config: Environment
    human_env_name: str
    image_decision: str
    unrecognized_tools: _containers.RepeatedCompositeFieldContainer[Tool]
    def __init__(self, config: _Optional[_Union[Environment, _Mapping]] = ..., human_env_name: _Optional[str] = ..., image_decision: _Optional[str] = ..., unrecognized_tools: _Optional[_Iterable[_Union[Tool, _Mapping]]] = ...) -> None: ...

class GenericResponse(_message.Message):
    __slots__ = ["result"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: Result
    def __init__(self, result: _Optional[_Union[Result, _Mapping]] = ...) -> None: ...

class GetSubscribeInfoResponse(_message.Message):
    __slots__ = ["result", "subscribe_info"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBE_INFO_FIELD_NUMBER: _ClassVar[int]
    result: Result
    subscribe_info: SubscribeInfo
    def __init__(self, result: _Optional[_Union[Result, _Mapping]] = ..., subscribe_info: _Optional[_Union[SubscribeInfo, _Mapping]] = ...) -> None: ...

class GetUserResponse(_message.Message):
    __slots__ = ["result", "username"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    result: Result
    username: str
    def __init__(self, result: _Optional[_Union[Result, _Mapping]] = ..., username: _Optional[str] = ...) -> None: ...

class GetWorkspaceInfoRequest(_message.Message):
    __slots__ = ["workspace_id"]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    def __init__(self, workspace_id: _Optional[str] = ...) -> None: ...

class GetWorkspaceInfoResponse(_message.Message):
    __slots__ = ["environment", "history", "result", "state"]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    environment: Environment
    history: _containers.RepeatedCompositeFieldContainer[Execution]
    result: Result
    state: str
    def __init__(self, result: _Optional[_Union[Result, _Mapping]] = ..., state: _Optional[str] = ..., history: _Optional[_Iterable[_Union[Execution, _Mapping]]] = ..., environment: _Optional[_Union[Environment, _Mapping]] = ...) -> None: ...

class GitSource(_message.Message):
    __slots__ = ["commit", "url"]
    COMMIT_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    commit: str
    url: str
    def __init__(self, url: _Optional[str] = ..., commit: _Optional[str] = ...) -> None: ...

class Hardware(_message.Message):
    __slots__ = ["processor"]
    PROCESSOR_FIELD_NUMBER: _ClassVar[int]
    processor: str
    def __init__(self, processor: _Optional[str] = ...) -> None: ...

class Image(_message.Message):
    __slots__ = ["environment_variables", "ports", "registry", "repository", "tag"]
    class EnvironmentVariablesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ENVIRONMENT_VARIABLES_FIELD_NUMBER: _ClassVar[int]
    PORTS_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_FIELD_NUMBER: _ClassVar[int]
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    environment_variables: _containers.ScalarMap[str, str]
    ports: _containers.RepeatedScalarFieldContainer[int]
    registry: str
    repository: str
    tag: str
    def __init__(self, registry: _Optional[str] = ..., repository: _Optional[str] = ..., tag: _Optional[str] = ..., ports: _Optional[_Iterable[int]] = ..., environment_variables: _Optional[_Mapping[str, str]] = ...) -> None: ...

class InitRequest(_message.Message):
    __slots__ = ["git_source", "project_name", "rsync_source", "source_type", "target_env"]
    GIT_SOURCE_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    RSYNC_SOURCE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_ENV_FIELD_NUMBER: _ClassVar[int]
    git_source: GitSource
    project_name: str
    rsync_source: RsyncSource
    source_type: str
    target_env: Environment
    def __init__(self, project_name: _Optional[str] = ..., rsync_source: _Optional[_Union[RsyncSource, _Mapping]] = ..., target_env: _Optional[_Union[Environment, _Mapping]] = ..., source_type: _Optional[str] = ..., git_source: _Optional[_Union[GitSource, _Mapping]] = ...) -> None: ...

class InitResponse(_message.Message):
    __slots__ = ["result", "rsync_dest", "using_config", "worker_addr", "workspace_id"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    RSYNC_DEST_FIELD_NUMBER: _ClassVar[int]
    USING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    WORKER_ADDR_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    result: Result
    rsync_dest: RsyncDestination
    using_config: GeneratedConfig
    worker_addr: str
    workspace_id: str
    def __init__(self, result: _Optional[_Union[Result, _Mapping]] = ..., rsync_dest: _Optional[_Union[RsyncDestination, _Mapping]] = ..., worker_addr: _Optional[str] = ..., workspace_id: _Optional[str] = ..., using_config: _Optional[_Union[GeneratedConfig, _Mapping]] = ...) -> None: ...

class InstallDepsRequest(_message.Message):
    __slots__ = ["workspace_id"]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    def __init__(self, workspace_id: _Optional[str] = ...) -> None: ...

class InstallDepsResponse(_message.Message):
    __slots__ = ["result", "stdout"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    STDOUT_FIELD_NUMBER: _ClassVar[int]
    result: Result
    stdout: bytes
    def __init__(self, result: _Optional[_Union[Result, _Mapping]] = ..., stdout: _Optional[bytes] = ...) -> None: ...

class KillRequest(_message.Message):
    __slots__ = ["execution_id", "workspace_id"]
    EXECUTION_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    execution_id: str
    workspace_id: str
    def __init__(self, workspace_id: _Optional[str] = ..., execution_id: _Optional[str] = ...) -> None: ...

class Remote(_message.Message):
    __slots__ = ["hardware", "toolchain"]
    HARDWARE_FIELD_NUMBER: _ClassVar[int]
    TOOLCHAIN_FIELD_NUMBER: _ClassVar[int]
    hardware: Hardware
    toolchain: _containers.RepeatedCompositeFieldContainer[Tool]
    def __init__(self, hardware: _Optional[_Union[Hardware, _Mapping]] = ..., toolchain: _Optional[_Iterable[_Union[Tool, _Mapping]]] = ...) -> None: ...

class Result(_message.Message):
    __slots__ = ["code", "message"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: StatusCode
    message: str
    def __init__(self, code: _Optional[_Union[StatusCode, str]] = ..., message: _Optional[str] = ...) -> None: ...

class RsyncDestination(_message.Message):
    __slots__ = ["daemon_module"]
    DAEMON_MODULE_FIELD_NUMBER: _ClassVar[int]
    daemon_module: str
    def __init__(self, daemon_module: _Optional[str] = ...) -> None: ...

class RsyncSource(_message.Message):
    __slots__ = ["directory", "machine_id", "public_key"]
    DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    MACHINE_ID_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    directory: str
    machine_id: int
    public_key: bytes
    def __init__(self, machine_id: _Optional[int] = ..., directory: _Optional[str] = ..., public_key: _Optional[bytes] = ...) -> None: ...

class SetAclsRequest(_message.Message):
    __slots__ = ["add_reader", "add_writer", "resource_id", "resource_type", "visibility", "workspace_id"]
    ADD_READER_FIELD_NUMBER: _ClassVar[int]
    ADD_WRITER_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    add_reader: str
    add_writer: str
    resource_id: str
    resource_type: str
    visibility: str
    workspace_id: str
    def __init__(self, workspace_id: _Optional[str] = ..., resource_type: _Optional[str] = ..., resource_id: _Optional[str] = ..., visibility: _Optional[str] = ..., add_reader: _Optional[str] = ..., add_writer: _Optional[str] = ...) -> None: ...

class SetAclsResponse(_message.Message):
    __slots__ = ["readers", "result", "visibility"]
    READERS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    readers: _containers.RepeatedScalarFieldContainer[str]
    result: Result
    visibility: str
    def __init__(self, result: _Optional[_Union[Result, _Mapping]] = ..., visibility: _Optional[str] = ..., readers: _Optional[_Iterable[str]] = ...) -> None: ...

class SetUsernameRequest(_message.Message):
    __slots__ = ["username"]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class StopRequest(_message.Message):
    __slots__ = ["save", "workspace_id"]
    SAVE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    save: bool
    workspace_id: str
    def __init__(self, workspace_id: _Optional[str] = ..., save: bool = ...) -> None: ...

class StopResponse(_message.Message):
    __slots__ = ["image", "push_progress", "result"]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    PUSH_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    image: Image
    push_progress: DockerImageProgress
    result: Result
    def __init__(self, result: _Optional[_Union[Result, _Mapping]] = ..., push_progress: _Optional[_Union[DockerImageProgress, _Mapping]] = ..., image: _Optional[_Union[Image, _Mapping]] = ...) -> None: ...

class SubscribeInfo(_message.Message):
    __slots__ = ["payment_link"]
    PAYMENT_LINK_FIELD_NUMBER: _ClassVar[int]
    payment_link: str
    def __init__(self, payment_link: _Optional[str] = ...) -> None: ...

class Tool(_message.Message):
    __slots__ = ["name", "version"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    name: str
    version: str
    def __init__(self, name: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class UnfreezeRequest(_message.Message):
    __slots__ = ["workspace_id"]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    def __init__(self, workspace_id: _Optional[str] = ...) -> None: ...

class UnfreezeResponse(_message.Message):
    __slots__ = ["result", "worker_addr"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    WORKER_ADDR_FIELD_NUMBER: _ClassVar[int]
    result: Result
    worker_addr: str
    def __init__(self, result: _Optional[_Union[Result, _Mapping]] = ..., worker_addr: _Optional[str] = ...) -> None: ...

class WorkerInitRequest(_message.Message):
    __slots__ = ["workspace_id"]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    workspace_id: str
    def __init__(self, workspace_id: _Optional[str] = ...) -> None: ...

class WorkerInitResponse(_message.Message):
    __slots__ = ["pull_progress", "result"]
    PULL_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    pull_progress: DockerImageProgress
    result: Result
    def __init__(self, result: _Optional[_Union[Result, _Mapping]] = ..., pull_progress: _Optional[_Union[DockerImageProgress, _Mapping]] = ...) -> None: ...

class StatusCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
