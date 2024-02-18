# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE
import pytest
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path)


def pytest_configure():
    pytest.workgroup = None
    pytest.project = None
