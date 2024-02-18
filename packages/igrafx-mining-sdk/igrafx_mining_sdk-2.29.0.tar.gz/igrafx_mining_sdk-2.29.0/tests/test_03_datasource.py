# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE
import pytest
from igrafx_mining_sdk.datasource import Datasource
import os


NAME = os.environ.get('NAME')
TYPE = os.environ.get('TYPE')
HOST = os.environ.get('HOST')
PORT = os.environ.get('PORT')


class TestDatasource:
    """Class for testing Datasource class.
    Workgroup and project are pytest fixtures defined in conftest.py file.
    """
    @pytest.mark.dependency(depends=['workgroup'], scope='session')
    def test_create_datasource(self):
        """Test creating a Datasource"""
        ds = Datasource(NAME, TYPE, HOST, PORT, pytest.workgroup.api_connector)
        assert isinstance(ds, Datasource)

    @pytest.mark.dependency(depends=['project_contains_data'], scope='session')
    def test_columns(self):
        """Test the columns of a Datasource"""
        ds = pytest.project.edges_datasource
        assert ds.columns != []

    @pytest.mark.dependency(depends=['project_contains_data'], scope='session')
    def test_non_empty_ds(self):
        """Test that the datasource is not empty"""
        ds = pytest.project.nodes_datasource
        assert 0 < len(ds.load_dataframe(load_limit=10)) <= 10

    @pytest.mark.dependency(depends=['project_contains_data'], scope='session')
    def test_read_only(self):
        """Test that the datasource is read only"""
        ds = pytest.project.edges_datasource
        pk = pytest.project.process_keys[0]
        # Test that all of those requests will fail
        with pytest.raises(Exception):
            assert ds.request(f'DELETE FROM "{ds.name}" WHERE processkey = \'{pk}\'')
        with pytest.raises(Exception):
            assert ds.request(f'INSERT INTO "{ds.name}"(processkey) VALUES (\'{pk}\')')
        with pytest.raises(Exception):
            assert ds.request(f'DROP TABLE "{ds.name}"')
            ds.drop()
        with pytest.raises(Exception):
            assert ds.request(f'ALTER TABLE "{ds.name}" DROP COLUMN processkey')

    @pytest.mark.dependency(depends=['workgroup'], scope='session')
    def test_close(self):
        """Test that the Datasource can be closed"""
        ds = Datasource(NAME, TYPE, HOST, PORT, pytest.workgroup.api_connector)
        # ensure connection and cursor are none
        assert ds._cursor is None
        assert ds._connection is None

        # initialize both cursor and connection
        cursor = ds.cursor
        connection = ds.connection
        assert cursor is not None
        assert connection is not None

        # close cursor and connection then check that they are none again
        ds.close()
        assert ds._cursor is None
        assert ds._connection is None
