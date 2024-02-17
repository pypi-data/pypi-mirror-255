from os.path import dirname, basename
from unittest.mock import patch, MagicMock
from ara_tools.directory_navigator import DirectoryNavigator  

import pytest
import os



@pytest.fixture
def navigator():
    return DirectoryNavigator()

