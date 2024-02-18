# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE
import time
import pytest
from pathlib import Path
from igrafx_mining_sdk.project import FileStructure
from igrafx_mining_sdk.column_mapping import Column, ColumnType, ColumnMapping, FileType
from igrafx_mining_sdk.datasource import Datasource
from igrafx_mining_sdk.dtos.PredictionStatusDto import PredictionStatusDto
from igrafx_mining_sdk.dtos.PredictionTaskTypeDto import PredictionTaskTypeDto
from igrafx_mining_sdk.dtos.PredictionLaunchErrorStatusDto import PredictionLaunchErrorStatusDto
from igrafx_mining_sdk.dtos.PredictionPossibilityDto import PredictionPossibilityDto
from igrafx_mining_sdk.dtos.PredictionErrorStatusDto import PredictionErrorStatusDto
from igrafx_mining_sdk.dtos.WorkflowStatusDto import WorkflowStatusDto
from igrafx_mining_sdk.api_connector import APIConnector
from unittest.mock import MagicMock
import uuid
from datetime import datetime


class TestProject:
    """Tests for Project class.
    Workgroup and project are pytest fixtures defined in conftest.py file.
    """

    @pytest.fixture
    def api_connector(self):
        return MagicMock()

    @pytest.mark.dependency(depends=['project'], scope='session')
    def test_project_exists(self):
        """Test that a project exists."""
        project_exists = pytest.project.exists
        assert project_exists is True

    @pytest.mark.dependency(depends=['project'], scope='session')
    def test_get_project_name(self):
        """ Test that the project name is returned and correct."""
        project_name = pytest.project.get_project_name()
        assert project_name == "Test Project"

    @pytest.mark.dependency(depends=['project', 'column_mapping'], scope='session')
    def test_column_mapping_dont_exists(self):
        """Test that a column mapping can be created."""
        assert not pytest.project.column_mapping_exists

    @pytest.mark.dependency(name='add_column_mapping', depends=['project', 'column_mapping'], scope='session')
    def test_add_column_mapping(self):
        """Test that a column mapping can be created."""
        filestructure = FileStructure(
            file_type=FileType.xlsx,
            sheet_name="Sheet1"
        )
        column_list = [
            Column('case_id', 0, ColumnType.CASE_ID),
            Column('task_name', 1, ColumnType.TASK_NAME),
            Column('time', 2, ColumnType.TIME, time_format="yyyy-MM-dd'T'HH:mm")
        ]
        column_mapping = ColumnMapping(column_list)
        assert pytest.project.add_column_mapping(filestructure, column_mapping)

    @pytest.mark.dependency(depends=['project'], scope='session')
    def test_get_mapping_infos(self):
        """Test that the correct mapping infos can be returned"""
        assert pytest.project.get_mapping_infos()

    @pytest.mark.dependency(name='reset', depends=['project'], scope='session')
    def test_reset(self):
        """Test that a project can be reset."""
        assert pytest.project.reset()

    @pytest.mark.dependency(depends=['reset', 'add_column_mapping'])
    def test_add_xlsx_file(self):
        """Test that an xlsx file can be added to a project."""
        pytest.project.reset()
        filestructure = FileStructure(
            file_type=FileType.xlsx,
            sheet_name="Sheet1"
        )
        column_list = [
            Column('Case ID', 0, ColumnType.CASE_ID),
            Column('Start Timestamp', 1, ColumnType.TIME, time_format='yyyy/MM/dd HH:mm:ss.SSS'),
            Column('Complete Timestamp', 2, ColumnType.TIME, time_format='yyyy/MM/dd HH:mm:ss.SSS'),
            Column('Activity', 3, ColumnType.TASK_NAME),
            Column('Ressource', 4, ColumnType.DIMENSION),
        ]
        column_mapping = ColumnMapping(column_list)
        base_dir = Path(__file__).resolve().parent
        file_path = base_dir / 'data' / 'tables' / 'p2pShortExcel.xlsx'
        assert pytest.project.add_column_mapping(filestructure, column_mapping)
        assert pytest.project.add_file(str(file_path))

    @pytest.mark.dependency(depends=['reset', 'add_column_mapping'])
    def test_add_xls_file(self):
        """Test that an xls file can be added to a project."""
        pytest.project.reset()
        filestructure = FileStructure(
            file_type=FileType.xls,
            sheet_name="Sheet1"
        )
        column_list = [
            Column('Case ID', 0, ColumnType.CASE_ID),
            Column('Start Timestamp', 1, ColumnType.TIME, time_format='yyyy/MM/dd HH:mm:ss.SSS'),
            Column('Complete Timestamp', 2, ColumnType.TIME, time_format='yyyy/MM/dd HH:mm:ss.SSS'),
            Column('Activity', 3, ColumnType.TASK_NAME),
            Column('Ressource', 4, ColumnType.DIMENSION),
        ]
        column_mapping = ColumnMapping(column_list)
        base_dir = Path(__file__).resolve().parent
        file_path = base_dir / 'data' / 'tables' / 'p2pShortExcel.xls'
        assert pytest.project.add_column_mapping(filestructure, column_mapping)
        assert pytest.project.add_file(str(file_path))

    @pytest.mark.dependency(name='add_csv_file', depends=['reset', 'add_column_mapping'], scope='session')
    def test_add_csv_file(self):
        """Test that a csv file can be added to a project."""
        pytest.project.reset()
        filestructure = FileStructure(
            file_type=FileType.csv,
        )
        column_list = [
            Column('Case ID', 0, ColumnType.CASE_ID),
            Column('Activity', 1, ColumnType.TASK_NAME),
            Column('Start Date', 2, ColumnType.TIME, time_format='dd/MM/yyyy HH:mm'),
            Column('End Date', 3, ColumnType.TIME, time_format='dd/MM/yyyy HH:mm'),
        ]
        column_mapping = ColumnMapping(column_list)
        base_dir = Path(__file__).resolve().parent
        file_path = base_dir / 'data' / 'tables' / 'testdata.csv'
        assert pytest.project.add_column_mapping(filestructure, column_mapping)
        assert pytest.project.add_file(str(file_path))

    @pytest.mark.dependency(name='project_contains_data', depends=['add_csv_file'])
    def test_project_contains_data(self):
        count = 0
        while pytest.project.nodes_datasource.__class__ != Datasource:
            time.sleep(3)
            count += 1
            if count > 100:
                assert False, 'Timeout reached'
        assert True

    @pytest.mark.dependency(depends=['project_contains_data'])
    def test_datasources_types(self):
        """Test the types of the datasources"""
        assert pytest.project.nodes_datasource.__class__ == Datasource
        assert pytest.project.edges_datasource.__class__ == Datasource
        assert pytest.project.cases_datasource.__class__ == Datasource

    @pytest.mark.dependency(depends=['project_contains_data'])
    def test_get_project_variants(self):
        """Test that the project correct variants are returned."""
        assert pytest.project.get_project_variants(1, 3)

    @pytest.mark.dependency(depends=['project_contains_data'])
    def test_prediction_possibility_no_end_case_rule(self):
        """Test that the project prediction can not be launched because no end case rule created."""
        assert pytest.project.prediction_possibility() == PredictionPossibilityDto.NO_END_CASE_RULE

    @pytest.mark.dependency(depends=['project_contains_data'])
    def test_prediction_status_no_end_case_rule(self):
        """Test that the project prediction history is empty as no prediction has been launched."""
        assert len(pytest.project.predictions_status()) == 0

    @pytest.mark.dependency(depends=['project_contains_data'])
    def test_prediction_not_exists(self):
        """Test that the project has no prediction ready."""
        assert pytest.project.is_ready_prediction_exists() == False

    @pytest.mark.dependency(depends=['project_contains_data'])
    def test_prediction_launch_impossible(self):
        """Test that the project prediction can not be launched."""
        assert pytest.project.launch_prediction() == PredictionLaunchErrorStatusDto.NOTHING_TO_PREDICT

    @pytest.mark.dependency(depends=['project_contains_data'])
    def test_predictions_delete(self):
        """Test that the project prediction history deletion do not fail and correctly handle response."""
        assert pytest.project.delete_predictions() is None

    def test_prediction_possibility_success(self, mocker):
        """Test, via mocking,
        that the project prediction_possibility method correctly handle CAN_LAUNCH_PREDICTION return from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.json.return_value = {"isPredictionLaunchPossible": "CAN_LAUNCH_PREDICTION"}

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.prediction_possibility()

        assert result == PredictionPossibilityDto.CAN_LAUNCH_PREDICTION

    def test_prediction_possibility_invalid_response(self, mocker):
        """Test, via mocking,
        that the project prediction_possibility method correctly handle invalid isPredictionLaunchPossible
        value return from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.json.return_value = {"isPredictionLaunchPossible": "toto"}

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.prediction_possibility()

        assert result == PredictionPossibilityDto.INVALID_RESPONSE

    def test_prediction_possibility_unreadable_response(self, mocker):
        """Test, via mocking,
        that the project prediction_possibility method correctly handle invalid argument name in return from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.json.return_value = {"falseArgument": "CAN_LAUNCH_PREDICTION"}

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.prediction_possibility()

        assert result == PredictionPossibilityDto.INVALID_RESPONSE

    def test_prediction_non_activated(self, mocker):
        """Test, via mocking,
        that the project prediction_possibility method correctly handle a 402 return from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 402

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.prediction_possibility()

        assert result == PredictionPossibilityDto.NON_ACTIVATED_PREDICTION

    def test_prediction_forbidden(self, mocker):
        """Test, via mocking,
         that the project prediction_possibility method correctly handle a 403 return from API call.
         """

        mock_response = mocker.Mock()
        mock_response.status_code = 403

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.prediction_possibility()

        assert result == PredictionPossibilityDto.FORBIDDEN

    def test_prediction_unknown_error(self, mocker):
        """Test, via mocking,
        that the project prediction_possibility method correctly handle a 500 return from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 500

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.prediction_possibility()

        assert result == PredictionPossibilityDto.UNKNOWN_ERROR

    def test_predictions_status_success(self, mocker):
        """Test, via mocking,
        that the project predictions_status method correctly handle a expected JSON return from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.json.return_value = [
            {
                "workflowId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "status": "RUNNING",
                "projectId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "completedTasks": ["TRAIN_TOPOLOGY"],
                "startTime": "2023-12-12T13:24:11.929Z",
                "endTime": "2023-12-12T13:24:11.929Z"
            }
        ]

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.predictions_status()
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        expected_result = WorkflowStatusDto(
            uuid.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
            uuid.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
            PredictionStatusDto.RUNNING,
            datetime.strptime("2023-12-12T13:24:11.929Z", date_format),
            datetime.strptime("2023-12-12T13:24:11.929Z", date_format),
            [PredictionTaskTypeDto.TRAIN_TOPOLOGY]
        )

        assert result[0] == expected_result

    def test_predictions_status_success_no_end_date(self, mocker):
        """Test, via mocking,
        that the project predictions_status method correctly handle
        a expected JSON with no end date return from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.json.return_value = [
            {
                "workflowId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "status": "RUNNING",
                "projectId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "startTime": "2023-12-12T13:24:11.929Z"
            }
        ]

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.predictions_status()
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        expected_result = WorkflowStatusDto(
            uuid.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
            uuid.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
            PredictionStatusDto.RUNNING,
            datetime.strptime("2023-12-12T13:24:11.929Z", date_format),
            None,
            []
        )

        assert result[0] == expected_result

    def test_predictions_status_invalid_response_if_one_invalid_field(self, mocker):
        """Test, via mocking,
        that the project predictions_status method correctly respond INVALID_RESPONSE if any of elements returned
         from API call has invalid field.
         """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.json.return_value = [
            {
                "workflowId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "status": "RUNNING",
                "projectId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "completedTasks": ["TRAIN_TOPOLOGY"],
                "startTime": "2023-12-12T13:24:11.929Z",
                "endTime": "2023-12-12T13:24:11.929Z"
            },
            {
                "invalidField": "3fa45f64-5717-4562-b3fc-2c963f66afa6",
                "status": "RUNNING",
                "projectId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "completedTasks": ["TRAIN_TOPOLOGY"],
                "startTime": "2023-12-12T13:24:11.929Z",
                "endTime": "2023-12-12T13:24:11.929Z"
            }
        ]

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.predictions_status()

        assert result == PredictionErrorStatusDto.INVALID_RESPONSE

    def test_predictions_status_empty_response(self, mocker):
        """Test, via mocking,
         that the project predictions_status method correctly respond no elements returned from API call.
         """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.json.return_value = []

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.predictions_status()

        assert len(result) == 0

    def test_predictions_status_non_active(self, mocker):
        """Test, via mocking, that the project predictions_status method correctly handle 402 response from API call."""

        mock_response = mocker.Mock()
        mock_response.status_code = 402

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.predictions_status()

        assert result == PredictionErrorStatusDto.NON_ACTIVATED_PREDICTION

    def test_predictions_status_forbidden(self, mocker):
        """Test, via mocking, that the project predictions_status method correctly handle 403 response from API call."""

        mock_response = mocker.Mock()
        mock_response.status_code = 403

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.predictions_status()

        assert result == PredictionErrorStatusDto.FORBIDDEN

    def test_predictions_status_failure(self, mocker):
        """Test, via mocking, that the project predictions_status method correctly handle 424 response from API call."""

        mock_response = mocker.Mock()
        mock_response.status_code = 424

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.predictions_status()

        assert result == PredictionErrorStatusDto.PREDICTION_SERVICE_FAILURE

    def test_predictions_status_unkown_failure(self, mocker):
        """Test, via mocking, that the project predictions_status method correctly handle 500 response from API call."""

        mock_response = mocker.Mock()
        mock_response.status_code = 500

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.predictions_status()

        assert result == PredictionErrorStatusDto.UNKNOWN_ERROR

    def test_ready_prediction_exists(self, mocker):
        """Test, via mocking,
        that the project is_ready_prediction_exists method correctly handle expected response True from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.json.return_value = {"isPredictionReady": True}

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.is_ready_prediction_exists()

        assert result is True

    def test_ready_prediction_not_exists(self, mocker):
        """Test, via mocking,
        that the project is_ready_prediction_exists method correctly handle expected response False from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.json.return_value = {"isPredictionReady": False}

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.is_ready_prediction_exists()

        assert result is False

    def test_ready_prediction_exists_invalid_result(self, mocker):
        """Test, via mocking,
        that the project is_ready_prediction_exists method correctly handle
        unexpected non boolean response from API call to INVALID_RESPONSE result.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.json.return_value = {"isPredictionReady": "toto"}

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.is_ready_prediction_exists()

        assert result == PredictionErrorStatusDto.INVALID_RESPONSE

    def test_ready_prediction_exists_invalid_response(self, mocker):
        """Test, via mocking,
        that the project is_ready_prediction_exists method correctly handle response with unexpected field from API
        call to INVALID_RESPONSE result.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.json.return_value = {"invalidField": "toto"}

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.is_ready_prediction_exists()

        assert result == PredictionErrorStatusDto.INVALID_RESPONSE

    def test_ready_prediction_exists_non_active_prediction(self, mocker):
        """Test, via mocking,
        that the project is_ready_prediction_exists method correctly handle 402 response from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 402

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.is_ready_prediction_exists()

        assert result == PredictionErrorStatusDto.NON_ACTIVATED_PREDICTION

    def test_ready_prediction_exists_forbidden(self, mocker):
        """Test, via mocking,
        that the project is_ready_prediction_exists method correctly handle 403 response from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 403

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.is_ready_prediction_exists()

        assert result == PredictionErrorStatusDto.FORBIDDEN

    def test_ready_prediction_exists_forbidden_500(self, mocker):
        """Test, via mocking,
        that the project is_ready_prediction_exists method correctly handle 500 response from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 500

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.is_ready_prediction_exists()

        assert result == PredictionErrorStatusDto.UNKNOWN_ERROR

    def test_launch_prediction_success(self, mocker):
        """Test, via mocking,
        that the project launch_prediction method correctly handle expected response from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.json.return_value = {"predictionTrainId": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}

        mocker.patch.object(APIConnector, 'post_request', return_value=mock_response)

        result = pytest.project.launch_prediction()

        assert result == uuid.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")

    def test_launch_prediction_bad_response_uuid(self, mocker):
        """Test, via mocking,
        that the project launch_prediction method correctly handle response with invalid value in JSON from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.json.return_value = {"predictionTrainId": "toto"}

        mocker.patch.object(APIConnector, 'post_request', return_value=mock_response)

        result = pytest.project.launch_prediction()

        assert result == PredictionLaunchErrorStatusDto.INVALID_RESPONSE

    def test_launch_prediction_bad_response_field(self, mocker):
        """Test, via mocking,
        that the project launch_prediction method correctly handle response with invalid field in JSON from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.json.return_value = {"invalidField": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}

        mocker.patch.object(APIConnector, 'post_request', return_value=mock_response)

        result = pytest.project.launch_prediction()

        assert result == PredictionLaunchErrorStatusDto.INVALID_RESPONSE

    def test_launch_prediction_non_active(self, mocker):
        """Test, via mocking, that the project launch_prediction method correctly handle 402 response from API call."""

        mock_response = mocker.Mock()
        mock_response.status_code = 402

        mocker.patch.object(APIConnector, 'post_request', return_value=mock_response)

        result = pytest.project.launch_prediction()

        assert result == PredictionLaunchErrorStatusDto.NON_ACTIVATED_PREDICTION

    def test_launch_prediction_forbidden(self, mocker):
        """Test, via mocking, that the project launch_prediction method correctly handle 403 response from API call."""

        mock_response = mocker.Mock()
        mock_response.status_code = 403

        mocker.patch.object(APIConnector, 'post_request', return_value=mock_response)

        result = pytest.project.launch_prediction()

        assert result == PredictionLaunchErrorStatusDto.FORBIDDEN

    def test_launch_prediction_impossible(self, mocker):
        """Test, via mocking, that the project launch_prediction method correctly handle 409 response from API call."""

        mock_response = mocker.Mock()
        mock_response.status_code = 409

        mocker.patch.object(APIConnector, 'post_request', return_value=mock_response)

        result = pytest.project.launch_prediction()

        assert result == PredictionLaunchErrorStatusDto.NOTHING_TO_PREDICT

    def test_launch_prediction_failure(self, mocker):
        """Test, via mocking, that the project launch_prediction method correctly handle 424 response from API call."""

        mock_response = mocker.Mock()
        mock_response.status_code = 424

        mocker.patch.object(APIConnector, 'post_request', return_value=mock_response)

        result = pytest.project.launch_prediction()

        assert result == PredictionLaunchErrorStatusDto.PREDICTION_SERVICE_FAILURE

    def test_launch_prediction_unknown_failure(self, mocker):
        """Test, via mocking, that the project launch_prediction method correctly handle 500 response from API call."""

        mock_response = mocker.Mock()
        mock_response.status_code = 500

        mocker.patch.object(APIConnector, 'post_request', return_value=mock_response)

        result = pytest.project.launch_prediction()

        assert result == PredictionLaunchErrorStatusDto.UNKNOWN_ERROR

    def test_delete_predictions_success(self, mocker):
        """Test, via mocking,
        that the project delete_predictions method correctly handle expected response from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 204

        mocker.patch.object(APIConnector, 'delete_request', return_value=mock_response)

        result = pytest.project.delete_predictions()

        assert result is None

    def test_delete_predictions_non_active(self, api_connector, mocker):
        """Test, via mocking,
        that the project delete_predictions method correctly handles 402 response from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 402

        mocker.patch.object(APIConnector, 'delete_request', return_value=mock_response)

        result = pytest.project.delete_predictions()

        assert result == PredictionErrorStatusDto.NON_ACTIVATED_PREDICTION

    def test_delete_predictions_forbidden(self, mocker):
        """Test, via mocking, that the project delete_predictions method correctly handle 403 response from API call."""

        mock_response = mocker.Mock()
        mock_response.status_code = 403

        mocker.patch.object(APIConnector, 'delete_request', return_value=mock_response)

        result = pytest.project.delete_predictions()

        assert result == PredictionErrorStatusDto.FORBIDDEN

    def test_delete_predictions_fails(self, mocker):
        """Test, via mocking, that the project delete_predictions method correctly handle 424 response from API call."""

        mock_response = mocker.Mock()
        mock_response.status_code = 424

        mocker.patch.object(APIConnector, 'delete_request', return_value=mock_response)

        result = pytest.project.delete_predictions()

        assert result == PredictionErrorStatusDto.PREDICTION_SERVICE_FAILURE

    def test_delete_predictions_fails_500(self, mocker):
        """Test, via mocking, that the project delete_predictions method correctly handle 500 response from API call."""

        mock_response = mocker.Mock()
        mock_response.status_code = 500

        mocker.patch.object(APIConnector, 'delete_request', return_value=mock_response)

        result = pytest.project.delete_predictions()

        assert result == PredictionErrorStatusDto.UNKNOWN_ERROR

    def test_predictions_status_code_200(self, mocker):
        """Test, via mocking,
        that the project get_project_predictions method correctly handles 200 response from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"prediction": "result"}

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.get_project_predictions(["case_id"])

        assert result == {"prediction": "result"}

    def test_get_project_predictions_status_code_202(self, mocker):
        """Test, via mocking,
        that the project get_project_predictions method correctly handles 202 response from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 202
        mock_response.json.return_value = {"prediction": "test"}

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.get_project_predictions(["case_id"])

        assert result == "No prediction available for the given case"

    def test_get_project_predictions_status_code_402(self, mocker):
        """Test, via mocking,
        that the project get_project_predictions method correctly handles 402 response from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 402

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.get_project_predictions(["case_id"])

        assert result == "Prediction is not activated"

    def test_get_project_predictions_status_code_403(self, mocker):
        """Test, via mocking,
        that the project get_project_predictions method correctly handles 403 response from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 403

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.get_project_predictions(["case_id"])

        assert result == "User does not have access to this project or Train API is forbidden for this license/version"

    def test_get_project_predictions_status_code_unexpected(self, mocker):
        """Test, via mocking,
        that the project get_project_predictions method correctly handles unexpected status code from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 500  # For example, any unexpected status code

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        result = pytest.project.get_project_predictions(["case_id"])

        assert result == "Unexpected status code: 500. Failed to get predictions."

    def test_get_project_predictions_multiple_case_ids(self, mocker):
        """Test, via mocking,
        that the project get_project_predictions method correctly handles multiple case IDs from API call.
        """

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"prediction": "result"}

        mocker.patch.object(APIConnector, 'get_request', return_value=mock_response)

        case_ids = ["case_id_1", "case_id_2", "case_id_3"]
        result = pytest.project.get_project_predictions(case_ids)

        assert result == {"prediction": "result"}
