# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE
import pytest


class TestDelete:
    """Final tests to clean up session."""

    @pytest.mark.dependency(depends=['project'], scope='session')
    def test_delete_project(self):
        pytest.project.delete_project()
