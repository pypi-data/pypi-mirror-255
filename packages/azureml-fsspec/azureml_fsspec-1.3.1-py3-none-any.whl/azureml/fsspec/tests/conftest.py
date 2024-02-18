# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import sys
import pytest
from os import path

# Add this directory to the path so tests don't need to change the path
# before importing common code
curdir = path.dirname(path.abspath(__file__))
sys.path.append(path.normpath(path.join(curdir, "../../../../../tests/scenarios")))

pytest_plugins = "utilities.plugins.output_handler", \
                 "utilities.plugins.enforce_owner", \
                 "utilities.plugins.reporting"


def pytest_itemcollected(item):
    from utilities import constants
    if not item.get_closest_marker("owner"):
        item.add_marker(pytest.mark.owner(email=constants.owner_email_data_service))
