# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE
from pathlib import Path
import pytest
from igrafx_mining_sdk import Project
from igrafx_mining_sdk.workgroup import Workgroup
import os


class TestWorkgroup:
    """Tests for Workgroup class.
    Workgroup and project are pytest fixtures defined in conftest.py file.
    """

    @pytest.mark.dependency(name='workgroup', scope='session')
    def test_create_workgroup(self):
        """Test to create a workgroup."""
        workgroup_id = os.environ.get('WG_ID')
        workgroup_key = os.environ.get('WG_KEY')
        api_url = os.environ.get('WG_URL')
        auth_url = os.environ.get('WG_AUTH')

        # Create the workgroup instance
        wg = Workgroup(workgroup_id, workgroup_key, api_url, auth_url)

        pytest.workgroup = wg
        assert isinstance(wg, Workgroup)

    def test_wrong_login(self):
        """Test the login with wrong credentials."""
        with pytest.raises(Exception):
            assert Workgroup("a", "b")

    @pytest.mark.dependency(name='project', depends=['workgroup'], scope='session')
    def test_create_project(self):
        """Test initialization of a project."""
        project_name = "Test Project"
        description = "This is a test project."

        # Create the project
        project = pytest.workgroup.create_project(project_name, description)
        pytest.project = project
        assert isinstance(project, Project)

    @pytest.mark.dependency(depends=['workgroup'])
    def test_projects(self):
        """Test that there are projects in the workgroup."""
        assert len(pytest.workgroup.get_project_list()) > 0  # There should be at least one project in the workgroup

    @pytest.mark.dependency(depends=['workgroup'])
    def test_project_from_id(self):
        """Test that the project ID can be retrieved."""
        assert pytest.workgroup.project_from_id(pytest.project.id)