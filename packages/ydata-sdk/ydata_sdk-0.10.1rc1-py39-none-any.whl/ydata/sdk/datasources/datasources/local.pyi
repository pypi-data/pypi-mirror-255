from pandas import DataFrame as pdDataFrame
from pathlib import Path
from typing import Optional, Union
from ydata.sdk.common.client import Client
from ydata.sdk.datasources._models.datatype import DataSourceType
from ydata.sdk.datasources._models.filetype import FileType
from ydata.sdk.datasources.datasource import DataSource

class LocalDataSource(DataSource):
    def __init__(self, source: Union[pdDataFrame, str, Path], datatype: Optional[Union[DataSourceType, str]] = ..., filetype: Union[FileType, str] = ..., separator: str = ..., name: Optional[str] = ..., wait_for_metadata: bool = ..., client: Optional[Client] = ...) -> None: ...
