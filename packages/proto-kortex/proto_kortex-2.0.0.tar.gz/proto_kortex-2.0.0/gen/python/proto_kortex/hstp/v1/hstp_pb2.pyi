from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

COLLISION_STRATEGY_FAIL: CollisionStrategy
COLLISION_STRATEGY_FORCE_OVERWRITE: CollisionStrategy
COLLISION_STRATEGY_MERGE: CollisionStrategy
COLLISION_STRATEGY_NONE: CollisionStrategy
COLLISION_STRATEGY_OVERWRITE: CollisionStrategy
DESCRIPTOR: _descriptor.FileDescriptor
ERROR_CODE_CANNOT_UPDATE_SCHEMA: ErrorCode
ERROR_CODE_CLOCK_ERROR: ErrorCode
ERROR_CODE_COZO_DB_ERROR: ErrorCode
ERROR_CODE_CSV_INGEST_ERROR: ErrorCode
ERROR_CODE_EMBEDDED_PROGRAM_EXECUTE_ERROR: ErrorCode
ERROR_CODE_ENTITY_COLLISION: ErrorCode
ERROR_CODE_ENTITY_NOT_FOUND: ErrorCode
ERROR_CODE_ENTITY_PARSE_ERROR: ErrorCode
ERROR_CODE_ENTITY_SERIALIZE_ERROR: ErrorCode
ERROR_CODE_FASTTEXT_ERROR: ErrorCode
ERROR_CODE_IMMUDB_ERROR: ErrorCode
ERROR_CODE_INSUFFICIENT_PERMISSIONS: ErrorCode
ERROR_CODE_INVALID_ENTITY: ErrorCode
ERROR_CODE_INVALID_HSQL_INSTRUCTION: ErrorCode
ERROR_CODE_INVALID_OPERATOR: ErrorCode
ERROR_CODE_JWT_DECODE_ERROR: ErrorCode
ERROR_CODE_JWT_NO_KEY_ID: ErrorCode
ERROR_CODE_JWT_NO_KEY_MATCH: ErrorCode
ERROR_CODE_JWT_PARSE_ERROR: ErrorCode
ERROR_CODE_LINKS_PARSE_ERROR: ErrorCode
ERROR_CODE_MISSING_PROPERTY: ErrorCode
ERROR_CODE_NONE: ErrorCode
ERROR_CODE_NOT_ALLOWED: ErrorCode
ERROR_CODE_NOT_IMPLEMENTED: ErrorCode
ERROR_CODE_PARSE_QUERY_ERROR: ErrorCode
ERROR_CODE_QUERY_DIMENSION_MISMATCH: ErrorCode
ERROR_CODE_ROCKSDB_ERROR: ErrorCode
ERROR_CODE_SCHEMA_EMBEDDING_ERROR: ErrorCode
ERROR_CODE_SCHEMA_VALIDATION: ErrorCode
ERROR_CODE_TOKEN_EXPIRED: ErrorCode
ERROR_CODE_UNHANDLED_ERROR: ErrorCode
ERROR_CODE_UPSERT_COLLISION: ErrorCode
IDENTITY_PROVIDER_APPLE: IdentityProvider
IDENTITY_PROVIDER_AUTH0: IdentityProvider
IDENTITY_PROVIDER_FACEBOOK: IdentityProvider
IDENTITY_PROVIDER_GITHUB: IdentityProvider
IDENTITY_PROVIDER_GOOGLE: IdentityProvider
IDENTITY_PROVIDER_LINKEDIN: IdentityProvider
IDENTITY_PROVIDER_MICROSOFT: IdentityProvider
IDENTITY_PROVIDER_NONE: IdentityProvider
IDENTITY_PROVIDER_OKTA: IdentityProvider
IDENTITY_PROVIDER_X: IdentityProvider
INGEST_TYPE_CSV: IngestType
INGEST_TYPE_JSON: IngestType
INGEST_TYPE_NONE: IngestType
LISTEN_RESPONSE_TYPE_ADDED: ListenResponseType
LISTEN_RESPONSE_TYPE_LINKS_ADDED: ListenResponseType
LISTEN_RESPONSE_TYPE_LINKS_REMOVED: ListenResponseType
LISTEN_RESPONSE_TYPE_LINKS_UPDATED: ListenResponseType
LISTEN_RESPONSE_TYPE_NONE: ListenResponseType
LISTEN_RESPONSE_TYPE_REMOVED: ListenResponseType
LISTEN_RESPONSE_TYPE_UPDATED: ListenResponseType
LISTEN_TYPE_ADD: ListenType
LISTEN_TYPE_LINKS_ADD: ListenType
LISTEN_TYPE_LINKS_REMOVE: ListenType
LISTEN_TYPE_NONE: ListenType
LISTEN_TYPE_REMOVE: ListenType

class ArchiveRequest(_message.Message):
    __slots__ = ["swid"]
    SWID_FIELD_NUMBER: _ClassVar[int]
    swid: str
    def __init__(self, swid: _Optional[str] = ...) -> None: ...

class ArchiveResponse(_message.Message):
    __slots__ = ["entity", "error"]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    entity: str
    error: HSTPError
    def __init__(self, entity: _Optional[str] = ..., error: _Optional[_Union[HSTPError, _Mapping]] = ...) -> None: ...

class AuthInfo(_message.Message):
    __slots__ = ["cover_verifier", "csrf_token", "nonce", "url"]
    COVER_VERIFIER_FIELD_NUMBER: _ClassVar[int]
    CSRF_TOKEN_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    cover_verifier: str
    csrf_token: str
    nonce: str
    url: str
    def __init__(self, url: _Optional[str] = ..., cover_verifier: _Optional[str] = ..., csrf_token: _Optional[str] = ..., nonce: _Optional[str] = ...) -> None: ...

class BatchArchiveRequest(_message.Message):
    __slots__ = ["requests"]
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[ArchiveRequest]
    def __init__(self, requests: _Optional[_Iterable[_Union[ArchiveRequest, _Mapping]]] = ...) -> None: ...

class BatchArchiveResponse(_message.Message):
    __slots__ = ["responses"]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    responses: _containers.RepeatedCompositeFieldContainer[ArchiveResponse]
    def __init__(self, responses: _Optional[_Iterable[_Union[ArchiveResponse, _Mapping]]] = ...) -> None: ...

class BatchLinksRequest(_message.Message):
    __slots__ = ["requests"]
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[LinksRequest]
    def __init__(self, requests: _Optional[_Iterable[_Union[LinksRequest, _Mapping]]] = ...) -> None: ...

class BatchLinksResponse(_message.Message):
    __slots__ = ["responses"]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    responses: _containers.RepeatedCompositeFieldContainer[LinksResponse]
    def __init__(self, responses: _Optional[_Iterable[_Union[LinksResponse, _Mapping]]] = ...) -> None: ...

class BatchListenRequest(_message.Message):
    __slots__ = ["requests"]
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[ListenRequest]
    def __init__(self, requests: _Optional[_Iterable[_Union[ListenRequest, _Mapping]]] = ...) -> None: ...

class BatchListenResponse(_message.Message):
    __slots__ = ["responses"]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    responses: _containers.RepeatedCompositeFieldContainer[ListenResponse]
    def __init__(self, responses: _Optional[_Iterable[_Union[ListenResponse, _Mapping]]] = ...) -> None: ...

class BatchNearestRequest(_message.Message):
    __slots__ = ["requests"]
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[NearestRequest]
    def __init__(self, requests: _Optional[_Iterable[_Union[NearestRequest, _Mapping]]] = ...) -> None: ...

class BatchNearestResponse(_message.Message):
    __slots__ = ["responses"]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    responses: _containers.RepeatedCompositeFieldContainer[NearestResponse]
    def __init__(self, responses: _Optional[_Iterable[_Union[NearestResponse, _Mapping]]] = ...) -> None: ...

class BatchReadRequest(_message.Message):
    __slots__ = ["requests"]
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[ReadRequest]
    def __init__(self, requests: _Optional[_Iterable[_Union[ReadRequest, _Mapping]]] = ...) -> None: ...

class BatchReadResponse(_message.Message):
    __slots__ = ["responses"]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    responses: _containers.RepeatedCompositeFieldContainer[ReadResponse]
    def __init__(self, responses: _Optional[_Iterable[_Union[ReadResponse, _Mapping]]] = ...) -> None: ...

class BatchRestoreRequest(_message.Message):
    __slots__ = ["requests"]
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[RestoreRequest]
    def __init__(self, requests: _Optional[_Iterable[_Union[RestoreRequest, _Mapping]]] = ...) -> None: ...

class BatchRestoreResponse(_message.Message):
    __slots__ = ["responses"]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    responses: _containers.RepeatedCompositeFieldContainer[RestoreResponse]
    def __init__(self, responses: _Optional[_Iterable[_Union[RestoreResponse, _Mapping]]] = ...) -> None: ...

class BatchUpsertRequest(_message.Message):
    __slots__ = ["requests"]
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[UpsertRequest]
    def __init__(self, requests: _Optional[_Iterable[_Union[UpsertRequest, _Mapping]]] = ...) -> None: ...

class BatchUpsertResponse(_message.Message):
    __slots__ = ["responses"]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    responses: _containers.RepeatedCompositeFieldContainer[UpsertResponse]
    def __init__(self, responses: _Optional[_Iterable[_Union[UpsertResponse, _Mapping]]] = ...) -> None: ...

class Entities(_message.Message):
    __slots__ = ["entities"]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    entities: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, entities: _Optional[_Iterable[str]] = ...) -> None: ...

class EntityDistance(_message.Message):
    __slots__ = ["distance", "entity"]
    DISTANCE_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    distance: float
    entity: str
    def __init__(self, entity: _Optional[str] = ..., distance: _Optional[float] = ...) -> None: ...

class EntityDistanceList(_message.Message):
    __slots__ = ["entities"]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    entities: _containers.RepeatedCompositeFieldContainer[EntityDistance]
    def __init__(self, entities: _Optional[_Iterable[_Union[EntityDistance, _Mapping]]] = ...) -> None: ...

class EntityList(_message.Message):
    __slots__ = ["entities"]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    entities: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, entities: _Optional[_Iterable[str]] = ...) -> None: ...

class GetAuthUrlRequest(_message.Message):
    __slots__ = ["provider"]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    provider: IdentityProvider
    def __init__(self, provider: _Optional[_Union[IdentityProvider, str]] = ...) -> None: ...

class GetAuthUrlResponse(_message.Message):
    __slots__ = ["auth_info", "error"]
    AUTH_INFO_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    auth_info: AuthInfo
    error: HSTPError
    def __init__(self, auth_info: _Optional[_Union[AuthInfo, _Mapping]] = ..., error: _Optional[_Union[HSTPError, _Mapping]] = ...) -> None: ...

class HSTPError(_message.Message):
    __slots__ = ["code", "message", "swid"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SWID_FIELD_NUMBER: _ClassVar[int]
    code: ErrorCode
    message: str
    swid: str
    def __init__(self, code: _Optional[_Union[ErrorCode, str]] = ..., message: _Optional[str] = ..., swid: _Optional[str] = ...) -> None: ...

class IngestDryRunSuccess(_message.Message):
    __slots__ = ["generated_schemas", "processed_data"]
    GENERATED_SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_DATA_FIELD_NUMBER: _ClassVar[int]
    generated_schemas: _containers.RepeatedScalarFieldContainer[str]
    processed_data: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, processed_data: _Optional[_Iterable[str]] = ..., generated_schemas: _Optional[_Iterable[str]] = ...) -> None: ...

class IngestRequest(_message.Message):
    __slots__ = ["doctype", "document", "dry_run"]
    DOCTYPE_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    doctype: IngestType
    document: str
    dry_run: bool
    def __init__(self, doctype: _Optional[_Union[IngestType, str]] = ..., document: _Optional[str] = ..., dry_run: bool = ...) -> None: ...

class IngestResponse(_message.Message):
    __slots__ = ["dry_run_success", "error", "success"]
    DRY_RUN_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    dry_run_success: IngestDryRunSuccess
    error: HSTPError
    success: IngestSuccess
    def __init__(self, success: _Optional[_Union[IngestSuccess, _Mapping]] = ..., error: _Optional[_Union[HSTPError, _Mapping]] = ..., dry_run_success: _Optional[_Union[IngestDryRunSuccess, _Mapping]] = ...) -> None: ...

class IngestSuccess(_message.Message):
    __slots__ = ["ingested_schemas", "ingested_swids"]
    INGESTED_SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    INGESTED_SWIDS_FIELD_NUMBER: _ClassVar[int]
    ingested_schemas: _containers.RepeatedScalarFieldContainer[str]
    ingested_swids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, ingested_swids: _Optional[_Iterable[str]] = ..., ingested_schemas: _Optional[_Iterable[str]] = ...) -> None: ...

class Links(_message.Message):
    __slots__ = ["links_with_this_swid_as_dst", "links_with_this_swid_as_src", "swid"]
    LINKS_WITH_THIS_SWID_AS_DST_FIELD_NUMBER: _ClassVar[int]
    LINKS_WITH_THIS_SWID_AS_SRC_FIELD_NUMBER: _ClassVar[int]
    SWID_FIELD_NUMBER: _ClassVar[int]
    links_with_this_swid_as_dst: _containers.RepeatedCompositeFieldContainer[ReadResponse]
    links_with_this_swid_as_src: _containers.RepeatedCompositeFieldContainer[ReadResponse]
    swid: str
    def __init__(self, swid: _Optional[str] = ..., links_with_this_swid_as_dst: _Optional[_Iterable[_Union[ReadResponse, _Mapping]]] = ..., links_with_this_swid_as_src: _Optional[_Iterable[_Union[ReadResponse, _Mapping]]] = ...) -> None: ...

class LinksRequest(_message.Message):
    __slots__ = ["swid"]
    SWID_FIELD_NUMBER: _ClassVar[int]
    swid: str
    def __init__(self, swid: _Optional[str] = ...) -> None: ...

class LinksResponse(_message.Message):
    __slots__ = ["error", "links"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    LINKS_FIELD_NUMBER: _ClassVar[int]
    error: HSTPError
    links: Links
    def __init__(self, links: _Optional[_Union[Links, _Mapping]] = ..., error: _Optional[_Union[HSTPError, _Mapping]] = ...) -> None: ...

class ListenRequest(_message.Message):
    __slots__ = ["swid", "type"]
    SWID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    swid: str
    type: ListenType
    def __init__(self, swid: _Optional[str] = ..., type: _Optional[_Union[ListenType, str]] = ...) -> None: ...

class ListenResponse(_message.Message):
    __slots__ = ["entity", "error", "response_type", "type"]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    entity: str
    error: HSTPError
    response_type: ListenResponseType
    type: ListenType
    def __init__(self, entity: _Optional[str] = ..., error: _Optional[_Union[HSTPError, _Mapping]] = ..., type: _Optional[_Union[ListenType, str]] = ..., response_type: _Optional[_Union[ListenResponseType, str]] = ...) -> None: ...

class NearestRequest(_message.Message):
    __slots__ = ["point", "space_swid", "swid", "topk"]
    POINT_FIELD_NUMBER: _ClassVar[int]
    SPACE_SWID_FIELD_NUMBER: _ClassVar[int]
    SWID_FIELD_NUMBER: _ClassVar[int]
    TOPK_FIELD_NUMBER: _ClassVar[int]
    point: Point
    space_swid: str
    swid: str
    topk: int
    def __init__(self, swid: _Optional[str] = ..., point: _Optional[_Union[Point, _Mapping]] = ..., space_swid: _Optional[str] = ..., topk: _Optional[int] = ...) -> None: ...

class NearestResponse(_message.Message):
    __slots__ = ["entities", "entity_distances", "error"]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    ENTITY_DISTANCES_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    entities: EntityList
    entity_distances: EntityDistanceList
    error: HSTPError
    def __init__(self, entities: _Optional[_Union[EntityList, _Mapping]] = ..., error: _Optional[_Union[HSTPError, _Mapping]] = ..., entity_distances: _Optional[_Union[EntityDistanceList, _Mapping]] = ...) -> None: ...

class ParseQueryRequest(_message.Message):
    __slots__ = ["query"]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: str
    def __init__(self, query: _Optional[str] = ...) -> None: ...

class ParseQueryResponse(_message.Message):
    __slots__ = ["error", "response_type"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TYPE_FIELD_NUMBER: _ClassVar[int]
    error: HSTPError
    response_type: str
    def __init__(self, response_type: _Optional[str] = ..., error: _Optional[_Union[HSTPError, _Mapping]] = ...) -> None: ...

class Point(_message.Message):
    __slots__ = ["coordinates"]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    coordinates: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, coordinates: _Optional[_Iterable[float]] = ...) -> None: ...

class QueryRequest(_message.Message):
    __slots__ = ["query"]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: str
    def __init__(self, query: _Optional[str] = ...) -> None: ...

class QueryResponse(_message.Message):
    __slots__ = ["error", "result"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    error: HSTPError
    result: str
    def __init__(self, result: _Optional[str] = ..., error: _Optional[_Union[HSTPError, _Mapping]] = ...) -> None: ...

class ReadRequest(_message.Message):
    __slots__ = ["swid"]
    SWID_FIELD_NUMBER: _ClassVar[int]
    swid: str
    def __init__(self, swid: _Optional[str] = ...) -> None: ...

class ReadResponse(_message.Message):
    __slots__ = ["entity", "error"]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    entity: str
    error: HSTPError
    def __init__(self, entity: _Optional[str] = ..., error: _Optional[_Union[HSTPError, _Mapping]] = ...) -> None: ...

class RestoreRequest(_message.Message):
    __slots__ = ["swid"]
    SWID_FIELD_NUMBER: _ClassVar[int]
    swid: str
    def __init__(self, swid: _Optional[str] = ...) -> None: ...

class RestoreResponse(_message.Message):
    __slots__ = ["entity", "error"]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    entity: str
    error: HSTPError
    def __init__(self, entity: _Optional[str] = ..., error: _Optional[_Union[HSTPError, _Mapping]] = ...) -> None: ...

class UpsertRequest(_message.Message):
    __slots__ = ["collision_strategy", "entity"]
    COLLISION_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    collision_strategy: CollisionStrategy
    entity: str
    def __init__(self, entity: _Optional[str] = ..., collision_strategy: _Optional[_Union[CollisionStrategy, str]] = ...) -> None: ...

class UpsertResponse(_message.Message):
    __slots__ = ["entity", "error"]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    entity: str
    error: HSTPError
    def __init__(self, entity: _Optional[str] = ..., error: _Optional[_Union[HSTPError, _Mapping]] = ...) -> None: ...

class ListenType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ListenResponseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class CollisionStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class IngestType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class IdentityProvider(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
