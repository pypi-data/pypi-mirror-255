#
# Copyright 2023 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

import trafaret as t

from datarobot._experimental.models.enums import ExternalStorageType, StorageKind
from datarobot.enums import DEFAULT_MAX_WAIT
from datarobot.models.api_object import APIObject
from datarobot.utils.waiters import wait_for_async_resolution


class ExternalStorage(APIObject):
    """
    The external storage location for the data chunks.

    Attributes
    ----------
     external_reference_id : str
        The ID of the storage entity.
     external_storage_type : str
        The type of external storage.

    """

    _converter = t.Dict(
        {
            t.Key("external_reference_id"): t.String,
            t.Key("external_storage_type"): t.String,
        }
    ).allow_extra("*")

    def __init__(
        self,
        external_reference_id: str,
        external_storage_type: str,
    ):
        self.external_reference_id = external_reference_id
        self.external_storage_type = external_storage_type


class Chunk(APIObject):
    """
    Data chunk object that holds metadata about a chunk.

    Attributes
    ----------
    id : str
        The ID of the chunk entity.
    chunk_definition_id : str
        The ID of the dataset chunk definition the chunk belongs to.
    limit : int
        The number of rows in the chunk.
    offset : int
        The offset in the dataset to create the chunk.
    chunk_index : str
        The index of the chunk if chunks are divided uniformly. Otherwise, it is None.
    data_source_id : str
        The ID of the data request used to create the chunk.
    external_storage : ExternalStorage
        A list of storage locations where the chunk is stored.

    """

    _converter = t.Dict(
        {
            t.Key("id"): t.String,
            t.Key("chunk_definition_id"): t.String,
            t.Key("limit"): t.Int,
            t.Key("offset"): t.Int,
            t.Key("chunk_index", optional=True): t.Or(t.Int, t.Null),
            t.Key("data_source_id", optional=True): t.Or(t.String, t.Null),
            t.Key("external_storage", optional=True): t.Or(
                t.List(ExternalStorage._converter), t.Null
            ),
        }
    ).allow_extra("*")

    def __init__(
        self,
        id: str,
        chunk_definition_id: str,
        limit: int,
        offset: int,
        chunk_index: Optional[int] = None,
        data_source_id: Optional[str] = None,
        external_storage: Optional[List[ExternalStorage]] = None,
    ):
        self.id = id
        self.chunk_definition_id = chunk_definition_id
        self.chunk_index = chunk_index
        self.offset = offset
        self.limit = limit
        self.data_source_id = data_source_id
        self.external_storage = external_storage

    def get_external_storage_id(self, storage_type: ExternalStorageType) -> Optional[str]:
        """
        Get external storage id for the chunk.

        Parameters
        ----------
        storage_type: ExternalStorageType
            The external storage type where the chunk is store.

        Returns
        -------
        external_reference_id: str
            An ID that references the external storage for the chunk.

        """
        if self.external_storage is None:
            return None

        for external_storage in self.external_storage:
            if isinstance(external_storage, Dict):
                external_storage = ExternalStorage(**external_storage)

            if external_storage.external_storage_type == storage_type:
                return external_storage.external_reference_id
        return None


class DatasourceDefinition(APIObject):
    """
    Data source definition that holds information data source.


     Attributes
     ----------
     id : str
         The ID of the data source definition.
     data_store_id : str
         The ID of the data store.
     credentials_id : str
        The ID of the credentials.
     table : str
         The data source table name.
     schema : str
         The offset into the dataset to create the chunk.
     catalog : str
         The database or catalog name.
     storage_kind : str
         The origin data source or data warehouse (e.g., Snowflake, BigQuery).
     data_source_id : str
         The ID of the data request used to generate sampling and metadata.
     total_rows : str
         The total number of rows in the dataset.
     source_size : str
         The size of the dataset.
     estimated_size_per_row : str
         The estimated size per row.
     columns : str
         The list of column names in the dataset.

    """

    _converter = t.Dict(
        {
            t.Key("id"): t.String,
            t.Key("data_store_id"): t.String,
            t.Key("credentials_id"): t.String,
            t.Key("table"): t.String,
            t.Key("schema"): t.String,
            t.Key("catalog"): t.String,
            t.Key("storage_kind"): t.String,
            t.Key("name", optional=True): t.Or(t.String, t.Null),
            t.Key("data_source_id", optional=True): t.Or(t.String, t.Null),
            t.Key("total_rows", optional=True): t.Or(t.Int, t.Null),
            t.Key("source_size", optional=True): t.Or(t.Int, t.Null),
            t.Key("estimated_size_per_row", optional=True): t.Or(t.Int, t.Null),
            t.Key("columns", optional=True): t.Or(t.List(t.String), t.Null),
        }
    ).allow_extra("*")

    def __init__(
        self,
        id: str,
        data_store_id: str,
        credentials_id: str,
        table: str,
        schema: str,
        catalog: str,
        storage_kind: StorageKind,
        name: Optional[str] = None,
        data_source_id: Optional[str] = None,
        total_rows: Optional[int] = None,
        source_size: Optional[int] = None,
        estimated_size_per_row: Optional[int] = None,
        columns: Optional[List[str]] = None,
    ):
        self.id = id
        self.name = name
        self.data_store_id = data_store_id
        self.credentials_id = credentials_id
        self.table = table
        self.schema = schema
        self.catalog = catalog
        self.storage_kind = storage_kind
        self.data_source_id = data_source_id
        self.total_rows = total_rows
        self.source_size = source_size
        self.estimated_size_per_row = estimated_size_per_row
        self.columns = columns


class DatasetChunkDefinition(APIObject):
    """
    Dataset chunking definition that holds information about how to chunk the dataset.

     Attributes
    ----------
    id : str
        The ID of the dataset chunk definition.
    user_id : str
        The ID of the user who created the definition.
    name : str
        The name of the dataset chunk definition.
    project_starter_chunk_size : int
        The size, in bytes, of the project starter chunk.
    order_by_columns : List[str]
        A list of columns used to sort the dataset.
    datasource_definition_id : str
        The datasource definition ID associated with the dataset chunk definition.
    storage_kind : str
        The origin data source or data warehouse e.g. Snowflake, BigQuery.
    data_source_id : str
        The ID of the data request used to generate sampling and metadata.
    filter_id : str
       The ID of the filter.
    columns_to_select : List[str]
        A list of columns to select from the dataset.

    """

    _path = "datasetChunkDefinitions/"
    _path_with_id = _path + "{}/"
    _path_datasource = _path + "{}/datasourceDefinition/"
    _path_chunks = _path + "{}/chunks/"
    _path_chunk = _path_chunks + "{}/"

    _converter = t.Dict(
        {
            t.Key("id"): t.String,
            t.Key("user_id"): t.String,
            t.Key("name"): t.String,
            t.Key("project_starter_chunk_size"): t.Int,
            t.Key("user_chunk_size"): t.Int,
            t.Key("order_by_columns"): t.List(t.String),
            t.Key("datasource_definition_id", optional=True): t.Or(t.String, t.Null),
            t.Key("filter_id", optional=True): t.Or(t.String, t.Null),
            t.Key("select_columns", optional=True): t.Or(t.List(t.String), t.Null),
        }
    ).allow_extra("*")

    def __init__(
        self,
        id: str,
        user_id: str,
        name: str,
        project_starter_chunk_size: int,
        user_chunk_size: int,
        order_by_columns: List[str],
        datasource_definition_id: Optional[str] = None,
        filter_id: Optional[str] = None,
        select_columns: Optional[List[str]] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.project_starter_chunk_size = project_starter_chunk_size
        self.user_chunk_size = user_chunk_size
        self.order_by_columns = order_by_columns
        self.datasource_definition_id = datasource_definition_id
        self.filter_id = filter_id
        self.select_columns = select_columns

    @classmethod
    def get(cls, dataset_chunk_definition_id: str) -> DatasetChunkDefinition:
        """
        Retrieve a specific dataset chunk definition metadata.

        Parameters
        ----------
        dataset_chunk_definition_id: str
            The ID of the dataset chunk definition.

        Returns
        -------
        dataset_chunk_definition : DatasetChunkDefinition
            The queried instance.
        """
        path = cls._path_with_id.format(dataset_chunk_definition_id)
        response = cls._client.get(path)
        return cls.from_server_data(response.json())

    @classmethod
    def list(cls, limit: int = 50, offset: int = 0) -> List[DatasetChunkDefinition]:
        """
        Retrieves a list of dataset chunk definitions

        Parameters
        ----------
        limit: int
            The maximum number of objects to return. Default is 50.
        offset: int
            The starting offset of the results. Default is 0.
        Returns
        -------
        dataset_chunk_definitions : List[DatasetChunkDefinition]
            The list of dataset chunk definitions.

        """
        params: Dict[str, Union[str, int]] = {"limit": limit, "offset": offset}
        response = cls._client.get(cls._path, params=params)
        r_data = response.json()
        return [cls.from_server_data(item) for item in r_data["data"]]

    @classmethod
    def create(
        cls,
        name: str,
        project_starter_chunk_size: int,
        user_chunk_size: int,
        data_store_id: str,
        credentials_id: str,
        table: str,
        schema: str,
        catalog: str,
        storage_kind: StorageKind,
        order_by_columns: List[str],
        filter_id: Optional[str] = None,
        select_columns: Optional[List[str]] = None,
    ) -> DatasetChunkDefinition:
        """
        Create a dataset chunk definition. Required for both index-based and custom chunks.

        In order to create a dataset chunk definition, you must first:
            - Create a data connection to the target data source via ``dr.DataStore.create()``
            - Create credentials that must be attached to the data connection via ``dr.Credential.create()``

        If you have an existing data connections and credentials:
            - Retrieve the data store id by the canonical name via
              ``[ds for ds in dr.DataStore.list() if ds.canonical_name == <name>][0].id``
            - Retrieve the credential id by the name via
              ``[cr for cr in dr.Credential.list() if ds.name == <name>][0].id``

        Parameters
        ----------
        name : str
            The name of the dataset chunk definition.
        project_starter_chunk_size : int
            The size in bytes of the first chunk. Used to start a datarobot project.
        data_store_id : str
            The ID of the target data source.
        credentials_id : str
            The ID of the credentials attached or associated with the data_store_id.
        table : str
            The name of the table.
        schema : str
            The name of the schema.
        catalog : str
            The name of the database.
        catalog : str
            The name of the database.
        storage_kind : str
            The type of data source or data warehouse e.g Snowflake, BigQuery.
        order_by_columns : List[str]
            A list of columns used to sort the dataset.
        filter_id: str
            The ID of the filter object used to filter the data.
        select_columns: List[str]
            A list of columns to select from the dataset.


        Returns
        -------
        dataset_chunk_definition: DatasetChunkDefinition
            An instance of a created dataset chunk definition.

        """

        payload = {
            "name": name,
            "starterChunkSize": project_starter_chunk_size,
            "chunkSize": user_chunk_size,
            "columnsOrder": order_by_columns,
            "dataStoreId": data_store_id,
            "credentialsId": credentials_id,
            "table": table,
            "schema": schema,
            "catalog": catalog,
            "storageKind": storage_kind,
        }

        if select_columns is not None:
            payload["select_columns"] = select_columns
        if filter_id is not None:
            payload["filter_id"] = filter_id

        response = cls._client.post(cls._path, data=payload)
        data = response.json()
        return cls.from_server_data(data)

    @classmethod
    def get_datasource_definition(cls, dataset_chunk_definition_id: str) -> DatasourceDefinition:
        """
        Retrieves the data source definition associated with a dataset chunk definition.

        Parameters
        ----------
        dataset_chunk_definition_id: str
            id of the dataset chunk definition

        Returns
        -------
        datasource_definition: DatasourceDefinition
            an instance of created datasource definition
        """
        path = cls._path_datasource.format(dataset_chunk_definition_id)
        response = cls._client.get(path)
        return DatasourceDefinition.from_server_data(response.json())

    @classmethod
    def get_chunk(cls, dataset_chunk_definition_id: str, chunk_id: str) -> Chunk:
        """
        Retrieves a specific data chunk associated with a dataset chunk definition

        Parameters
        ----------
        dataset_chunk_definition_id: str
            id of the dataset chunk definition
        chunk_id:
            id of the chunk

        Returns
        -------
        chunk: Chunk
            an instance of created chunk
        """
        path = cls._path_chunk.format(dataset_chunk_definition_id, chunk_id)
        response = cls._client.get(path)
        return Chunk.from_server_data(response.json())

    @classmethod
    def list_chunks(cls, dataset_chunk_definition_id: str) -> List[Chunk]:
        """
        Retrieves all data chunks associated with a dataset chunk definition

        Parameters
        ----------
        dataset_chunk_definition_id: str
            id of the dataset chunk definition

        Returns
        -------
        chunks: List[Chunk]
            a list of chunks
        """
        path = cls._path_chunks.format(dataset_chunk_definition_id)
        response = cls._client.get(path)
        r_data = response.json()
        return [Chunk.from_server_data(item) for item in r_data["data"]]

    def analyze_dataset(self) -> DatasourceDefinition:
        """
        Analyzes the data source to retrieve and compute metadata about the dataset.

        Depending on the size of the data set, adding ``order_by_columns`` to the dataset chunking definition
        will increase the execution time to create the data chunk.
        Set the ``max_wait_time`` for the appropriate wait time.

        Returns
        -------
        datasource_definition: DatasourceDefinition
            an instance of created datasource definition
        """
        path = self._path_with_id + "analyzeDataset"
        response = self._client.post(path.format(self.id))
        async_loc = response.headers["Location"]
        datasource_location = wait_for_async_resolution(
            self._client, async_loc, max_wait=DEFAULT_MAX_WAIT
        )
        return DatasourceDefinition.from_location(datasource_location)

    def create_chunk(
        self,
        limit: int,
        offset: int = 0,
        storage_type: ExternalStorageType = ExternalStorageType.DATASTAGE,
        max_wait_time: int = DEFAULT_MAX_WAIT,
    ) -> Chunk:
        """
        Creates a data chunk using the limit and offset. By default, the data chunk is stored in data stages.

        Depending on the size of the data set, adding ``order_by_columns`` to the dataset chunking definition
        will increase the execution time to retrieve or create the data chunk.
        Set the ``max_wait_time`` for the appropriate wait time.

        Parameters
        ----------
        limit: int
            The maximum number of rows.
        offset: int
            The offset into the dataset to begin reading.
        storage_type: ExternalStorageType
            The storage location of the chunk.

        Returns
        -------
        chunk: Chunk
            An instance of a created or updated chunk.
        """
        payload = {
            "limit": limit,
            "offset": offset,
            "storageType": storage_type,
        }

        url = self._path_with_id + "createChunk"
        path = url.format(self.id)
        return self._create_chunk(path, payload, max_wait_time=max_wait_time)

    def create_chunk_by_index(
        self,
        index: int,
        storage_type: ExternalStorageType = ExternalStorageType.DATASTAGE,
        max_wait_time: int = DEFAULT_MAX_WAIT,
    ) -> Chunk:
        """
        Creates a data chunk using the limit and offset. By default, the data chunk is stored in data stages.

        Depending on the size of the data set, adding ``order_by_columns`` to the dataset chunking definition
        will increase the execution time to retrieve or create the data chunk.
        Set the ``max_wait_time`` for the appropriate wait time.

        Parameters
        ----------
        limit: int
            The maximum number of rows.
        offset: int
            The offset into the dataset to begin reading.
        storage_type: ExternalStorageType
            The storage location of the chunk.

        Returns
        -------
        chunk: Chunk
            An instance of a created or updated chunk.
        """
        payload = {
            "index": index,
            "storageType": storage_type,
        }
        url = self._path_with_id + "createIndexChunk"
        path = url.format(self.id)
        return self._create_chunk(path, payload, max_wait_time=max_wait_time)

    def _create_chunk(
        self, path: str, payload: Dict[str, Any], max_wait_time: int = DEFAULT_MAX_WAIT
    ) -> Chunk:
        response = self._client.post(path, data=payload)
        async_loc = response.headers["Location"]
        chunk_location = wait_for_async_resolution(self._client, async_loc, max_wait=max_wait_time)
        return Chunk.from_location(chunk_location)
