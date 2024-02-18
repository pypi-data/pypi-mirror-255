# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE

import os
import random
from igrafx_mining_sdk.graph import Graph, GraphInstance
from igrafx_mining_sdk.column_mapping import FileStructure, ColumnMapping
from igrafx_mining_sdk.datasource import Datasource
from igrafx_mining_sdk.api_connector import APIConnector
from igrafx_mining_sdk.dtos.PredictionStatusDto import PredictionStatusDto
from igrafx_mining_sdk.dtos.PredictionTaskTypeDto import PredictionTaskTypeDto
from igrafx_mining_sdk.dtos.PredictionLaunchErrorStatusDto import PredictionLaunchErrorStatusDto
from igrafx_mining_sdk.dtos.PredictionPossibilityDto import PredictionPossibilityDto
from igrafx_mining_sdk.dtos.PredictionErrorStatusDto import PredictionErrorStatusDto
from igrafx_mining_sdk.dtos.WorkflowStatusDto import WorkflowStatusDto
import uuid
from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Union


class Project:
    """A iGrafx P360 Live Mining project"""
    def __init__(self, pid: str, api_connector: APIConnector):
        """Create a iGrafx P360 Live Mining project from a project ID and the Workgroup it was created from

        :param pid: the Project's ID
        :param api_connector: the APIConnector object
        """
        self.id = pid
        self.api_connector = api_connector
        self._graph = None
        self._ds_response = None
        self._process_keys = []

    @property
    def exists(self):
        """Check if the project exists"""
        response_project_exist = self.api_connector.get_request(f"/project/{self.id}/exist").json()
        return response_project_exist["exists"]

    def delete_project(self):
        """Deletes the project"""
        response_project_delete = self.api_connector.delete_request(f"/project/{self.id}")
        return response_project_delete

    def get_project_name(self):
        """Returns the name of the project"""
        response_project_name = self.api_connector.get_request(f"/project/{self.id}/name").json()
        return response_project_name["name"]

    def graph(self, gateways=False):
        """Performs a REST request for the project model graph if it hasn't already been retrieved.

        :param gateways: Boolean that controls whether the graph returned will be BPMN-like or not
        """
        if self._graph is None:
            params = {"mode": "gateways" if gateways else "simplified"}
            response_graph = self.api_connector.get_request(
                f"/project/{self.id}/graph",
                params=params)
            self._graph = Graph.from_dict(self.id, response_graph.json())
        return self._graph

    def get_graph_instances(self, limit=None, shuffle=False):
        """Returns all the project's Graph Instances, performing a REST request for any instances that don't already
        exist within the project.

        :param limit: the maximum number of graph instances to return
        :param shuffle: whether to shuffle the list of graph instances with a default value set to False
        """
        limit = min(limit, len(self.process_keys)) if limit is not None else len(self.process_keys)
        sample = random.sample(self.process_keys, limit) if shuffle else self.process_keys[:limit]
        return [self.graph_instance_from_key(k) for k in sample]

    def graph_instance_from_key(self, process_id):
        """Performs a REST request for the graph instance associated with a process key, and returns it.

        :param process_id: the id of the process whose graph we want to get
        """
        parameters = {"processId": process_id}
        response_graph_instance = None
        try:
            response_graph_instance = self.api_connector.get_request(
                f"/project/{self.id}/graphInstance",
                params=parameters)
            graph = response_graph_instance.json()
            graph_instance = GraphInstance.from_dict(self.id, graph)
        except Exception as error:
            print(f"Could not parse graph: {error}")
            print(response_graph_instance)
            return None
        return graph_instance

    def __datasource_request(self):
        """Request datasources associated with the project"""

        response_datasource = self.api_connector.get_request(f"/datasources/{self.id}")
        return response_datasource

    @property
    def nodes_datasource(self):
        """Returns datasource of type '_vertex'"""
        return self.__get_datasource_by_name('_vertex')

    @property
    def edges_datasource(self):
        """Returns datasource of type '_simplifiedEdge'"""
        return self.__get_datasource_by_name('_simplifiedEdge')


    @property
    def cases_datasource(self):
        """Returns datasource of type 'cases'"""
        return self.__get_datasource_by_name('cases')

    def __get_datasource_by_name(self, ds_type):
        """Helper method that filters the datasources based on the given type

        :param ds_type: The type of datasource. Can be 'cases', '_simplifiedEdge' or '_vertex'
        """
        if self._ds_response is None or self._ds_response.status_code == 404:
            self._ds_response = self.__datasource_request()

        if self._ds_response.status_code == 200:
            json_response = self._ds_response.json()
            for item in json_response:
                if "_simplifiedEdge" in item["name"]:
                    item["type"] = "_simplifiedEdge"
                elif "_vertex" in item["name"]:
                    item["type"] = "_vertex"
                else:
                    item["type"] = "cases"

            response_filtered = [d for d in json_response if d['type'] == ds_type][0]
            return Datasource(
                response_filtered["name"],
                response_filtered["type"],
                response_filtered["host"],
                response_filtered["port"],
                self.api_connector)
        else:
            return None

    def get_project_variants(self, page_index: int, limit: int, search: str = None):
        """Returns the project variants

        :param page_index: the page index for pagination
        :param limit: The maximum number of items to return per page
        :param search: The search query to filter variants by name (optional)
        """
        params = {"projectId": self.id, "pageIndex": page_index, "limit": limit}
        if search is not None:
            params["search"] = search

        route = f"/project/{self.id}/variants"
        response_variants = self.api_connector.get_request(route, params=params)
        return response_variants.json()

    def get_project_completed_cases(self, page_index: int, limit: int, search_case_id: str = None):
        """Returns the projects completed cases

        :param page_index: the page index for pagination
        :param limit: The maximum number of items to return per page
        :param search_case_id: The search query to filter cases by ID (optional)

        """
        params = {"projectId": self.id, "pageIndex": page_index, "limit": limit}
        if search_case_id is not None:
            params["searchCaseId"] = search_case_id

        route = f"/project/{self.id}/completedCases"
        response_case_ids = self.api_connector.get_request(route, params=params)
        return response_case_ids.json()

    @property
    def process_keys(self):
        """Queries the datasources to find the different process keys of the project"""

        if len(self._process_keys) == 0:
            ds = self.edges_datasource
            res = ds.request(f"SELECT DISTINCT processkey FROM \"{ds.name}\"")
            self._process_keys = [key for key in res['processkey']]

        return self._process_keys

    def add_column_mapping(self, filestructure: FileStructure, columnmapping: ColumnMapping):
        """Create a column mapping for the project

        :param filestructure: The filestructure
        :param columnmapping: The column mapping
        """
        route = f"/project/{self.id}/column-mapping"
        json = {'fileStructure': filestructure.to_dict(), 'columnMapping': columnmapping.to_dict()}
        response_column_mapping = self.api_connector.post_request(route, json=json)
        return response_column_mapping.status_code == 204

    @property
    def column_mapping_exists(self):
        """Check if a column mapping exists"""

        json_response = self.api_connector.get_request(f"/project/{self.id}/column-mapping-exists")
        return json_response.json()['exists']

    def get_mapping_infos(self):
        """Returns the mapping infos of the project such as the column names"""

        response_mapping_infos = self.api_connector.get_request(f"/project/{self.id}/mappingInfos").json()
        return response_mapping_infos

    def reset(self):
        """Makes an API call to manually reset a project"""

        response_reset = self.api_connector.post_request(f"/project/{self.id}/reset")
        return response_reset.status_code == 204

    def add_file(self, path):
        """Adds a file to the project

        :param path: The path to the file to add
        """
        route = f"/project/{self.id}/file?teamId={self.api_connector.wg_id}"
        file_extension = os.path.splitext(path)[-1].lower()
        if file_extension == ".csv":
            mime_type = "text/csv"
        elif file_extension == ".xlsx":
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif file_extension == ".xls":
            mime_type = "application/vnd.ms-excel"
        else:
            raise ValueError(f"File extension {file_extension} is not supported")

        with open(path, 'rb') as file:
            files = {'file': (os.path.basename(path), file, mime_type)}
            headers = {"accept": "application/json, text/plain, */*"}
            response_add_file = self.api_connector.post_request(route, files=files, headers=headers)

        print(response_add_file)
        return response_add_file.status_code == 201

    def prediction_possibility(self) -> PredictionPossibilityDto:
        """Makes an API call to get information on possibility to launch prediction on a project,
        or on why it can not be launched on the project"""

        json_response = self.api_connector.get_request(f"/projects/{self.id}/predictions/trains/possible")

        if json_response.status_code == 200:
            json_content = json_response.json()
            if 'isPredictionLaunchPossible' in json_content:
                response_value = json_content['isPredictionLaunchPossible']
                value_as_enum = self._get_enum_value_or_none(response_value, PredictionPossibilityDto)
                if value_as_enum is None:
                    print(f"Tried to get prediction possibility but invalid response value on project {self.id}. "
                          f"Response: {json_content}")
                    return PredictionPossibilityDto.INVALID_RESPONSE
                else:
                    return value_as_enum
            else:
                print(f"Tried to get prediction possibility but invalid response format on project {self.id}. "
                      f"Response: {json_content}")
                return PredictionPossibilityDto.INVALID_RESPONSE
        elif json_response.status_code == 402:
            print(f"Tried to get prediction possibility but non activated on project {self.id}. "
                  f"Response: {json_response}")
            return PredictionPossibilityDto.NON_ACTIVATED_PREDICTION
        elif json_response.status_code == 403:
            print(f"Tried to get prediction possibility but forbidden on project {self.id}. Response: {json_response}")
            return PredictionPossibilityDto.FORBIDDEN
        else:
            # Handle errors or unexpected responses
            print(f"Failed to check prediction possibility on project {self.id}. Response: {json_response}")
            return PredictionPossibilityDto.UNKNOWN_ERROR

    def predictions_status(self) -> Union[List[WorkflowStatusDto], PredictionErrorStatusDto]:
        """Makes an API call to get project's predictions history"""

        json_response = self.api_connector.get_request(f"/projects/{self.id}/predictions/trains/status")

        if json_response.status_code == 200:
            json_content = json_response.json()
            workflows_status = [self._parse_workflow_status(item) for item in json_content]
            if any(isinstance(workflow_status, PredictionErrorStatusDto) for workflow_status in workflows_status):
                print(f"Tried to get predictions status but invalid response format on project {self.id}. "
                      f"Response: {json_content}")
                return PredictionErrorStatusDto.INVALID_RESPONSE
            else:
                return workflows_status
        elif json_response.status_code == 402:
            print(f"Tried to get predictions status but non activated on project {self.id}. Response: {json_response}")
            return PredictionErrorStatusDto.NON_ACTIVATED_PREDICTION
        elif json_response.status_code == 403:
            print(f"Tried to get predictions status but forbidden on project {self.id}. Response: {json_response}")
            return PredictionErrorStatusDto.FORBIDDEN
        elif json_response.status_code == 424:
            print(f"Tried to get predictions status but service failed on project {self.id}. Response: {json_response}")
            return PredictionErrorStatusDto.PREDICTION_SERVICE_FAILURE
        else:
            print(f"Failed to check predictions status on project {self.id}. Response: {json_response}")
            return PredictionErrorStatusDto.UNKNOWN_ERROR

    def is_ready_prediction_exists(self) -> Union[bool, PredictionErrorStatusDto]:
        """Makes an API call to check if a prediction is ready on the project"""

        response = self.api_connector.get_request(f"/projects/{self.id}/predictions/exists")

        if response.status_code == 200:
            json_content = response.json()
            is_prediction_ready = json_content.get('isPredictionReady')
            if is_prediction_ready is not None and isinstance(is_prediction_ready, bool):
                return is_prediction_ready
            else:
                print(f"Tried to get prediction existence but invalid response format on project {self.id}. "
                      f"Response: {json_content}")
                return PredictionErrorStatusDto.INVALID_RESPONSE
        elif response.status_code == 402:
            print(f"Tried to get prediction existence but non activated on project {self.id}. Response: {response}")
            return PredictionErrorStatusDto.NON_ACTIVATED_PREDICTION
        elif response.status_code == 403:
            print(f"Tried to get prediction existence but forbidden on project {self.id}. Response: {response}")
            return PredictionErrorStatusDto.FORBIDDEN
        else:
            print(f"Failed to check prediction existence on project {self.id}. Response: {response}")
            return PredictionErrorStatusDto.UNKNOWN_ERROR

    def launch_prediction(self) -> Union[uuid.UUID, PredictionLaunchErrorStatusDto]:
        """Makes an API call to launch a prediction computation on the project"""

        response = self.api_connector.post_request(f"/projects/{self.id}/predictions/trains/launch")

        if response.status_code == 200:
            json_content = response.json()
            prediction_train_id = json_content.get('predictionTrainId')
            if prediction_train_id is not None:
                try:
                    return uuid.UUID(prediction_train_id)
                except ValueError:
                    print(f"Invalid train id on launch train for project {self.id}. Train id: {prediction_train_id}")
                    return PredictionLaunchErrorStatusDto.INVALID_RESPONSE
            else:
                print(f"Invalid response on launch train on project {self.id}. Response: {json_content}")
                return PredictionLaunchErrorStatusDto.INVALID_RESPONSE
        elif response.status_code == 402:
            print(f"Tried to launch prediction but non activated on project {self.id}. Response: {response}")
            return PredictionLaunchErrorStatusDto.NON_ACTIVATED_PREDICTION
        elif response.status_code == 403:
            print(f"Tried to launch prediction but forbidden on project {self.id}. Response: {response}")
            return PredictionLaunchErrorStatusDto.FORBIDDEN
        elif response.status_code == 409:
            return PredictionLaunchErrorStatusDto.NOTHING_TO_PREDICT
        elif response.status_code == 424:
            print(f"Tried to launch prediction but service failed on project {self.id}. Response: {response}")
            return PredictionLaunchErrorStatusDto.PREDICTION_SERVICE_FAILURE
        else:
            print(f"Failed to launch prediction on project {self.id}. Response: {response}")
            return PredictionLaunchErrorStatusDto.UNKNOWN_ERROR

    def delete_predictions(self) -> Union[None, PredictionErrorStatusDto]:
        """Makes an API call to delete project's current prediction results and predictions history"""

        response = self.api_connector.delete_request(f"/projects/{self.id}/predictions")

        if response.status_code == 204:
            return None
        elif response.status_code == 402:
            print(f"Tried to delete predictions but non activated on project {self.id}. Response: {response}")
            return PredictionErrorStatusDto.NON_ACTIVATED_PREDICTION
        elif response.status_code == 403:
            print(f"Tried to delete predictions but forbidden on project {self.id}. Response: {response}")
            return PredictionErrorStatusDto.FORBIDDEN
        elif response.status_code == 424:
            print(f"Tried to delete predictions but service failed on project {self.id}. Response: {response}")
            return PredictionErrorStatusDto.PREDICTION_SERVICE_FAILURE
        else:
            print(f"Failed to delete predictions on project {self.id}. Response: {response}")
            return PredictionErrorStatusDto.UNKNOWN_ERROR

    def _parse_workflow_status(self, item: Dict[str, str]) ->  Union[WorkflowStatusDto, PredictionErrorStatusDto]:
        """Parses the prediction status object to a business class WorkflowStatusDto"""

        prediction_id = self._cast_string_to_uuid_or_none(item.get('workflowId'))
        project_id = self._cast_string_to_uuid_or_none(item.get('projectId'))
        status = self._get_enum_value_or_none(item.get('status'), PredictionStatusDto)
        start_time = item.get('startTime')
        completed_tasks = [self._get_enum_value_or_none(task, PredictionTaskTypeDto) for task in item.get('completedTasks', [])]
        end_time = item.get('endTime', None)

        if None in (prediction_id, project_id, status, start_time, completed_tasks):
            return PredictionErrorStatusDto.INVALID_RESPONSE
        else:
            try:
                date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
                start_datetime = datetime.strptime(start_time, date_format)

                if end_time is not None:
                    end_datetime = datetime.strptime(end_time, date_format)
                else:
                    end_datetime = None

                return WorkflowStatusDto(prediction_id, project_id, status, start_datetime, end_datetime, completed_tasks)
            except ValueError:
                return PredictionErrorStatusDto.INVALID_RESPONSE

    def _get_enum_value_or_none(self, value_str: str, enum_type: Enum) -> Optional[Enum]:
        """Parses the value_str string to the given enum_type or None if does not match"""

        try:
            return enum_type(value_str)
        except ValueError:
            return None

    def _cast_string_to_uuid_or_none(self, string_value: str) -> Optional[uuid.UUID]:
        """Parses the string_value string to a UUID class or None if does not match to a UUID"""

        try:
            if string_value is None:
                return None
            else:
                return uuid.UUID(string_value)
        except ValueError:
            return None

    def get_project_predictions(self, case_ids: list):
        """Returns predictions for a given project and case IDs

        :param case_ids: List of case IDs to predict
        """
        if not case_ids or not all(isinstance(case_id, str) for case_id in case_ids):
            raise ValueError("case_ids should be a non-empty list of strings")

        params = {"projectId": self.id, "caseIds": case_ids}
        route = f"/projects/{self.id}/predictions"
        response = self.api_connector.get_request(route, params=params)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 202:
            return "No prediction available for the given case"
        elif response.status_code == 402:
            return "Prediction is not activated"
        elif response.status_code == 403:
            return "User does not have access to this project or Train API is forbidden for this license/version"
        else:
            return f"Unexpected status code: {response.status_code}. Failed to get predictions."
