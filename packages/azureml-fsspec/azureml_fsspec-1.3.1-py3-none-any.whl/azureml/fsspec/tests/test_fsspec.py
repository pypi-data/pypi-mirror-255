# test cases cover _infer_storage_options, _path_in_fs_root_to_resource_id, _entry_resource_id_to_path_in_fs
# methods not sure whether add tests: _infer_storage_options_for_new_path, _strip_protocol

import pytest
from azureml.fsspec import AzureMachineLearningFileSystem, \
    _DATASTORE_HANDLER, _DATAASSET_HANDLER, \
    _HANDLER_SUBS_KEY, _HANDLER_RG_KEY, _HANDLER_WS_KEY, _HANDLER_DS_KEY, \
    _WS_CONTEXT_SUBS_KEY, _WS_CONTEXT_RG_KEY, _WS_CONTEXT_WS_KEY, _WS_CONTEXT_DS_KEY, \
    _WS_CONTEXT_DA_KEY, _WS_CONTEXT_DA_VERSION_KEY
from azureml.fsspec.spec import _get_long_form_uri_without_provider
from azureml.dataprep import UserErrorException


@pytest.mark.fsspec_unit_test
@pytest.mark.fsspec_unit_test_local_dprep
class TestAzureMachineLearningFileSystem:

    # test __init__ create valid path variable
    # test cases, datastore, data asset, registry
    def test_init_create_valid_path_variable(self):
        path_in_fs_root = 'myfolder/mydata.csv'
        datastore_longform_no_path_uri = 'azureml://subscriptions/subs/resourcegroups/rg/workspaces/ws/' \
            'datastores/ds'
        datastore_base_longform_without_provider = f'{datastore_longform_no_path_uri}/paths/'
        datastore_longform_path_uri = f'{datastore_longform_no_path_uri}/paths/{path_in_fs_root}'

        assert datastore_longform_path_uri == f'{datastore_base_longform_without_provider}{path_in_fs_root}'

        datastore_fs = AzureMachineLearningFileSystem(datastore_longform_no_path_uri)
        assert datastore_fs._path == datastore_longform_no_path_uri
        assert datastore_fs._path_long_form_without_provider == datastore_longform_no_path_uri
        assert datastore_fs._base_long_form_without_provider == datastore_base_longform_without_provider

        datastore_fs = AzureMachineLearningFileSystem(datastore_base_longform_without_provider + '')
        assert datastore_fs._path == datastore_base_longform_without_provider + ''
        assert datastore_fs._path_long_form_without_provider == datastore_base_longform_without_provider + ''
        assert datastore_fs._base_long_form_without_provider == datastore_base_longform_without_provider

        datastore_fs = AzureMachineLearningFileSystem(datastore_longform_path_uri)
        assert datastore_fs._path == datastore_longform_path_uri
        assert datastore_fs._path_long_form_without_provider == datastore_longform_path_uri
        assert datastore_fs._base_long_form_without_provider == datastore_base_longform_without_provider

        dataasset_longform_no_path_uri = 'azureml://subscriptions/subs/resourcegroups/rg/workspaces/ws/' \
            'data/my_data_asset/versions/1'
        dataasset_base_longform_without_provider = f'{dataasset_longform_no_path_uri}/'

        dataasset_fs = AzureMachineLearningFileSystem(dataasset_longform_no_path_uri)
        assert dataasset_fs._path == dataasset_longform_no_path_uri
        assert dataasset_fs._path_long_form_without_provider == dataasset_longform_no_path_uri
        assert dataasset_fs._base_long_form_without_provider == dataasset_base_longform_without_provider

        # registry currently not using following variables so skip testing
        # self._path_long_form_without_provider and self._base_long_form_without_provider
        registry_longform_no_path_uri = 'azureml://registries/UnsecureTest-fsspec/data/testfile/versions/1'
        registry_fs = AzureMachineLearningFileSystem(registry_longform_no_path_uri)
        assert registry_fs._path == registry_longform_no_path_uri

    # test _infer_storage_options
    # datastore long-form uri path should succeed to return results
    def test_infer_storage_options_datastore_longform_uri_path(self):
        expected_handler = _DATASTORE_HANDLER
        expected_path_in_fs_root = 'myfolder/mydata.csv'
        subs = 'subs'
        rg = 'rg'
        ws = 'ws'
        ds = 'ds'

        path = f'azureml://subscriptions/{subs}/resourcegroups/{rg}/workspaces/{ws}/' \
            f'datastores/{ds}/paths/{expected_path_in_fs_root}'
        expected_handler_parameters = {
            _HANDLER_SUBS_KEY: subs,
            _HANDLER_RG_KEY: rg,
            _HANDLER_WS_KEY: ws,
            _HANDLER_DS_KEY: ds,
        }
        expected_storage_context = {
            _WS_CONTEXT_SUBS_KEY: subs,
            _WS_CONTEXT_RG_KEY: rg,
            _WS_CONTEXT_WS_KEY: ws,
            _WS_CONTEXT_DS_KEY: ds,
        }
        handler, path_in_fs_root, have_path, handler_parameters, storage_context = \
            AzureMachineLearningFileSystem._infer_storage_options(path)
        assert handler == expected_handler
        assert path_in_fs_root == expected_path_in_fs_root
        assert have_path is True
        assert handler_parameters == expected_handler_parameters
        assert storage_context == expected_storage_context

    # data asset long-form uri should succeed to return results
    def test_infer_storage_options_data_asset_longform_uri(self):
        expected_handler = _DATAASSET_HANDLER
        expected_path_in_fs_root = '/'
        subs = 'subs'
        rg = 'rg'
        ws = 'ws'
        data = 'my_data_asset'
        version = '1'

        path = f'azureml://subscriptions/{subs}/resourcegroups/{rg}/workspaces/{ws}/' \
            f'data/{data}/versions/{version}'
        expected_handler_parameters = {}
        expected_storage_context = {
            _WS_CONTEXT_SUBS_KEY: subs,
            _WS_CONTEXT_RG_KEY: rg,
            _WS_CONTEXT_WS_KEY: ws,
            _WS_CONTEXT_DA_KEY: data,
            _WS_CONTEXT_DA_VERSION_KEY: version,
        }
        handler, path_in_fs_root, have_path, handler_parameters, storage_context = \
            AzureMachineLearningFileSystem._infer_storage_options(path)
        assert handler == expected_handler
        assert path_in_fs_root == expected_path_in_fs_root
        assert have_path is False
        assert handler_parameters == expected_handler_parameters
        assert storage_context == expected_storage_context

    def test_infer_storage_options_data_asset_longform_uri_path(self):
        expected_path_in_fs_root = 'myfolder/mydata.csv'
        subs = 'subs'
        rg = 'rg'
        ws = 'ws'
        data = 'my_data_asset'
        version = '1'

        path = f'azureml://subscriptions/{subs}/resourcegroups/{rg}/workspaces/{ws}/' \
            f'data/{data}/versions/{version}/{expected_path_in_fs_root}'
        exp_err_msg = f'{path} is not a valid datastore uri, data asset uri, or registry uri'
        with pytest.raises(UserErrorException, match=exp_err_msg):
            _, _, _, _, _ = \
                AzureMachineLearningFileSystem._infer_storage_options(path)

    # path in filesystem root should fail to return results
    def test_infer_storage_options_path_in_fs_root(self):
        path = 'myfolder/mydata.csv'
        exp_err_msg = f'{path} is not a valid datastore uri, data asset uri, or registry uri'
        with pytest.raises(UserErrorException, match=exp_err_msg):
            _, _, _, _, _ = \
                AzureMachineLearningFileSystem._infer_storage_options(path)

    # test _path_in_fs_root_to_resource_id
    # datastore path in filesystem root should succeed to return results
    def test_path_in_fs_root_to_resource_id_datastore_path_in_fs_root(self):
        expected_path_in_fs_root = 'myfolder/mydata.csv'
        subs = 'subs'
        rg = 'rg'
        ws = 'ws'
        ds = 'ds'

        path = f'azureml://subscriptions/{subs}/resourcegroups/{rg}/workspaces/{ws}/' \
            f'datastores/{ds}/paths/{expected_path_in_fs_root}'
        (handler, path_in_fs_root, _, _, storage_context) = \
            AzureMachineLearningFileSystem._infer_storage_options(path)
        assert path_in_fs_root == expected_path_in_fs_root

        expected_resource_id = f'{ds}/{expected_path_in_fs_root}'
        resource_id = AzureMachineLearningFileSystem._path_in_fs_root_to_resource_id(
            path_in_fs_root, handler, storage_context)
        assert resource_id == expected_resource_id

    # data asset path in filesystem root should succeed to return results
    def test_path_in_fs_root_to_resource_id_data_asset_path_in_fs_root(self):
        # prepare path_in_fs_root, handler, storage_context with _infer_storage_options
        path_in_fs_root = 'myfolder/mydata.csv'
        subs = 'subs'
        rg = 'rg'
        ws = 'ws'
        data = 'my_data_asset'
        version = '1'

        path = f'azureml://subscriptions/{subs}/resourcegroups/{rg}/workspaces/{ws}/' \
            f'data/{data}/versions/{version}'
        handler, _, _, _, storage_context = \
            AzureMachineLearningFileSystem._infer_storage_options(path)

        expected_resource_id = f'AmlDataAsset://{subs}/{rg}/{ws}/' \
            f'data/{data}/versions/{version}/{path_in_fs_root}'
        resource_id = AzureMachineLearningFileSystem._path_in_fs_root_to_resource_id(
            path_in_fs_root, handler, storage_context)
        assert resource_id == expected_resource_id

    # not supported handler should fail to return results
    def test_path_in_fs_root_to_resource_id_not_supported_handler(self):
        handler = 'not_supported_handler'
        path_in_fs_root = 'myfolder/mydata.csv'
        subs = 'subs'
        rg = 'rg'
        ws = 'ws'
        ds = 'ds'

        storage_context = {
            _WS_CONTEXT_SUBS_KEY: subs,
            _WS_CONTEXT_RG_KEY: rg,
            _WS_CONTEXT_WS_KEY: ws,
            _WS_CONTEXT_DS_KEY: ds,
        }
        exp_err_msg = f'storage type {handler} is not supported'
        with pytest.raises(UserErrorException, match=exp_err_msg):
            AzureMachineLearningFileSystem._path_in_fs_root_to_resource_id(
                path_in_fs_root, handler, storage_context)

    # test _get_long_form_uri_without_provider
    # datastore path in filesystem root should succeed to return results
    def test_get_long_form_uri_without_provider_datastore_path_in_fs_root(self):
        path_in_fs_root = 'myfolder/mydata.csv'
        handler = _DATASTORE_HANDLER
        subs = 'subs'
        rg = 'rg'
        ws = 'ws'
        ds = 'ds'

        storage_context = {
            _WS_CONTEXT_SUBS_KEY: subs,
            _WS_CONTEXT_RG_KEY: rg,
            _WS_CONTEXT_WS_KEY: ws,
            _WS_CONTEXT_DS_KEY: ds,
        }

        expected_long_form_uri_without_provider = f'azureml://subscriptions/{subs}/resourcegroups/{rg}/' \
            f'workspaces/{ws}/datastores/{ds}/paths/{path_in_fs_root}'
        long_form_uri_without_provider = \
            _get_long_form_uri_without_provider(handler, storage_context, path_in_fs_root)
        assert long_form_uri_without_provider == expected_long_form_uri_without_provider

    # data asset path in filesystem root should succeed to return results
    def test_get_long_form_uri_without_provider_data_asset_path_in_fs_root(self):
        path_in_fs_root = 'myfolder/mydata.csv'
        handler = _DATAASSET_HANDLER
        subs = 'subs'
        rg = 'rg'
        ws = 'ws'
        data = 'my_data_asset'
        version = '1'

        storage_context = {
            _WS_CONTEXT_SUBS_KEY: subs,
            _WS_CONTEXT_RG_KEY: rg,
            _WS_CONTEXT_WS_KEY: ws,
            _WS_CONTEXT_DA_KEY: data,
            _WS_CONTEXT_DA_VERSION_KEY: version,
        }

        expected_long_form_uri_without_provider = f'azureml://subscriptions/{subs}/resourcegroups/{rg}/' \
            f'workspaces/{ws}/data/{data}/versions/{version}/{path_in_fs_root}'
        long_form_uri_without_provider = _get_long_form_uri_without_provider(
            handler, storage_context, path_in_fs_root)
        assert long_form_uri_without_provider == expected_long_form_uri_without_provider

    # not supported handler should fail to return results
    def test_get_long_form_uri_without_provider_not_supported_handler(self):
        handler = 'not_supported_handler'
        path_in_fs_root = 'myfolder/mydata.csv'
        subs = 'subs'
        rg = 'rg'
        ws = 'ws'
        ds = 'ds'

        storage_context = {
            _WS_CONTEXT_SUBS_KEY: subs,
            _WS_CONTEXT_RG_KEY: rg,
            _WS_CONTEXT_WS_KEY: ws,
            _WS_CONTEXT_DS_KEY: ds,
        }
        exp_err_msg = f'storage type {handler} is not supported'
        with pytest.raises(UserErrorException, match=exp_err_msg):
            _get_long_form_uri_without_provider(
                handler, storage_context, path_in_fs_root)

    # test _entry_resource_id_to_path_in_fs
    # datastore entry resource id should succeed to return results
    def test_entry_resource_id_to_path_in_fs_datastore_entry_resource_id(self):
        expected_path_in_fs_root = 'myfolder/mydata.csv'
        subs = 'subs'
        rg = 'rg'
        ws = 'ws'
        ds = 'ds'

        entry_resource_id = f'{ds}/{expected_path_in_fs_root}'
        handler = _DATASTORE_HANDLER
        handler_parameters = {
            _HANDLER_SUBS_KEY: subs,
            _HANDLER_RG_KEY: rg,
            _HANDLER_WS_KEY: ws,
            _HANDLER_DS_KEY: ds,
        }
        empty_path = ""  # if not registry handler, don't need this arg
        path_in_fs = AzureMachineLearningFileSystem._entry_resource_id_to_path_in_fs(
            entry_resource_id, handler, handler_parameters, empty_path)
        assert path_in_fs == expected_path_in_fs_root

    # data asset entry resource id should succeed to return results
    def test_entry_resource_id_to_path_in_fs_data_asset_entry_resource_id(self):
        expected_path_in_fs_root = 'myfolder/mydata.csv'
        subs = 'subs'
        rg = 'rg'
        ws = 'ws'
        data = 'my_data_asset'
        version = '1'

        entry_resource_id = f'{_DATAASSET_HANDLER}://{subs}/{rg}/{ws}/' \
            f'data/{data}/versions/{version}/{expected_path_in_fs_root}'
        handler = _DATAASSET_HANDLER
        handler_parameters = {}
        empty_path = ""  # if not registry handler, don't need this arg
        path_in_fs = AzureMachineLearningFileSystem._entry_resource_id_to_path_in_fs(
            entry_resource_id, handler, handler_parameters, empty_path)
        assert path_in_fs == expected_path_in_fs_root

    # not supported handler should fail to return results
    def test_entry_resource_id_to_path_in_fs_not_supported_handler(self):
        handler = 'not_supported_handler'
        entry_resource_id = 'myfolder/mydata.csv'
        handler_parameters = {}
        exp_err_msg = f'storage type {handler} is not supported'
        empty_path = ""  # if not registry handler, don't need this arg
        with pytest.raises(UserErrorException, match=exp_err_msg):
            AzureMachineLearningFileSystem._entry_resource_id_to_path_in_fs(
                entry_resource_id, handler, handler_parameters, empty_path)

    # data asset entry resource id with incorrect pattern should fail to return results
    def test_entry_resource_id_to_path_in_fs_data_asset_entry_resource_id_incorrect_pattern(self):
        expected_path_in_fs_root = 'myfolder/mydata.csv'
        subs = 'subs'
        rg = 'rg'
        ws = 'ws'
        data = 'my_data_asset'
        version = '1'

        incorrect_entry_resource_id_1 = f'{_DATAASSET_HANDLER}://{subs}//{rg}/{ws}/' \
            f'data/{data}/versions/{version}/{expected_path_in_fs_root}'
        incorrect_entry_resource_id_2 = f'{_DATAASSET_HANDLER}://{subs}/{ws}/' \
            f'data/{data}/versions/{version}/{expected_path_in_fs_root}'
        incorrect_entry_resource_id_3 = f'{_DATASTORE_HANDLER}://{subs}/{rg}/{ws}/' \
            f'data/{data}/versions/{version}/{expected_path_in_fs_root}'
        handler = _DATAASSET_HANDLER
        handler_parameters = {}

        incorrect_entry_resource_id_cases = [
            incorrect_entry_resource_id_1,
            incorrect_entry_resource_id_2,
            incorrect_entry_resource_id_3
        ]
        for incorrect_entry_resource_id in incorrect_entry_resource_id_cases:
            exp_err_msg = f'directory entry path {incorrect_entry_resource_id} is not a valid named asset scheme path'
            empty_path = ""  # if not registry handler, don't need this arg
            with pytest.raises(UserErrorException, match=exp_err_msg):
                AzureMachineLearningFileSystem._entry_resource_id_to_path_in_fs(
                    incorrect_entry_resource_id, handler, handler_parameters, empty_path)

    # test to_absolute_path
    # relative path in filesystem root should succeed to return results
    def test_to_absolute_path_relative_path_in_fs_root(self):
        relative_path_in_fs_root = 'data/fsspec/../fsspec'
        expected_absolute_path = 'data/fsspec'
        for prefix in ['', '/', './', '../']:
            absolute_path = AzureMachineLearningFileSystem.to_absolute_path(
                prefix + relative_path_in_fs_root)
            assert absolute_path == expected_absolute_path
