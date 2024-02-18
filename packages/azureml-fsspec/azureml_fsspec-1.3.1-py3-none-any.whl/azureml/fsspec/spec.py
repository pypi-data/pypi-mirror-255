# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains fsspec api implementation for aml uri
"""
from fsspec.asyn import (
    AsyncFileSystem,
    get_loop,
    sync
)
from fsspec.callbacks import _DEFAULT_CALLBACK
from fsspec.implementations.local import make_path_posix

import os
import re
import inspect
from glob import has_magic
from azureml.dataprep.api._loggerfactory import track, _LoggerFactory
from azureml.dataprep.api._constants import ACTIVITY_INFO_KEY, ERROR_CODE_KEY, \
    COMPLIANT_MESSAGE_KEY, OUTER_ERROR_CODE_KEY
from azureml.dataprep.rslex import StreamInfo, CachingOptions, BufferingOptions, Downloader, \
    Copier, PyIfDestinationExists, PyLocationInfo, UriAccessor
from azureml.dataprep.api._rslex_executor import ensure_rslex_environment
from azureml.dataprep import UserErrorException, ExecutionError
from azureml.dataprep.api.mltable._validation_and_error_handler import _reclassify_rslex_error

_PUBLIC_API = 'PublicApi'
_APP_NAME = 'azureml-fsspec'
_logger = None
_DATASTORE_HANDLER = 'AmlDatastore'
_DATAASSET_HANDLER = 'AmlDataAsset'

_HANDLER_SUBS_KEY = 'subscription'
_HANDLER_RG_KEY = 'resourceGroup'
_HANDLER_WS_KEY = 'workspaceName'
_HANDLER_DS_KEY = 'datastoreName'
_HANDLER_DATA_ASSET_NAME_KEY = 'dataassetName'
_HANDLER_DATA_ASSET_VERSION_KEY = 'dataassetVersion'

_WS_CONTEXT_SUBS_KEY = 'subscription'
_WS_CONTEXT_RG_KEY = 'resource_group'
_WS_CONTEXT_WS_KEY = 'workspace_name'
_WS_CONTEXT_DS_KEY = 'datastore_name'
_WS_CONTEXT_DA_KEY = 'dataasset_name'
_WS_CONTEXT_DA_VERSION_KEY = 'dataasset_version'
_WS_CONTEXT_REGISTRY_NAME_KEY = 'registry_name'

_REGISTRY_HANDLER = 'AmlRegistry'

# TODO change to new error code from rslex and throw customized user error
_USER_ERROR_MESSAGES = [
    "StreamError(NotFound)", "DataAccessError(NotFound)", "DataAccessError(PermissionDenied)", "OutputError(NotEmpty)",
    "DestinationError(NotEmpty)"]

_USER_ERROR_CODES = ["ScriptExecution.WriteStreams.AlreadyExists"]

_STRING_TO_PYIFDESTINATIONEXISTS = {
    # if find conflict file in destination, wil leave the original file
    "APPEND": PyIfDestinationExists.APPEND,
    # if find conflict file in destination, will raise not empty error
    "FAIL_ON_FILE_CONFLICT": PyIfDestinationExists.FAIL_ON_FILE_CONFLICT,
    # if find conflict file in destination, will overwrite with new file"
    "MERGE_WITH_OVERWRITE": PyIfDestinationExists.MERGE_WITH_OVERWRITE,
}


def _to_py_if_destination_exists(overwrite):
    if not isinstance(overwrite, str):
        raise UserErrorException('The overwrite kwargs should be a string')

    try:
        return _STRING_TO_PYIFDESTINATIONEXISTS[overwrite.upper()]
    except KeyError:
        raise UserErrorException(
            f"Given invalid overwrite kwargs {str(overwrite)}, supported "
            "value are: 'APPEND', 'FAIL_ON_FILE_CONFLICT', "
            "'MERGE_WITH_OVERWRITE'.")


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


def _get_long_form_datastore_uri_path_without_provider(storage_context, relative_path=None):
    subs = storage_context[_WS_CONTEXT_SUBS_KEY]
    rg = storage_context[_WS_CONTEXT_RG_KEY]
    ws = storage_context[_WS_CONTEXT_WS_KEY]
    ds = storage_context[_WS_CONTEXT_DS_KEY]
    if relative_path is not None:
        return f'azureml://subscriptions/{subs}/' \
            f'resourcegroups/{rg}/workspaces/{ws}/' \
            f'datastores/{ds}/paths/{relative_path}'
    else:
        return f'azureml://subscriptions/{subs}/' \
            f'resourcegroups/{rg}/workspaces/{ws}/' \
            f'datastores/{ds}'


def _get_long_form_data_asset_uri_without_provider(storage_context, relative_path=None):
    subs = storage_context[_WS_CONTEXT_SUBS_KEY]
    rg = storage_context[_WS_CONTEXT_RG_KEY]
    ws = storage_context[_WS_CONTEXT_WS_KEY]
    da = storage_context[_WS_CONTEXT_DA_KEY]
    da_version = storage_context[_WS_CONTEXT_DA_VERSION_KEY]
    if relative_path is not None:
        return f'azureml://subscriptions/{subs}/' \
            f'resourcegroups/{rg}/workspaces/{ws}/' \
            f'data/{da}/versions/{da_version}/{relative_path}'
    else:
        return f'azureml://subscriptions/{subs}/' \
            f'resourcegroups/{rg}/workspaces/{ws}/' \
            f'data/{da}/versions/{da_version}'


def _get_long_form_uri_without_provider(handler, storage_context, relative_path=None):
    if handler == _DATASTORE_HANDLER:
        return _get_long_form_datastore_uri_path_without_provider(storage_context, relative_path)
    elif handler == _DATAASSET_HANDLER:
        return _get_long_form_data_asset_uri_without_provider(storage_context, relative_path)
    else:
        raise UserErrorException(f"storage type {handler} is not supported")


class AzureMachineLearningFileSystem(AsyncFileSystem):
    """
    Access Azure Machine Learning defined URI as if it were a file system.
    This exposes a filesystem-like API on top of Azure Machine Learning defined URI

    .. remarks::
        This will enable pandas/dask to load Azure Machine Learning defined URI.

        .. code-block:: python
            # list all the files from a folder
            datastore_uri_fs = AzureMachineLearningFileSystem(uri=
                'azureml://subscriptions/{sub_id}/resourcegroups/{rs_group}/'
                'workspaces/{ws}/datastores/{my_datastore}')
            datastore_uri_fs.ls('folder/')

            # load parquet file to pandas
            import pandas
            df = pandas.read_parquet('azureml://subscriptions/{sub_id}/resourcegroups/{rs_group}/workspaces/{ws}'
                                     '/datastores/workspaceblobstore/paths/myfolder/mydata.parquet')

            # load csv file to pandas
            import pandas
            df = pandas.read_csv('azureml://subscriptions/{sub_id}/resourcegroups/{rs_group}/workspaces/{ws}'
                                 '/datastores/workspaceblobstore/paths/myfolder/mydata.csv')

            # load parquet file to dask
            import dask.dataframe as dd
            df = dd.read_parquet('azureml://subscriptions/{sub_id}/resourcegroups/{rs_group}/workspaces/{ws}'
                                 '/datastores/workspaceblobstore/paths/myfolder/mydata.parquet')

            # load csv file to dask
            import dask.dataframe as dd
            df = dd.read_csv('azureml://subscriptions/{sub_id}/resourcegroups/{rs_group}/workspaces/{ws}'
                             '/datastores/workspaceblobstore/paths/myfolder/mydata.csv')

            # load csv file from registry
            import pandas
            df = pandas.read_csv('azureml://registries/{registry_name}/data/{data_name}/versions/{data_version}'}')

    :param uri: Azure Machine Learning defined URI
        Supports both datastore URIs, data asset URIs, and registry URIs.

        1. Datastore URI Format:
        "azureml://subscriptions/{subscription_id}/resourcegroups/{resource_group}/
        [providers/Microsoft.MachineLearningServices/]workspaces/{workspace}/datastores/{datastore_name}/[paths/{path}]"

        Where:
        - {subscription_id} is the ID of the Azure subscription.
        - {resource_group} is the name of the Azure resource group.
        - {workspace} is the name of the Azure Machine Learning workspace.
        - {datastore_name} is the name of the datastore.
        - [paths/{path}] is an optional segment representing the path within the datastore.

        2. Data Asset URI Format:
        "azureml://subscriptions/{subscription_id}/resourcegroups/{resource_group}/
        [providers/Microsoft.MachineLearningServices/]workspaces/{workspace}/data/{data_name}/[versions/{version}]"

        Where:
        - {subscription_id}, {resource_group}, and {workspace} have the same meanings as above.
        - {data_name} is the name of the data asset.
        - [versions/{version}] is an optional segment representing the version of the data asset.

        Note:
        The segment "providers/Microsoft.MachineLearningServices/" is optional in both URI formats.
        We support URIs both with and without this segment.

        3. Registry URI Format:
        "azureml://registries/{registry_name}/data/{data_name}/versions/{version}"
    :type uri: str
    """

    protocol = "azureml"

    @track(_get_logger, custom_dimensions={'app_name': _APP_NAME})
    def __init__(
            self,
            uri: str = None,
            **kwargs):
        """
        Initialize a new AzureMachineLearningFileSystem object

        :param uri: the uri to initialize AzureMachineLearningFileSystem.
        :type uri: str

        """
        super().__init__(
            asynchronous=False, loop=get_loop()
        )

        from azureml.dataprep.api._datastore_helper import _set_auth_from_dict
        auth_dict = kwargs.get('auth_dict')
        if auth_dict:
            _set_auth_from_dict(auth_dict)
        ml_client = kwargs.get('ml_client')
        if ml_client:
            # this try block is to make sure it is working with older version of dataprep
            try:
                from azureml.dataprep.api._datastore_helper import _set_auth_ml_client
                _set_auth_ml_client(ml_client)
            except Exception as ex:
                error_message = str(ex)
                _LoggerFactory.trace(_get_logger(),
                                     f"failed to set auth with {error_message}, check if update to latest version",
                                     self._workspace_context)
        (self._handler, path_in_fs_root, have_path, self._handler_parameters, self._storage_context) = \
            AzureMachineLearningFileSystem._infer_storage_options(uri)
        self._workspace_context = {}
        for key in [_WS_CONTEXT_SUBS_KEY, _WS_CONTEXT_RG_KEY, _WS_CONTEXT_WS_KEY]:
            self._workspace_context[key] = self._storage_context.get(key, "")

        self._path = uri
        if self._handler != _REGISTRY_HANDLER:
            self._base_long_form_without_provider = \
                self._get_long_form_uri_without_provider(path='')
            if have_path:
                self._path_long_form_without_provider = \
                    self._get_long_form_uri_without_provider(path_in_fs_root)
            else:
                self._path_long_form_without_provider = \
                    self._get_long_form_uri_without_provider()

        self._inspect_caller = ""
        try:
            callstack = inspect.stack()
            stack_count = 0
            for frame in callstack:
                cur_filename = frame.filename
                cur_filename = cur_filename.replace('\\', '/')
                if cur_filename.find('site-packages/pandas') != -1:
                    self._inspect_caller = 'pandas'
                elif cur_filename.find('site-packages/dask') != -1:
                    self._inspect_caller = 'dask'
                stack_count += 1
                if stack_count > 10:
                    break
        except Exception as e:
            _LoggerFactory.trace_warn(_get_logger(),
                                      f"__init__ get inspect caller have exceptions: {e}",
                                      self._workspace_context)

        _LoggerFactory.trace(_get_logger(), "__init__",
                             self._workspace_context)

    @track(_get_logger, custom_dimensions={'app_name': _APP_NAME})
    async def _info(self, path, refresh=True):
        """
        Info api

        :param path: the path to return info for.
        :type path: str
        :param refresh: whether to load it from dircache.
        :type refresh: bool
        :return: A dictionary of file details, returns FileNotFoundError if not exist
        :rtype: dict
        """
        normalized_path = self._strip_protocol(path, self._storage_context)
        parent = self._parent(path)

        if not refresh:
            # try to get it from dir cache
            out = self._ls_from_cache(normalized_path.rstrip('/'))
            if not out:
                return {"name": path, "size": None, "type": "directory"}
            else:
                entries = [
                    f
                    for f in self.dircache[parent]
                    if f["name"] == normalized_path
                ]
                if len(entries) == 0:
                    # parent dir was listed but did not contain this path
                    raise FileNotFoundError(path)
                return entries[0]
        else:
            try:
                # try to list the parent path to return path info
                out = await self._ls(parent, detail=True, refresh=True)

                # the same path might have entry for both file and directory
                entries = [
                    f
                    for f in out
                    if f["name"] in [normalized_path, normalized_path + '/']
                ]

                if len(entries) == 0:
                    raise FileNotFoundError(path)
                return entries[0]
            except Exception as ex:
                raise FileNotFoundError(ex)

    @track(_get_logger, custom_dimensions={'app_name': _APP_NAME})
    async def _exists(self, path):
        """
        exists api

        :param path: the path to return info for.
        :type path: str
        :return: whether a path exists or not
        :rtype: bool
        """
        self._validate_storage_context(path)
        normalized_path = self._strip_protocol(path, self._storage_context)
        parent = self._parent(path)

        # first check ls cache with key path and its parent path
        if self._ls_from_cache(normalized_path.rstrip('/')):
            return True

        out = self._ls_from_cache(parent)
        if out:
            files = [
                f
                for f in out
                if f["name"] == normalized_path
            ]
            if len(files) > 0:
                return True

        try:
            await self._info(path, refresh=True)
            return True
        except FileNotFoundError:
            return False

    @track(_get_logger, custom_dimensions={'app_name': _APP_NAME})
    def glob(self, path=None, **kwargs):
        """
        globbing result for the uri

        :param path: path to glob, it can be long form datastore uri or
                    just relative path in the format of {datastore}/{relative_path}
        :type path: str
        :return: A list of file paths
        :rtype: list[str]
        """
        return sync(self.loop, self._glob, path)

    async def _ls(self, path=None, detail=False, refresh=True, **kwargs):
        """
        List uri, this will return the full list of files iteratively.

        :param path: path to list
        :type path: str
        :param detail: whether to return details other than path
        :type detail: bool
        :param refresh: whether to just list for dircache
        :type refresh: bool
        :return: A list of file paths if detail is False, else returns a list of dict
        :rtype: list[str] or list[dict]
        """
        custom_dimensions = {'app_name': _APP_NAME}
        custom_dimensions.update(self._workspace_context)

        with _LoggerFactory.track_activity(_get_logger(), '_ls', _PUBLIC_API,
                                           custom_dimensions) as activityLogger:
            try:
                ensure_rslex_environment()

                if self._handler == _REGISTRY_HANDLER:
                    if not path:
                        path = self._path
                else:
                    if not path:
                        path = self._path_long_form_without_provider
                    self._validate_storage_context(path)
                    path = self._strip_protocol(path, self._storage_context)
                    path = AzureMachineLearningFileSystem.to_absolute_path(path)
                    path = f'{self._base_long_form_without_provider}{path}'

                    if not refresh:
                        try:
                            return self._ls_from_cache(path)
                        except KeyError:
                            raise FileNotFoundError

                uri_accessor = UriAccessor()
                list_results = []
                # list result might have the same path for file and directory, but directory will have ending / in path
                entrys = uri_accessor.list_directory(path)

                for entry in entrys:
                    list_results.append({
                        'name': AzureMachineLearningFileSystem._entry_resource_id_to_path_in_fs(
                            entry.resource_identifier, self._handler, self._handler_parameters, self._path),
                        'type': entry.type_string,
                        'size': None if entry.type_string == 'directory' else entry.file_attributes.get_value('size')
                    })

                self.dircache[path] = list_results
                return self.dircache[path] if detail else sorted([o["name"] for o in self.dircache[path]])
            except Exception as e:
                if hasattr(activityLogger, ACTIVITY_INFO_KEY):
                    activityLogger.activity_info['error_code'] = getattr(
                        e, ERROR_CODE_KEY, '')
                    activityLogger.activity_info['message'] = getattr(
                        e, COMPLIANT_MESSAGE_KEY, str(e))
                    activityLogger.activity_info['outer_error_code'] = getattr(
                        e, OUTER_ERROR_CODE_KEY, '')

                _reclassify_rslex_error(e)

    async def _open(
            self,
            path: str = None,
            mode: str = 'rb',
            **kwargs,
    ):
        """
        Open a file from a datastore uri

        :param path: the path to open, default to the first file
        :type path: str
        :param mode: mode to open the file, supported modes are ['r', 'rb'], both means read byte
        :type mode: str
        :return: OpenFile
        :rtype: OpenFile
        """

        """Open a file from a datastore uri

        Parameters
        ----------
        path: str
            Path to file to open, result returned from ls() or glob()
        """
        custom_dimensions = {'app_name': _APP_NAME, 'inspect_caller': self._inspect_caller}
        custom_dimensions.update(self._workspace_context)

        memory_cache_size = 2 * 1024 * 1024 * 1024
        read_threads = 64
        _FS_DOWNLOAD_MEMORY_CACHE_SIZE = '_FS_DOWNLOAD_MEMORY_CACHE_SIZE'
        if _FS_DOWNLOAD_MEMORY_CACHE_SIZE in os.environ:
            memory_cache_size = os.environ[_FS_DOWNLOAD_MEMORY_CACHE_SIZE]

        _FS_DOWNLOAD_READ_THREADS = '_FS_DOWNLOAD_READ_THREADS'
        if _FS_DOWNLOAD_READ_THREADS in os.environ:
            read_threads = os.environ[_FS_DOWNLOAD_READ_THREADS]

        with _LoggerFactory.track_activity(_get_logger(), '_open', _PUBLIC_API,
                                           custom_dimensions) as activityLogger:
            try:
                ensure_rslex_environment()
                self._validate_args_for_open(mode)

                if self._handler == _REGISTRY_HANDLER:
                    if not path:
                        path = self._path
                else:
                    if not path:
                        path = self._path_long_form_without_provider
                self._validate_storage_context(path)
                path = self._strip_protocol(path, self._storage_context)
                path = AzureMachineLearningFileSystem._path_in_fs_root_to_resource_id(
                    path, self._handler, self._storage_context)

                si = StreamInfo(
                    self._handler, path, self._handler_parameters)

                downloader = Downloader(block_size=8 * 1024 * 1024, read_threads=read_threads,
                                        caching_options=CachingOptions(memory_cache_size=memory_cache_size))
                return si.open(buffering_options=BufferingOptions(64, downloader))
            except Exception as e:
                if hasattr(activityLogger, ACTIVITY_INFO_KEY):
                    activityLogger.activity_info['error_code'] = getattr(
                        e, ERROR_CODE_KEY, '')
                    activityLogger.activity_info['message'] = getattr(
                        e, COMPLIANT_MESSAGE_KEY, str(e))
                    activityLogger.activity_info['outer_error_code'] = getattr(
                        e, OUTER_ERROR_CODE_KEY, '')

                _reclassify_rslex_error(e)

    @track(_get_logger, custom_dimensions={'app_name': _APP_NAME})
    async def _expand_path(self, path, recursive=False, maxdepth=None):
        if isinstance(path, str):
            out = await self._expand_path([path], recursive, maxdepth)
        else:
            # reduce depth on each recursion level unless None or 0
            maxdepth = maxdepth if not maxdepth else maxdepth - 1
            out = set()
            path = [self._strip_protocol(
                p, self._storage_context) for p in path]
            for p in path:  # can gather here
                if has_magic(p):
                    bit = set(await self._glob(p))
                    out |= bit
                    continue
                elif recursive:
                    rec = set(await self._find(p, maxdepth=maxdepth, withdirs=False))
                    out |= rec
                if (not out or p not in out) and recursive is False:
                    # should only check once, for the root
                    out.add(p)
        if not out:
            raise FileNotFoundError(path)
        return list(sorted(out))

    @track(_get_logger, custom_dimensions={'app_name': _APP_NAME})
    def get(self, rpath, lpath, recursive=False, callback=_DEFAULT_CALLBACK, **kwargs):
        """Copy file(s) to local."""
        return sync(self.loop, self._get, rpath, lpath, recursive, callback, **kwargs)

    async def _get(
            self, rpath, lpath, recursive=False, callback=_DEFAULT_CALLBACK, **kwargs
    ):
        """Copy file(s) to local.

        Copies a specific file or tree of files (if recursive=True). If lpath
        ends with a "/", it will be assumed to be a directory, and target files
        will go within. Can submit a list of paths, which may be glob-patterns
        and will be expanded.

        The get_file method will be called concurrently on a batch of files. The
        batch_size option can configure the amount of futures that can be executed
        at the same time. If it is -1, then all the files will be uploaded concurrently.
        The default can be set for this instance by passing "batch_size" in the
        constructor, or for all instances by setting the "gather_batch_size" key
        in ``fsspec.config.conf``, falling back to 1/8th of the system limit .
        """
        custom_dimensions = {'app_name': _APP_NAME}
        custom_dimensions.update(self._workspace_context)

        with _LoggerFactory.track_activity(_get_logger(), '_get', _PUBLIC_API,
                                           custom_dimensions) as activityLogger:
            try:
                ensure_rslex_environment()
                lpath = make_path_posix(lpath)
                overwrite = kwargs.get('overwrite', "FAIL_ON_FILE_CONFLICT")
                if_destination_exists = _to_py_if_destination_exists(overwrite)
                if self._handler == _REGISTRY_HANDLER:
                    download_location = PyLocationInfo('Local', lpath, {})
                    Copier.copy_uri(download_location, rpath, if_destination_exists, "")
                else:
                    self._validate_storage_context(rpath)
                    rpath = self._strip_protocol(rpath, self._storage_context)
                    if (await self._info(rpath))["type"] == "file" and recursive is True:
                        raise UserErrorException("rpath type of single file should not use recursive download")
                    rpaths = await self._expand_path(rpath, recursive=recursive)
                    rpath = AzureMachineLearningFileSystem._path_in_fs_root_to_resource_id(
                        rpath, self._handler, self._storage_context)
                    # needs to get parent folder if its download single file as base dir
                    base_dir = rpath if len(
                        rpaths) > 1 or recursive else self._parent(rpath)
                    kwargs.update({'base_dir': base_dir})
                    copier = Copier(PyLocationInfo('Local', lpath, {}),
                                    base_dir, if_destination_exists)
                    copier.copy_volume(PyLocationInfo(self._handler, rpath, self._handler_parameters), '')
            except Exception as e:
                if hasattr(activityLogger, ACTIVITY_INFO_KEY):
                    activityLogger.activity_info['error_code'] = getattr(
                        e, ERROR_CODE_KEY, '')
                    activityLogger.activity_info['message'] = getattr(
                        e, COMPLIANT_MESSAGE_KEY, str(e))
                    activityLogger.activity_info['outer_error_code'] = getattr(
                        e, OUTER_ERROR_CODE_KEY, '')

                _reclassify_rslex_error(e)

    async def _get_file(self, rpath, lpath, overwrite="FAIL_ON_FILE_CONFLICT", callback=_DEFAULT_CALLBACK, **kwargs):
        """
        Copy single file remote to local
        :param lpath: Path to local file
        :param rpath: Path to remote file, rpath is in the format of {datastore_name}/{relative_path}
        :param overwrite: string. Suppurts values "APPEND", "FAIL_ON_FILE_CONFLICT", "MERGE_WITH_OVERWRITE".
        """
        custom_dimensions = {'app_name': _APP_NAME}
        custom_dimensions.update(self._workspace_context)

        with _LoggerFactory.track_activity(_get_logger(), '_get_file', _PUBLIC_API,
                                           custom_dimensions) as activityLogger:
            overwrite = _to_py_if_destination_exists(overwrite)

            try:
                ensure_rslex_environment()
                base_dir = kwargs.get('base_dir', None)

                copier = Copier(PyLocationInfo('Local', lpath, {}),
                                base_dir, overwrite)
                si = StreamInfo(_DATASTORE_HANDLER, rpath,
                                self._handler_parameters)
                copier.copy_stream_info(si, '')
            except Exception as e:
                if hasattr(activityLogger, ACTIVITY_INFO_KEY):
                    activityLogger.activity_info['error_code'] = getattr(
                        e, ERROR_CODE_KEY, '')
                    activityLogger.activity_info['message'] = getattr(
                        e, COMPLIANT_MESSAGE_KEY, str(e))
                    activityLogger.activity_info['outer_error_code'] = getattr(
                        e, OUTER_ERROR_CODE_KEY, '')

                _reclassify_rslex_error(e)

    @track(_get_logger, custom_dimensions={'app_name': _APP_NAME})
    def put(self, lpath, rpath, recursive=False, callback=_DEFAULT_CALLBACK, **kwargs):
        """Copy file(s) to local."""
        return sync(self.loop, self._put, lpath, rpath, recursive, callback, **kwargs)

    async def _put(
            self,
            lpath,
            rpath,
            recursive=False,
            callback=_DEFAULT_CALLBACK,
            batch_size=None,
            **kwargs,
    ):
        """Copy file(s) from local.

        Copies a specific file or tree of files (if recursive=True). If rpath
        ends with a "/", it will be assumed to be a directory, and target files
        will go within.

        The put_file method will be called concurrently on a batch of files. The
        batch_size option can configure the amount of futures that can be executed
        at the same time. If it is -1, then all the files will be uploaded concurrently.
        The default can be set for this instance by passing "batch_size" in the
        constructor, or for all instances by setting the "gather_batch_size" key
        in ``fsspec.config.conf``, falling back to 1/8th of the system limit .
        """
        custom_dimensions = {'app_name': _APP_NAME}
        custom_dimensions.update(self._workspace_context)
        overwrite = kwargs.get('overwrite', "FAIL_ON_FILE_CONFLICT")
        if_destination_exists = _to_py_if_destination_exists(overwrite)

        with _LoggerFactory.track_activity(_get_logger(), '_put', _PUBLIC_API,
                                           custom_dimensions) as activityLogger:
            try:
                if self._handler == _DATAASSET_HANDLER:
                    raise UserErrorException(f'storage type {self._handler} does not support download')
                if not rpath:
                    rpath = self._path_long_form_without_provider
                    # append ending / to indicate its a directory
                self._validate_storage_context(rpath)
                rpath = self._strip_protocol(rpath, self._storage_context)
                rpath = AzureMachineLearningFileSystem._path_in_fs_root_to_resource_id(
                    rpath, self._handler, self._storage_context)
                rpath = rpath.rstrip('/') + '/'
                if isinstance(lpath, str):
                    lpath = make_path_posix(lpath)

                ensure_rslex_environment()
                lpath = os.path.abspath(lpath)
                lpath = lpath.replace('\\', '/')
                base_path = lpath
                if not os.path.isdir(lpath):
                    base_path = self._parent(lpath)

                copier = Copier(PyLocationInfo(self._handler, rpath, self._handler_parameters),
                                base_path, if_destination_exists)
                copier.copy_volume(PyLocationInfo('Local', lpath, {}), '')
            except Exception as e:
                if hasattr(activityLogger, ACTIVITY_INFO_KEY):
                    activityLogger.activity_info['error_code'] = getattr(
                        e, ERROR_CODE_KEY, '')
                    activityLogger.activity_info['message'] = getattr(
                        e, COMPLIANT_MESSAGE_KEY, str(e))
                    activityLogger.activity_info['outer_error_code'] = getattr(
                        e, OUTER_ERROR_CODE_KEY, '')

                _reclassify_rslex_error(e)

    async def _put_file(
            self, lpath, rpath, overwrite="FAIL_ON_FILE_CONFLICT", callback=_DEFAULT_CALLBACK, **kwargs
    ):
        """
        Copy single file to remote
        :param lpath: Path to local file
        :param rpath: Path to remote file, rpath is in the format of {datastore_name}/{relative_path}
        :param overwrite: string. Suppurts values "APPEND", "FAIL_ON_FILE_CONFLICT", "MERGE_WITH_OVERWRITE".
        :param callback: callback function
        """
        custom_dimensions = {'app_name': _APP_NAME}
        custom_dimensions.update(self._workspace_context)
        with _LoggerFactory.track_activity(_get_logger(), '_put_file', _PUBLIC_API,
                                           custom_dimensions) as activityLogger:
            overwrite = _to_py_if_destination_exists(overwrite)

            try:
                # rpath has the remote file name, copy_stream_info expects folder
                rpath = self._parent(rpath)
                ensure_rslex_environment()
                destination_info = PyLocationInfo(
                    _DATASTORE_HANDLER,
                    rpath,
                    self._handler_parameters)

                # get abspath and replace '\' to '/'
                lpath = os.path.abspath(lpath)
                lpath = lpath.replace('\\', '/')

                copier = Copier(destination_info, self._parent(lpath), overwrite)

                source_stream_info = StreamInfo('Local', lpath, {})
                copier.copy_stream_info(source_stream_info, '')
            except Exception as e:
                if hasattr(activityLogger, ACTIVITY_INFO_KEY):
                    activityLogger.activity_info['error_code'] = getattr(
                        e, ERROR_CODE_KEY, '')
                    activityLogger.activity_info['message'] = getattr(
                        e, COMPLIANT_MESSAGE_KEY, str(e))
                    activityLogger.activity_info['outer_error_code'] = getattr(
                        e, OUTER_ERROR_CODE_KEY, '')

                _reclassify_rslex_error(e)

    @track(_get_logger, custom_dimensions={'app_name': _APP_NAME})
    def _validate_args_for_open(self, mode):
        supported_modes = ['r', 'rb']
        if mode not in supported_modes:
            raise UserErrorException(
                f'Invalid mode {mode}, supported modes are {supported_modes}, both means read as byte array')

    def _parent(self, path):
        self._validate_storage_context(path)
        path = self._strip_protocol(path.rstrip("/"), self._storage_context)
        if "/" in path:
            # path.rsplit("/", 1)[0].lstrip("/")
            return path.rsplit("/", 1)[0]
        # root path of datastore, eg: workspaceblobstore/
        else:
            return "/"

    def _ls_from_cache(self, path: str):
        """Check cache for listing

        Returns listing, if found (may me empty list for a directly that exists
        but contains nothing), None if not in cache.

        Override the default implementation in fsspec because we need to append ending / to indicate its a directory
        """
        if path.rstrip("/") in self.dircache:
            return self.dircache[path.rstrip("/")]

    @staticmethod
    def _infer_storage_options(path: str):
        # shorthand_datastore_uri
        # f'azureml://datastores/{datastore_name}/paths/{path_to_file}/'
        # longform_datastore_uri_without_provider
        # f'azureml://subscriptions/{subscription_id}/resourcegroups/{resource_group}/ \'
        # f'workspaces/{workspace}/datastores/{datastore_name}/paths/{path_to_file}/'
        # longform_datastore_uri_with_provider
        # f'azureml://subscriptions/{subscription_id}/resourcegroups/{resource_group}/ \'
        # f'providers/Microsoft.MachineLearningServices/workspaces/{workspace}/' \
        # f'datastores/{datastore_name}/paths/{path_to_file}/'

        # shorthand_named_asset_uri
        # f'azureml:{data_name}:{version}'
        # longform_named_asset_uri_without_provider
        # f'azureml://subscriptions/{subscription_id}/resourcegroups/{resource_group}/' \
        # f'workspaces/{workspace}/data/{data_name}/versions/{version}'
        # longform_named_asset_uri_with_provider
        # f'azureml://subscriptions/{subscription_id}/resourcegroups/{resource_group}/' \
        # f'providers/Microsoft.MachineLearningServices/workspaces/{workspace}/' \
        # f'data/{data_name}/versions/{version}'

        # TODO: add shorthand_uri after supporting (datastore, named_asset)

        _datastore_longform_uri_path_regex_pattern = re.compile(
            r'^azureml://subscriptions/([^\/]+)/resourcegroups/([^\/]+)/'
            r'(?:providers/Microsoft.MachineLearningServices/)?workspaces/([^\/]+)/'
            r'datastores/([^\/]+)/paths/(.*)',
            re.IGNORECASE)

        _datastore_longform_uri_regex_pattern = re.compile(
            r'^azureml://subscriptions/([^\/]+)/resourcegroups/([^\/]+)/'
            r'(?:providers/Microsoft.MachineLearningServices/)?workspaces/([^\/]+)/'
            r'datastores/([^\/]+)', re.IGNORECASE)

        _named_asset_longform_uri_regex_pattern = re.compile(
            r'^azureml://subscriptions/([^\/]+)/resourcegroups/([^\/]+)/'
            r'(?:providers/Microsoft.MachineLearningServices/)?workspaces/([^\/]+)/'
            r'data/([^\/]+)/versions/([^\/]+)$', re.IGNORECASE)

        _registry_uri_regex_pattern = re.compile(
            r'^azureml://registries/([^\/]+)/data/([^\/]+)/versions/([^\/]+)',
            re.IGNORECASE)
        _registry_uri_match = _registry_uri_regex_pattern.match(path)

        #  TODO: add shorthand_uri after supporting (datastore, named_asset)
        _datastore_longform_uri_path_match = _datastore_longform_uri_path_regex_pattern.match(path)
        _datastore_longform_uri_match = _datastore_longform_uri_regex_pattern.match(path)
        _named_asset_longform_uri_match = _named_asset_longform_uri_regex_pattern.match(path)

        #  TODO: include short-hand uri match after supporting
        if _datastore_longform_uri_path_match or _datastore_longform_uri_match:
            handler = _DATASTORE_HANDLER
            if _datastore_longform_uri_path_match:
                datastore_handler_info = {
                    _HANDLER_SUBS_KEY: _datastore_longform_uri_path_match[1],
                    _HANDLER_RG_KEY: _datastore_longform_uri_path_match[2],
                    _HANDLER_WS_KEY: _datastore_longform_uri_path_match[3],
                    _HANDLER_DS_KEY: _datastore_longform_uri_path_match[4],
                }
                storage_context = {
                    _WS_CONTEXT_SUBS_KEY: datastore_handler_info.get(_HANDLER_SUBS_KEY),
                    _WS_CONTEXT_RG_KEY: datastore_handler_info.get(_HANDLER_RG_KEY),
                    _WS_CONTEXT_WS_KEY: datastore_handler_info.get(_HANDLER_WS_KEY),
                    _WS_CONTEXT_DS_KEY: datastore_handler_info.get(_HANDLER_DS_KEY),
                }
                path_in_fs_root = _datastore_longform_uri_path_match[5]
                have_path = True
                return (handler, path_in_fs_root, have_path, datastore_handler_info, storage_context)
            elif _datastore_longform_uri_match:
                datastore_handler_info = {
                    _HANDLER_SUBS_KEY: _datastore_longform_uri_match[1],
                    _HANDLER_RG_KEY: _datastore_longform_uri_match[2],
                    _HANDLER_WS_KEY: _datastore_longform_uri_match[3],
                    _HANDLER_DS_KEY: _datastore_longform_uri_match[4],
                }
                storage_context = {
                    _WS_CONTEXT_SUBS_KEY: datastore_handler_info.get(_HANDLER_SUBS_KEY),
                    _WS_CONTEXT_RG_KEY: datastore_handler_info.get(_HANDLER_RG_KEY),
                    _WS_CONTEXT_WS_KEY: datastore_handler_info.get(_HANDLER_WS_KEY),
                    _WS_CONTEXT_DS_KEY: datastore_handler_info.get(_HANDLER_DS_KEY),
                }
                path_in_fs_root = '/'
                have_path = False
                return (handler, path_in_fs_root, have_path, datastore_handler_info, storage_context)
        elif _named_asset_longform_uri_match:
            handler = _DATAASSET_HANDLER
            named_asset_handler_info = {}
            storage_context = {
                _WS_CONTEXT_SUBS_KEY: _named_asset_longform_uri_match[1],
                _WS_CONTEXT_RG_KEY: _named_asset_longform_uri_match[2],
                _WS_CONTEXT_WS_KEY: _named_asset_longform_uri_match[3],
                _WS_CONTEXT_DA_KEY: _named_asset_longform_uri_match[4],
                _WS_CONTEXT_DA_VERSION_KEY: _named_asset_longform_uri_match[5],
            }
            path_in_fs_root = '/'
            have_path = False
            return (handler, path_in_fs_root, have_path, named_asset_handler_info, storage_context)
        elif _registry_uri_match:
            handler = _REGISTRY_HANDLER
            registry_handler_info = {}
            storage_context = {
                _WS_CONTEXT_REGISTRY_NAME_KEY: _registry_uri_match[0],
                _WS_CONTEXT_DA_KEY: _registry_uri_match[1],
                _WS_CONTEXT_DA_VERSION_KEY: _registry_uri_match[2],
            }
            path_in_fs_root = ''
            have_path = False
            return (handler, path_in_fs_root, have_path, registry_handler_info, storage_context)
        else:
            # TODO: include short-hand uri match after supporting
            raise UserErrorException(f'{path} is not a valid datastore uri, data asset uri, or registry uri.'
                                     'A datastore URI has this format: '
                                     'azureml://subscriptions/{subscription}/resourcegroups/{resource_group}/'
                                     'workspaces/{workspace}/datastores/{datastore_name}/paths/{path_on_datastore}.'
                                     'A data asset URI has this format: '
                                     'azureml://subscriptions/{subscription}/resourcegroups/{resource_group}/'
                                     'workspaces/{workspace}/data/{data_asset_name}/'
                                     'versions/{version}.'
                                     'A registry URI has this format: '
                                     'azureml://registries/{registry_name}/data/{data_name}/versions/{version}/'
                                     'See https://aka.ms/azureml-fsspec for more details.'
                                     )

    @staticmethod
    def to_absolute_path(path: str):
        """Convert relative path in filesystem root to absolute path"""
        path = path.strip("/")
        path = os.path.normpath(path)
        path = path.replace('\\', '/')
        while path.startswith("../"):
            path = path[3:]
        if path.startswith(".."):
            path = path[2:]
        if path.startswith("."):
            path = path[1:]
        return path

    @staticmethod
    def _path_in_fs_root_to_resource_id(path: str, handler: str, storage_context: dict):
        '''
        path: path in root of filesystem
        return resource_id that is used in rslex StreamInfo, destination_info, etc. for given handler type
        '''
        path = AzureMachineLearningFileSystem.to_absolute_path(path)

        if handler == _DATASTORE_HANDLER:
            return f"{storage_context[_WS_CONTEXT_DS_KEY]}/{path}"
        if handler == _REGISTRY_HANDLER:
            # return registry uri
            def get_registry_uri(registry_name, data_name, version, path):
                return f'azureml://registries/{registry_name}/data/{data_name}/versions/{version}/{path}'
            return get_registry_uri(
                storage_context[_WS_CONTEXT_REGISTRY_NAME_KEY],
                storage_context[_WS_CONTEXT_DA_KEY],
                storage_context[_WS_CONTEXT_DA_VERSION_KEY],
                path
            )
        elif handler == _DATAASSET_HANDLER:
            schema_path = f'{handler}://{storage_context.get(_WS_CONTEXT_SUBS_KEY)}/' \
                f'{storage_context.get(_WS_CONTEXT_RG_KEY)}/' \
                f'{storage_context.get(_WS_CONTEXT_WS_KEY)}/' \
                f'data/{storage_context.get(_WS_CONTEXT_DA_KEY)}/' \
                f'versions/{storage_context.get(_WS_CONTEXT_DA_VERSION_KEY)}' \
                f'/{path}'
            return schema_path
        else:
            raise UserErrorException(f'storage type {handler} is not supported')

    @staticmethod
    def _entry_resource_id_to_path_in_fs(entry_resource_id, handler, handler_parameters, path):
        if handler == _DATASTORE_HANDLER:
            return entry_resource_id[len(handler_parameters[_HANDLER_DS_KEY]) + 1:]
        elif handler == _REGISTRY_HANDLER:
            return entry_resource_id[len(path) + 1:]
        elif handler == _DATAASSET_HANDLER:
            # create a _named_asset_schema_path_regex_pattern
            # AmlDataAsset://{subs}/{rg}/{ws}/data/{data_name}/versions/{version}/{path}
            # where versions/{version} and {path} are optional pattern
            _named_asset_scheme_path_regex_pattern = re.compile(
                r'^AmlDataAsset://([^\/]+)/([^\/]+)/([^\/]+)/data/([^\/]+)/'
                r'(?:(?:versions/([^\/]+))?(?:/(.*))?)?$',
                re.IGNORECASE
            )
            _named_asset_scheme_path_match = _named_asset_scheme_path_regex_pattern.match(entry_resource_id)
            if _named_asset_scheme_path_match:
                subs, rg, ws, data_name, version, path = _named_asset_scheme_path_match.groups()
                if not path:
                    path = '/'
                return path
            else:
                raise UserErrorException(
                    f'directory entry path {entry_resource_id} is not a valid named asset scheme path')
        else:
            raise UserErrorException(f'storage type {handler} is not supported')

    @staticmethod
    def _get_kwargs_from_urls(path):
        """ Directly return the path """
        out = {}
        out["uri"] = path
        return out

    @staticmethod
    def _map_user_error(ex):
        if any(msg in ex.args[0] for msg in _USER_ERROR_MESSAGES) \
                or (isinstance(ex, ExecutionError)
                    and any(ex.error_code in error_code for error_code in _USER_ERROR_CODES)):
            raise UserErrorException(ex.args[0])
        raise ex

    def _validate_storage_context(self, path: str, storage_context=None):
        """
        Turn path from fully-qualified to file-system-specific
        return myfolder/mydata.parquet for
            'azureml://subscriptions/{sub_id}/resourcegroups/{rs_group}/workspaces/{ws}/'
            'datastores/{datastore_name}/paths/myfolder/mydata.parquet'
        """
        if path.startswith(self.__class__.protocol + "://"):
            (handler, path_in_fs_root, have_path, handler_parameters, this_storage_context) = \
                AzureMachineLearningFileSystem._infer_storage_options(path)
            if handler != self._handler:
                raise UserErrorException(
                    'Please create new file system instance for different storage operations')
            # shorten the line for pylint
            this_wc = this_storage_context
            wc = storage_context if storage_context is not None \
                else self._storage_context

            if handler == _DATASTORE_HANDLER and \
                    (this_wc[_WS_CONTEXT_SUBS_KEY] != wc[_WS_CONTEXT_SUBS_KEY]
                     or this_wc[_WS_CONTEXT_RG_KEY] != wc[_WS_CONTEXT_RG_KEY]
                     or this_wc[_WS_CONTEXT_WS_KEY] != wc[_WS_CONTEXT_WS_KEY]
                     or this_wc[_WS_CONTEXT_DS_KEY] != wc[_WS_CONTEXT_DS_KEY]):
                raise UserErrorException(
                    'Please create new file system instance for different workspace or storage operations')

            if handler == _DATAASSET_HANDLER and \
                    (this_wc[_WS_CONTEXT_SUBS_KEY] != wc[_WS_CONTEXT_SUBS_KEY]
                     or this_wc[_WS_CONTEXT_RG_KEY] != wc[_WS_CONTEXT_RG_KEY]
                     or this_wc[_WS_CONTEXT_WS_KEY] != wc[_WS_CONTEXT_WS_KEY]
                     or this_wc[_WS_CONTEXT_DA_KEY] != wc[_WS_CONTEXT_DA_KEY]
                     or this_wc[_WS_CONTEXT_DA_VERSION_KEY] != wc[_WS_CONTEXT_DA_VERSION_KEY]):
                raise UserErrorException(
                    'Please create new file system instance for different workspace or storage operations')
            # TODO: decide whether add registry handler validation or not

    @classmethod
    def _strip_protocol(cls, path: str, storage_context=None):
        """
        Turn path from fully-qualified to file-system-specific
        return myfolder/mydata.parquet for
            'azureml://subscriptions/{sub_id}/resourcegroups/{rs_group}/workspaces/{ws}/'
            'datastores/{datastore_name}/paths/myfolder/mydata.parquet'
        """
        if path.startswith(cls.protocol + "://"):
            (handler, path_in_fs_root, _, _, _) = \
                AzureMachineLearningFileSystem._infer_storage_options(path)
            if handler == _DATASTORE_HANDLER or handler == _DATAASSET_HANDLER or handler == _REGISTRY_HANDLER:
                return path_in_fs_root
            else:
                raise UserErrorException(f'storage type {handler} is not supported')
        else:
            return path

    def _get_long_form_uri_without_provider(self, path: str=None):
        """
        Turn path from file-system-specific to fully-qualified without-provider long-form uri
        e.g. for path in datastore filesystem,
        return 'azureml://subscriptions/{sub_id}/resourcegroups/{rs_group}/workspaces/{ws}/'
            'datastores/{datastore_name}/paths/myfolder/mydata.parquet' for
            myfolder/mydata.parquet
        """
        if path is not None:
            path = AzureMachineLearningFileSystem.to_absolute_path(path)
        return _get_long_form_uri_without_provider(self._handler, self._storage_context, path)

    @staticmethod
    def _other_paths(paths, path2, is_dir=None, exists=False):
        def common_prefix(paths):
            """For a list of paths, find the shortest prefix common to all"""
            parts = [p.split("/") for p in paths]
            lmax = min(len(p) for p in parts)
            end = 0
            for i in range(lmax):
                end = all(p[i] == parts[0][i] for p in parts)
                if not end:
                    break
            i += end
            return "/".join(parts[0][:i])

        if isinstance(path2, str):
            is_dir = is_dir or path2.endswith("/")
            path2 = path2.rstrip("/")
            if len(paths) > 1:
                cp = common_prefix(paths)
                if exists:
                    cp = cp.rsplit("/", 1)[0]
                path2 = [p.replace(cp, path2, 1) for p in paths]
            else:
                if is_dir:
                    path2 = [path2.rstrip("/") + "/" + paths[0].rsplit("/")[-1]]
                else:
                    path2 = [path2]
        else:
            assert len(paths) == len(path2)
        return path2
