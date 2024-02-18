# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Contains functionality of fsspec integration for azure machine learning defined uris

"""
from .spec import AzureMachineLearningFileSystem
# expose constants for unit test
from .spec import _DATASTORE_HANDLER, _DATAASSET_HANDLER  # noqa: F401
from .spec import _HANDLER_SUBS_KEY, _HANDLER_RG_KEY, _HANDLER_WS_KEY, _HANDLER_DS_KEY  # noqa: F401
from .spec import _WS_CONTEXT_SUBS_KEY, _WS_CONTEXT_RG_KEY, _WS_CONTEXT_WS_KEY, _WS_CONTEXT_DS_KEY  # noqa: F401
from .spec import _WS_CONTEXT_DA_KEY, _WS_CONTEXT_DA_VERSION_KEY  # noqa: F401
from .spec import _get_long_form_uri_without_provider  # noqa: F401


__all__ = ["AzureMachineLearningFileSystem"]
