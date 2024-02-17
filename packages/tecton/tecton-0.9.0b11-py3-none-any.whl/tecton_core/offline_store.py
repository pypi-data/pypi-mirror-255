import datetime
import enum
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Tuple
from typing import Union

import attrs
import pendulum
import pyarrow
import pyarrow.compute
import pyarrow.dataset
import pyarrow.fs

from tecton_core import id_helper
from tecton_core import time_utils
from tecton_core.compute_mode import BatchComputeMode
from tecton_core.errors import TectonInternalError
from tecton_core.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_core.query_consts import anchor_time
from tecton_core.specs import FeatureTableSpec
from tecton_core.specs import MaterializedFeatureViewSpec
from tecton_proto.common.id_pb2 import Id
from tecton_proto.data.feature_view_pb2 import DeltaOfflineStoreVersion
from tecton_proto.data.feature_view_pb2 import OfflineStoreParams
from tecton_proto.data.feature_view_pb2 import ParquetOfflineStoreVersion


TIME_PARTITION = "time_partition"
SECONDS_TO_NANOSECONDS = 1000 * 1000 * 1000
CONTINUOUS_PARTITION_SIZE_SECONDS = 86400


class PartitionType(str, enum.Enum):
    DATE_STR = "DateString"
    EPOCH = "Epoch"
    # RAW_TIMESTAMP is only used for Snowflake
    RAW_TIMESTAMP = "RawTimestamp"


class OfflineStoreType(str, enum.Enum):
    PARQUET = "parquet"
    DELTA = "delta"
    SNOWFLAKE = "snowflake"


@attrs.frozen
class TimestampFormats:
    spark_format: str
    python_format: str


@attrs.frozen
class OfflineStorePartitionParams:
    partition_by: str
    partition_type: PartitionType
    partition_interval: pendulum.duration


def partition_size_for_parquet(fd: FeatureDefinition) -> pendulum.Duration:
    if fd.offline_store_params is not None:
        return pendulum.Duration(
            seconds=fd.offline_store_params.parquet.time_partition_size.ToTimedelta().total_seconds()
        )
    elif fd.is_continuous:
        return pendulum.Duration(seconds=CONTINUOUS_PARTITION_SIZE_SECONDS)
    else:
        return fd.min_scheduling_interval


def partition_col_for_parquet(fd: FeatureDefinition) -> str:
    offline_store_version = (
        fd.offline_store_params.parquet.version
        if fd.offline_store_params is not None
        else ParquetOfflineStoreVersion.PARQUET_OFFLINE_STORE_VERSION_1
    )
    if offline_store_version == ParquetOfflineStoreVersion.PARQUET_OFFLINE_STORE_VERSION_1:
        return TIME_PARTITION if fd.is_continuous else anchor_time()
    elif offline_store_version == ParquetOfflineStoreVersion.PARQUET_OFFLINE_STORE_VERSION_2:
        return TIME_PARTITION
    else:
        msg = "unsupported offline store version"
        raise TectonInternalError(msg)


def partition_size_for_delta(fd: FeatureDefinition) -> pendulum.Duration:
    if fd.offline_store_params is not None:
        return pendulum.Duration(
            seconds=fd.offline_store_params.delta.time_partition_size.ToTimedelta().total_seconds()
        )
    else:
        return pendulum.Duration(
            seconds=fd.offline_store_config.delta.time_partition_size.ToTimedelta().total_seconds()
        )


def partition_type_for_delta(offline_store_params: Optional[OfflineStoreParams]) -> PartitionType:
    # TODO(TEC-17350): use this method when reading from the offline store
    if (
        offline_store_params is not None
        and offline_store_params.delta.version == DeltaOfflineStoreVersion.DELTA_OFFLINE_STORE_VERSION_2
    ):
        return PartitionType.EPOCH
    else:
        return PartitionType.DATE_STR


DELTA_SUPPORTED_VERSIONS = [
    DeltaOfflineStoreVersion.DELTA_OFFLINE_STORE_VERSION_1,
    DeltaOfflineStoreVersion.DELTA_OFFLINE_STORE_VERSION_2,
]

PARQUET_SUPPORTED_VERSIONS = [
    ParquetOfflineStoreVersion.PARQUET_OFFLINE_STORE_VERSION_1,
    ParquetOfflineStoreVersion.PARQUET_OFFLINE_STORE_VERSION_2,
]


def _check_supported_offline_store_version(fd: FeatureDefinition) -> None:
    if fd.offline_store_params is None:
        return
    if (
        fd.offline_store_params.HasField("delta")
        and fd.offline_store_params.delta.version not in DELTA_SUPPORTED_VERSIONS
    ):
        msg = (
            f"Unsupported offline store version {fd.offline_store_params.delta.version}. Try upgrading your Tecton SDK."
        )
        raise TectonInternalError(msg)
    if (
        fd.offline_store_params.HasField("parquet")
        and fd.offline_store_params.parquet.version not in PARQUET_SUPPORTED_VERSIONS
    ):
        msg = f"Unsupported offline store version {fd.offline_store_params.parquet.version}. Try upgrading your Tecton SDK."
        raise TectonInternalError(msg)


def get_offline_store_type(fd: FeatureDefinition) -> OfflineStoreType:
    # TODO(TEC-15800): Update Snowflake FV protos to have snowflake as their store type
    assert isinstance(fd.fv_spec, (MaterializedFeatureViewSpec, FeatureTableSpec))
    if (
        isinstance(fd.fv_spec, MaterializedFeatureViewSpec)
        and fd.fv_spec.batch_compute_mode == BatchComputeMode.SNOWFLAKE
    ):
        return OfflineStoreType.SNOWFLAKE

    store_type = fd.offline_store_config.WhichOneof("store_type")
    if store_type == OfflineStoreType.PARQUET:
        return OfflineStoreType.PARQUET
    elif store_type == OfflineStoreType.DELTA:
        return OfflineStoreType.DELTA
    else:
        msg = f"Unknown offline store type {store_type}"
        raise TectonInternalError(msg)


def get_offline_store_partition_params(feature_definition: FeatureDefinition) -> OfflineStorePartitionParams:
    # Examples of how our offline store is partitioned
    ### BWAFV on Delta
    # Partition Column: time_partition
    # Materialized Columns: _anchor_time, [join_keys], [feature_columns]

    ### Continuous SWAFV on Parquet
    # Partition Column: time_partition
    # Materialized Columns: timestamp, _anchor_time, [join_keys], [feature_columns]
    # Note: Very weird that we have a timestamp parquet column here - redundant with _anchor_time

    ### BWAFV on Parquet
    # Partition Column: _anchor_time
    # Materialized Columns: _anchor_time, [join_keys], [feature_columns]
    # !! In this case we need to drop the partition column from the top level columns

    ### BFV on Parquet
    # Partition Column: _anchor_time
    # Materialized Columns: ts, [join_keys], [feature_columns]

    ### Any FV on Snowflake
    # Partition Column: none
    # Materialized Columns: ts, [join_keys], [feature_columns]

    _check_supported_offline_store_version(feature_definition)
    store_type = get_offline_store_type(feature_definition)

    if store_type == OfflineStoreType.SNOWFLAKE:
        partition_by = feature_definition.time_key
        partition_type = PartitionType.RAW_TIMESTAMP
        partition_interval = pendulum.Duration(seconds=0)
    elif store_type == OfflineStoreType.DELTA:
        partition_by = TIME_PARTITION
        partition_type = PartitionType.DATE_STR
        partition_interval = partition_size_for_delta(feature_definition)
    elif store_type == OfflineStoreType.PARQUET:
        partition_by = partition_col_for_parquet(feature_definition)
        partition_type = PartitionType.EPOCH
        partition_interval = partition_size_for_parquet(feature_definition)
    else:
        msg = "Unexpected offline store config"
        raise Exception(msg)
    return OfflineStorePartitionParams(partition_by, partition_type, partition_interval)


def timestamp_to_partition_date_str(timestamp: pendulum.DateTime, partition_params: OfflineStorePartitionParams) -> str:
    partition_interval_timedelta = partition_params.partition_interval.as_timedelta()
    aligned_time = time_utils.align_time_downwards(timestamp, partition_interval_timedelta)
    partition_format = timestamp_formats(partition_interval_timedelta).python_format
    return aligned_time.strftime(partition_format)


def timestamp_to_partition_epoch(
    timestamp: pendulum.DateTime,
    partition_params: OfflineStorePartitionParams,
    feature_store_format_version: int,
) -> int:
    aligned_time = time_utils.align_time_downwards(timestamp, partition_params.partition_interval.as_timedelta())
    # align_time_downwards returns the time without tzinfo. convert_timestamp_for_version calls timestamp() which
    # treats naive datetime instances as local time. This can cause an issue if local time is not in UTC.
    aligned_time = aligned_time.replace(tzinfo=datetime.timezone.utc)
    return time_utils.convert_timestamp_for_version(aligned_time, feature_store_format_version)


def window_size_seconds(window: Union[timedelta, pendulum.Duration]) -> int:
    if isinstance(window, pendulum.Duration):
        window = window.as_timedelta()
    if window % timedelta(seconds=1) != timedelta(0):
        msg = f"partition_size is not a round number of seconds: {window}"
        raise AssertionError(msg)
    return int(window.total_seconds())


def timestamp_formats(partition_size: timedelta) -> TimestampFormats:
    if partition_size % timedelta(days=1) == timedelta(0):
        return TimestampFormats(spark_format="yyyy-MM-dd", python_format="%Y-%m-%d")
    else:
        return TimestampFormats(spark_format="yyyy-MM-dd-HH:mm:ss", python_format="%Y-%m-%d-%H:%M:%S")


def datetime_to_partition_str(dt: datetime, partition_size: timedelta) -> str:
    partition_format = timestamp_formats(partition_size).python_format
    return dt.strftime(partition_format)


@dataclass
class OfflineStoreReaderParams:
    delta_table_uri: str


class OfflineStoreReader(ABC):
    @abstractmethod
    def read(self, partition_time_limits: Optional[pendulum.Period] = None) -> "pyarrow.Table":  # noqa: F821
        raise NotImplementedError


@dataclass
class S3Options:
    access_key_id: str
    secret_access_key: str
    session_token: Optional[str]
    region: Optional[str] = None

    def to_dict(self):
        opts = {
            "AWS_ACCESS_KEY_ID": self.access_key_id,
            "AWS_SECRET_ACCESS_KEY": self.secret_access_key,
        }
        if self.session_token:
            opts["AWS_SESSION_TOKEN"] = self.session_token
        if self.region:
            opts["AWS_REGION"] = self.region
        return opts


class OfflineStoreOptionsProvider:
    def get_s3_options(self, feature_view_id: Id) -> Optional[S3Options]:
        return


class BotoOfflineStoreOptionsProvider(OfflineStoreOptionsProvider):
    """deltalake's built-in S3 auth is implemented by a Rust library which doesn't support the full range of AWS
    auth configurations supported by boto, which can be surprising to users used to boto's options. This class
    following does a fully-featured auth using boto instead of depending on Rust.

    See also https://github.com/delta-io/delta-rs/issues/855
    """

    @staticmethod
    def static_options() -> Optional[S3Options]:
        import boto3

        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            return None
        current_credentials = credentials.get_frozen_credentials()
        return S3Options(
            access_key_id=current_credentials.access_key,
            secret_access_key=current_credentials.secret_key,
            session_token=current_credentials.token,
        )

    def get_s3_options(self, feature_view_id: Id) -> Optional[S3Options]:
        return BotoOfflineStoreOptionsProvider.static_options()


DEFAULT_OPTIONS_PROVIDERS = [BotoOfflineStoreOptionsProvider()]


class DeltaReader(OfflineStoreReader):
    def __init__(
        self,
        params: OfflineStoreReaderParams,
        fd: FeatureDefinition,
        options_providers: Iterable[OfflineStoreOptionsProvider],
    ) -> None:
        self._params = params
        self._partition_size = partition_size_for_delta(fd).as_timedelta()
        self._fd = fd
        self._options_providers = options_providers

    def _storage_options(self) -> Dict[str, str]:
        fvid = id_helper.IdHelper.from_string(self._fd.id)
        if self._params.delta_table_uri.startswith("s3"):
            options = next(
                filter(lambda o: o is not None, (p.get_s3_options(fvid) for p in self._options_providers)), None
            )
            if options is None:
                msg = f"No S3 store options were provided for feature view {self._fd.name}"
                raise ValueError(msg)

            return options.to_dict()

        return {}

    def read(self, partition_time_limits: Optional[pendulum.Period] = None) -> "pyarrow.Table":  # noqa: F821
        # TODO(TEC-16757): Move import to top of file.
        from deltalake import DeltaTable

        filters = None
        if partition_time_limits is not None and self._partition_size:
            filters = []
            aligned_start_time = time_utils.align_time_downwards(partition_time_limits.start, self._partition_size)
            start_partition = datetime_to_partition_str(aligned_start_time, self._partition_size)
            filters.append((TIME_PARTITION, ">=", start_partition))

            aligned_end_time = time_utils.align_time_downwards(partition_time_limits.end, self._partition_size)
            end_partition = datetime_to_partition_str(aligned_end_time, self._partition_size)
            filters.append((TIME_PARTITION, "<=", end_partition))

        # "partitions" parameters is applied earlier by DeltaTable itself (and not passed to pyarrow like filters)
        return DeltaTable(
            table_uri=self._params.delta_table_uri, storage_options=self._storage_options()
        ).to_pyarrow_table(partitions=filters)


class ParquetReader(OfflineStoreReader):
    def __init__(
        self,
        fd: FeatureDefinition,
        options_providers: Iterable[OfflineStoreOptionsProvider],
    ) -> None:
        self._fd = fd
        self._options_providers = options_providers
        self._partition_params = get_offline_store_partition_params(self._fd)

    def _partition_column_type(self):
        return pyarrow.int64() if self._partition_params.partition_type == PartitionType.EPOCH else pyarrow.string()

    def _filesystem_and_uri(self) -> Tuple[pyarrow.fs.FileSystem, str]:
        uri = self._fd.materialized_data_path
        fs, path = pyarrow.fs.FileSystem.from_uri(uri)
        fvid = id_helper.IdHelper.from_string(self._fd.id)

        if isinstance(fs, pyarrow.fs.S3FileSystem):
            options = next(
                filter(lambda o: o is not None, (p.get_s3_options(fvid) for p in self._options_providers)), None
            )
            if options is None:
                msg = f"No S3 store options were provided for feature view {self._fd.name}"
                raise ValueError(msg)

            return (
                pyarrow.fs.S3FileSystem(
                    access_key=options.access_key_id,
                    secret_key=options.secret_access_key,
                    session_token=options.session_token,
                ),
                path,
            )

        return fs, path

    def _filter(self, partition_time_limits: Optional[pendulum.Period]) -> pyarrow.dataset.Expression:
        if not partition_time_limits:
            return

        start_partition = timestamp_to_partition_epoch(
            partition_time_limits.start,
            self._partition_params,
            self._fd.get_feature_store_format_version,
        )
        end_partition = timestamp_to_partition_epoch(
            partition_time_limits.end,
            self._partition_params,
            self._fd.get_feature_store_format_version,
        )
        column = pyarrow.compute.field(self._partition_params.partition_by)
        return (column >= start_partition) & (column <= end_partition)

    def read(self, partition_time_limits: Optional[pendulum.Period] = None) -> "pyarrow.Table":
        partitioning = pyarrow.dataset.partitioning(
            pyarrow.schema([(self._partition_params.partition_by, self._partition_column_type())]), flavor="hive"
        )
        fs, uri = self._filesystem_and_uri()

        # We had to use an explicit dataset creation (via FileSystemDatasetFactory)
        # to override default `selector_ignore_prefixes` parameter.
        # The default behaviour is to ignore directories/files starting with ["_", "."],
        # and we use column `_anchor_time` as a partition column.
        selector = pyarrow.fs.FileSelector(uri, recursive=True)
        file_format = pyarrow.dataset.ParquetFileFormat()
        options = pyarrow.dataset.FileSystemFactoryOptions(
            partitioning=partitioning,
            selector_ignore_prefixes=[".", "_SUCCESS", "_committed", "_started"],
        )
        ds = pyarrow.dataset.FileSystemDatasetFactory(fs, selector, file_format, options).finish()
        table = ds.to_table(filter=self._filter(partition_time_limits))
        return table
