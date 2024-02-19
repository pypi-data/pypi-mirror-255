import datetime
import json
import uuid
import sys
from typing import Tuple

import dill
import requests
import pickle
import pandas
import plotly
import msal
import os
import types
import sklearn
import wizata_dsapi
from pandas import DataFrame
from wizata_dsapi import MLModel
import urllib.parse

import string
import random

from .plot import Plot
from .request import Request
from .mlmodel import MLModel
from .experiment import Experiment
from .script import Script
from .execution import Execution
from .dsapi_json_encoder import DSAPIEncoder
from .ds_dataframe import DSDataFrame
from .model_toolkit import predict
from .template import Template, TemplateProperty
from .twinregistration import TwinRegistration
from .twin import Twin
from .datapoint import DataPoint, BusinessType, Label, Category
from .pipeline import Pipeline, PipelineStep, VarType
from .solution_component import SolutionComponent, SolutionType
from .paged_query_result import PagedQueryResult
from .api_interface import ApiInterface


def sanitize_url_parameter(param_value):
    illegal_characters = set(c for c in param_value if not (c.isalnum() or c in '-_., '))
    if illegal_characters:
        raise ValueError(f"illegal characters found in parameter {param_value}: {', '.join(illegal_characters)}")
    encoded_param_value = urllib.parse.quote(param_value)
    return encoded_param_value


class WizataDSAPIClient(ApiInterface):

    def __init__(self,
                 client_id=None,
                 scope=None,
                 tenant_id=None,
                 username=None,
                 password=None,
                 domain="localhost",
                 protocol="https",
                 client_secret=None):

        # properties
        self.domain = domain
        self.protocol = protocol

        # authentication
        self.__username = username
        self.__password = password

        self.__client_id = client_id
        self.__tenant_id = tenant_id
        if tenant_id is not None:
            self.__authority = "https://login.microsoftonline.com/" + tenant_id
        self.__scopes = [scope]

        self.__interactive_token = None
        self.__daemon = False

        if client_secret is not None:
            self.__daemon = True
            self.__confidential_app = msal.ConfidentialClientApplication(
                client_id=self.__client_id,
                client_credential=client_secret,
                authority=self.__authority
            )

        self.__app = msal.PublicClientApplication(
            client_id=self.__client_id,
            authority=self.__authority
        )

    def authenticate(self):
        result = self.__app.acquire_token_interactive(
            scopes=self.__scopes,
            success_template="""<html><body>You are authenticated and your code is running, you can close this page.<script>setTimeout(function(){window.close()}, 3000);</script></body></html> """
        )
        self.__daemon = False
        self.__interactive_token = result["access_token"]

    def __url(self):
        return self.protocol + "://" + self.domain + "/dsapi/"

    def __token(self):
        # Interactive Authentication
        if self.__interactive_token is not None:
            return self.__interactive_token

        if not self.__daemon:
            # Silent Authentication
            result = None
            accounts = self.__app.get_accounts(username=self.__username)
            if accounts:
                # If there is an account in the cache, try to get the token silently
                result = self.__app.acquire_token_silent(scopes=self.__scopes, account=accounts[0])

            if not result:
                # If there is no cached token, try to get a new token using the provided username and password
                result = self.__app.acquire_token_by_username_password(
                    username=self.__username,
                    password=self.__password,
                    scopes=self.__scopes
                )

            if "error_description" in result.keys():
                raise RuntimeError(str(result["error_description"]))

            if "access_token" in result.keys():
                return result["access_token"]
            else:
                raise RuntimeError(str(result))
        else:
            result = self.__confidential_app.acquire_token_silent(scopes=self.__scopes, account=None)

            if not result:
                result = self.__confidential_app.acquire_token_for_client(scopes=self.__scopes)

            if "error_description" in result.keys():
                raise RuntimeError(str(result["error_description"]))

            if "access_token" in result.keys():
                return result["access_token"]

            return result

    def __header(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.__token()}'
        }

    def __raise_error(self, response):
        json_content = response.json()
        if "errors" in json_content.keys():
            message = json_content["errors"][0]["message"]
            return RuntimeError(str(response.status_code) + " - " + message)
        else:
            return RuntimeError(str(response.status_code) + " - " + response.reason)

    def lists(self, str_type):
        """
        lists all elements of a specific entity.

        :param str_type: plural name of the entity (e.g. scripts, plots, mlmodels, dataframes...)
        :return: list of all elements with at least the id property.
        """
        if str_type == "scripts":
            response = requests.request("GET",
                                        self.__url() + "scripts/",
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                scripts = []
                for json_model in response.json():
                    scripts.append(Script(uuid.UUID(json_model["id"])))
                return scripts
            else:
                raise self.__raise_error(response)
        elif str_type == "plots":
            response = requests.request("GET",
                                        self.__url() + "plots/",
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                plots = []
                for plot in response.json():
                    plots.append(Plot(plot["id"]))
                return plots
            else:
                raise self.__raise_error(response)
        elif str_type == "mlmodels":
            response = requests.request("GET",
                                        self.__url() + "mlmodels/",
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                json_models = response.json()
                ml_models = []
                for json_model in json_models:
                    ml_models.append(MLModel(uuid.UUID(json_model["id"])))
                return ml_models
            else:
                raise self.__raise_error(response)
        elif str_type == "dataframes":
            response = requests.request("GET",
                                        self.__url() + "dataframes/",
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                json_dfs = response.json()
                dfs = []
                for json_model in json_dfs:
                    dfs.append(DSDataFrame(uuid.UUID(json_model["id"])))
                return dfs
            else:
                raise self.__raise_error(response)
        elif str_type == "templates":
            response = requests.request("GET",
                                        self.__url() + "templates/",
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                templates_json = response.json()
                templates = []
                for template_json in templates_json:
                    template = Template()
                    template.from_json(template_json)
                    templates.append(template)
                return templates
            else:
                raise self.__raise_error(response)
        elif str_type == "pipelines":
            response = requests.request("GET",
                                        self.__url() + "pipelines/",
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                pipelines_json = response.json()
                pipelines = []
                for pipeline_json in pipelines_json:
                    pipeline = Pipeline()
                    pipeline.from_json(pipeline_json)
                    pipelines.append(pipeline)
                return pipelines
            else:
                raise self.__raise_error(response)
        else:
            raise TypeError("Type not supported.")

    def get(self,
            obj=None,
            script_name=None,
            experiment_key=None,
            pipeline_key=None,
            model_key=None,
            template_key=None,
            twin_hardware_id=None,
            datapoint_hardware_id=None):
        """
        get full content of an object identified with is id.

        :param obj: object of a supported entity with at list its id
        :param script_name: alternatively you can use a function name to get a script
        :param experiment_key: alternatively you can use an experiment key to get an experiment
        :param pipeline_key: alternatively you can use an pipeline key to get a pipeline
        :param model_key: model key you want to get.
        :param template_key: template key you want to get.
        :param twin_hardware_id: twin hardware id you want to get.
        :param datapoint_hardware_id: datapoint hardware id you want to get.
        :return: object completed with all properties on server (None if not found or raise Error if with id)
        """
        if script_name is not None:
            response = requests.request("GET",
                                        self.__url() + "scripts/" + str(script_name) + "/",
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                script_bytes = response.content
                return dill.loads(script_bytes)
            else:
                raise self.__raise_error(response)
        elif experiment_key is not None:
            response = requests.request("GET",
                                        self.__url() + "experiments/",
                                        params={
                                            'key': experiment_key
                                        },
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                for obj_json in response.json():
                    obj = Experiment()
                    obj.from_json(obj_json)
                    return obj
                return None
            else:
                raise self.__raise_error(response)
        elif pipeline_key is not None:
            response = requests.request("GET",
                                        self.__url() + "pipelines/",
                                        params={
                                            'key': pipeline_key
                                        },
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                for obj_json in response.json():
                    obj = Pipeline()
                    obj.from_json(obj_json)
                    return obj
                return None
            else:
                raise self.__raise_error(response)
        elif model_key is not None:
            response = requests.request("GET",
                                        self.__url() + "mlmodels/",
                                        params={
                                            'key': model_key
                                        },
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                for obj_json in response.json():
                    obj = MLModel()
                    obj.from_json(obj_json)
                    return obj
                return None
            else:
                raise self.__raise_error(response)

        elif template_key is not None:
            response = requests.request("GET",
                                        self.__url() + "templates/",
                                        params={
                                            'key': template_key
                                        },
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                for obj_json in response.json():
                    obj = Template()
                    obj.from_json(obj_json)
                    return obj
                return None
            else:
                raise self.__raise_error(response)

        elif twin_hardware_id is not None:
            response = requests.request("GET",
                                        self.__url() + "twins/",
                                        params={
                                            'key': twin_hardware_id
                                        },
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                for obj_json in response.json():
                    obj = Twin()
                    obj.from_json(obj_json)
                    return obj
                return None
            else:
                raise self.__raise_error(response)

        elif datapoint_hardware_id is not None:
            response = requests.request("GET",
                                        self.__url() + "datapoints/",
                                        params={
                                            'key': datapoint_hardware_id
                                        },
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                for obj_json in response.json():
                    obj = DataPoint()
                    obj.from_json(obj_json)
                    return obj
                return None
            else:
                raise self.__raise_error(response)

        elif obj is not None:
            if isinstance(obj, Execution):
                response = requests.request("GET",
                                            self.__url() + "execute/" + str(obj.execution_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    obj.from_json(response.json())
                    return obj
                else:
                    raise self.__raise_error(response)
            if isinstance(obj, MLModel):
                response = requests.request("GET",
                                            self.__url() + "mlmodels/" + str(obj.model_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    mlmodel_bytes = response.content
                    return pickle.loads(mlmodel_bytes)
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, Script):
                response = requests.request("GET",
                                            self.__url() + "scripts/" + str(obj.name) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    script_bytes = response.content
                    return dill.loads(script_bytes)
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, Plot):
                response = requests.request("GET",
                                            self.__url() + "plots/" + str(obj.plot_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    obj.from_json(response.json())
                    return obj
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, DSDataFrame):
                response = requests.request("GET",
                                            self.__url() + "dataframes/" + str(obj.df_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    df_bytes = response.content
                    return pickle.loads(df_bytes)
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, Request):
                response = requests.request("POST", self.__url() + "execute/data",
                                            headers=self.__header(),
                                            data=json.dumps(obj.prepare(), cls=DSAPIEncoder))
                if response.status_code == 200:
                    return pickle.loads(response.content)
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, Experiment):
                response = requests.request("GET",
                                            self.__url() + "experiments/" + str(obj.experiment_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    obj.from_json(response.json())
                    return obj
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, Pipeline):
                response = requests.request("GET",
                                            self.__url() + "pipelines/" + str(obj.pipeline_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    obj.from_json(response.json())
                    return obj
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, Template):
                response = requests.request("GET",
                                            self.__url() + "templates/" + str(obj.template_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    obj.from_json(response.json())
                    return obj
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, DataPoint):
                response = requests.request("GET",
                                            self.__url() + "datapoints/" + str(obj.datapoint_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    obj.from_json(response.json())
                    return obj
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, Twin):
                response = requests.request("GET",
                                            self.__url() + "twins/" + str(obj.twin_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    obj.from_json(response.json())
                    return obj
                else:
                    raise self.__raise_error(response)
            else:
                raise TypeError("Type not supported.")

    def get_categories(self) -> dict:
        """
        get a name / uuid dictionary with all categories in platform.
        """
        response = requests.request("GET",
                                    self.__url() + "datapoints/categories/",
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            categories_json = response.json()
            categories_dict = {}
            for category_json in categories_json:
                categories_dict[category_json["name"]] = category_json["id"]
            return categories_dict
        else:
            raise self.__raise_error(response)

    def get_business_labels(self) -> dict:
        """
        get a name / uuid dictionary with all business labels in platform.
        """
        response = requests.request("GET",
                                    self.__url() + "components/labels/",
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            categories_json = response.json()
            categories_dict = {}
            for category_json in categories_json:
                categories_dict[category_json["name"]] = category_json["id"]
            return categories_dict
        else:
            raise self.__raise_error(response)

    def create(self, obj):
        """
        create and save an object on the server

        :param obj: object to save on the server (any id is ignored and replaced)
        :return: id of created object
        """
        if callable(obj) and isinstance(obj, types.FunctionType):
            obj = Script(
                function=obj
            )
        if isinstance(obj, Script):
            response = requests.post(self.__url() + "scripts/",
                                     headers=self.__header(),
                                     data=dill.dumps(obj))
            if response.status_code == 200:
                obj.script_id = uuid.UUID(response.json()["id"])
                return obj.script_id
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Experiment):
            if len(obj.key) > 16:
                raise ValueError('experiment key is limited to 16 char.')
            response = requests.post(self.__url() + "experiments/",
                                     headers=self.__header(),
                                     data=json.dumps(obj.to_json()))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Pipeline):
            response = requests.post(self.__url() + "pipelines/",
                                     headers=self.__header(),
                                     data=json.dumps(obj.to_json()))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Template):
            response = requests.post(self.__url() + "templates/",
                                     headers=self.__header(),
                                     data=json.dumps(obj.to_json()))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, DataPoint):
            response = requests.post(self.__url() + "datapoints/",
                                     headers=self.__header(),
                                     data=json.dumps(obj.to_json()))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Twin):
            response = requests.post(self.__url() + "twins/",
                                     headers=self.__header(),
                                     data=json.dumps(obj.to_json()))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        else:
            raise TypeError("Type not supported.")

    def update(self, obj):
        """
        update and save an object on the server

        :param obj: object to update on the server
        :return: None
        """
        if callable(obj) and isinstance(obj, types.FunctionType):
            obj = Script(
                function=obj
            )
        if isinstance(obj, Script):
            response = requests.put(self.__url() + "scripts/" + str(obj.script_id) + "/",
                                    headers=self.__header(),
                                    data=dill.dumps(obj))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Experiment):
            response = requests.put(self.__url() + "experiments/" + str(obj.experiment_id) + "/",
                                    headers=self.__header(),
                                    data=json.dumps(obj.to_json()))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Template):
            response = requests.put(self.__url() + "templates/" + str(obj.template_id) + "/",
                                    headers=self.__header(),
                                    data=json.dumps(obj.to_json()))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Pipeline):
            response = requests.put(self.__url() + "pipelines/" + str(obj.pipeline_id) + "/",
                                    headers=self.__header(),
                                    data=json.dumps(obj.to_json()))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, DataPoint):
            response = requests.put(self.__url() + "datapoints/" + str(obj.datapoint_id) + "/",
                                    headers=self.__header(),
                                    data=json.dumps(obj.to_json()))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Twin):
            response = requests.put(self.__url() + "twins/" + str(obj.twin_id) + "/",
                                    headers=self.__header(),
                                    data=json.dumps(obj.to_json()))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        else:
            raise TypeError("Type not supported.")

    def upsert(self, obj):
        """
        upsert on object on the server
        work with Script, MLModel or directly a function name

        :param obj: object to upsert on the server
        :return: ID of the object created or updated
        """
        if callable(obj) and isinstance(obj, types.FunctionType):
            obj = Script(
                function=obj
            )
        if isinstance(obj, Script):
            response = requests.put(self.__url() + "scripts/",
                                    headers=self.__header(),
                                    data=dill.dumps(obj))
            if response.status_code == 200:
                obj.script_id = uuid.UUID(response.json()['id'])
                return obj.script_id
            else:
                raise self.__raise_error(response)
        if isinstance(obj, MLModel):
            response = requests.put(self.__url() + "mlmodels/",
                                    headers=self.__header(),
                                    data=pickle.dumps(obj))
            if response.status_code == 200:
                obj.model_id = uuid.UUID(response.json()['id'])
                return obj.model_id
            else:
                raise self.__raise_error(response)
        if isinstance(obj, Template):
            return self.upsert_template(obj.key, obj.name)
        if isinstance(obj, Pipeline):
            return self.upsert_pipeline(pipeline=obj)
        if isinstance(obj, DataPoint):
            return self.upsert_datapoint(datapoint=obj)
        if isinstance(obj, Twin):
            return self.upsert_twin(twin=obj)
        else:
            raise TypeError("Type not supported.")

    def delete(self, obj):
        """
        delete an object on the server

        :param obj: object to delete including all content
        :return: None
        """
        if isinstance(obj, Pipeline):
            response = requests.delete(self.__url() + "pipelines" + "/" + str(obj.pipeline_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        if isinstance(obj, Experiment):
            response = requests.delete(self.__url() + "experiments" + "/" + str(obj.experiment_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        if isinstance(obj, Script):
            response = requests.delete(self.__url() + "scripts" + "/" + str(obj.script_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Plot):
            response = requests.delete(self.__url() + "plots" + "/" + str(obj.plot_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, MLModel):
            response = requests.delete(self.__url() + "mlmodels" + "/" + str(obj.model_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, DSDataFrame):
            response = requests.delete(self.__url() + "dataframes" + "/" + str(obj.df_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Template):
            response = requests.delete(self.__url() + "templates" + "/" + str(obj.template_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, DataPoint):
            response = requests.delete(self.__url() + "datapoints" + "/" + str(obj.datapoint_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Twin):
            response = requests.delete(self.__url() + "twins" + "/" + str(obj.twin_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        else:
            raise TypeError("Type not supported.")

    def query(self,
              datapoints: list[str] = None,
              start: datetime = None,
              end: datetime = None,
              interval: int = None,
              agg_method: str = "mean",
              template: str = None,
              twin: str = None,
              null: str = None,
              filters: dict = None,
              options: dict = None) -> pandas.DataFrame:
        """
        Query a dataframe from API.
        :param agg_method:
        :param datapoints: list of datapoints to fetch.
        :param start: start datetime of range to fetch
        :param end: end datetime of range to fetch
        :param interval: interval in milliseconds.
        :param template: template to fetch.
        :param twin: hardware ID of twin to fetch based on template.
        :param null: By default at 'drop' and dropping NaN values. If not intended behavior please set it to 'ignore' or 'all'.
        :param filters: dict of filters.
        :param options: dict of options.
        :return: dataframe
        """
        request = Request()

        if datapoints is not None:
            request.add_datapoints(datapoints)

        if start is not None:
            request.start = start
        else:
            raise ValueError('start datetime is required.')

        if end is not None:
            request.end = end
        else:
            raise ValueError('end datetime is required.')

        if null is not None:
            request.null = null

        if interval is None:
            raise ValueError('interval is required.')
        request.set_aggregation(agg_method, interval)

        if template is not None and twin is not None:
            request.select_template(
                template_key=template,
                twin_hardware_id=twin
            )

        if filters is not None:
            request.filters = filters

        if options is not None:
            request.options = options

        return self.get(request)

    def get_ts_query(self,
                     datapoints: list[str] = None,
                     start: datetime = None,
                     end: datetime = None,
                     interval: int = None,
                     agg_method: str = "mean",
                     template: str = None,
                     twin: str = None,
                     null: str = None,
                     filters: dict = None,
                     options: dict = None) -> str:
        """
        Get a Query string to Timeseries Database.
        :param agg_method:
        :param datapoints: list of datapoints to fetch.
        :param start: start datetime of range to fetch
        :param end: end datetime of range to fetch
        :param interval: interval in milliseconds.
        :param template: template to fetch.
        :param twin: hardware ID of twin to fetch based on template.
        :param null: By default at 'drop' and dropping NaN values. If not intended behavior please set it to 'ignore' or 'all'.
        :param filters: dict of filters.
        :param options: dict of options.
        :return: dataframe
        """
        request = Request()

        if datapoints is not None:
            request.add_datapoints(datapoints)

        if start is not None:
            request.start = start
        else:
            raise ValueError('start datetime is required.')

        if end is not None:
            request.end = end
        else:
            raise ValueError('end datetime is required.')

        if null is not None:
            request.null = null

        if interval is None:
            raise ValueError('interval is required.')
        request.set_aggregation(agg_method, interval)

        if template is not None and twin is not None:
            request.select_template(
                template_key=template,
                twin_hardware_id=twin
            )

        if filters is not None:
            request.filters = filters

        if options is not None:
            request.options = options

        response = requests.request("POST", self.__url() + "data/string",
                                    headers=self.__header(),
                                    data=json.dumps(request.prepare(), cls=DSAPIEncoder))
        if response.status_code == 200:
            return response.json()
        else:
            raise self.__raise_error(response)

    def __execute(self,
                  execution: Execution = None,
                  request: Request = None,
                  dataframe=None,
                  script=None,
                  ml_model=None,
                  isAnomalyDetection=False,
                  function=None,
                  experiment=None,
                  properties: dict = None,
                  pipeline=None,
                  twin=None,
                  mode: str = 'experiment'
                  ) -> Execution:
        """
        internal function - deprecated - please use experiment() or test_run() instead.
        """
        # Prepare
        if execution is None:
            execution = Execution()
        if request is not None:
            execution.request = request
        if dataframe is not None:
            if isinstance(dataframe, pandas.DataFrame):
                execution.dataframe = dataframe
            elif isinstance(dataframe, DSDataFrame):
                execution.input_ds_dataframe = dataframe
        if script is not None:
            if isinstance(script, uuid.UUID) or (isinstance(script, str) and is_valid_uuid(script)):
                execution.script = Script(script)
            elif isinstance(script, str):
                execution.script = self.get(script_name=script)
            elif isinstance(script, Script):
                execution.script = script
        if ml_model is not None:
            if isinstance(ml_model, uuid.UUID) or (isinstance(ml_model, str) and is_valid_uuid(ml_model)):
                execution.ml_model = MLModel(ml_model)
            elif isinstance(ml_model, str):
                execution.ml_model = self.get(model_key=ml_model)
            elif isinstance(ml_model, MLModel):
                execution.ml_model = ml_model

        if isAnomalyDetection:
            execution.isAnomalyDetection = True
        if function is not None:
            execution.function = function
        if experiment is not None:
            if isinstance(experiment, uuid.UUID):
                execution.experiment_id = experiment
            elif isinstance(experiment, str):
                execution.experiment_id = self.get(experiment_key=experiment).experiment_id
            elif isinstance(experiment, Experiment):
                execution.experiment_id = experiment.experiment_id
        if properties is not None and isinstance(properties, dict):
            execution.properties = properties

        if pipeline is not None:
            if isinstance(pipeline, uuid.UUID) or (isinstance(pipeline, str) and is_valid_uuid(pipeline)):
                execution.pipeline = Pipeline(pipeline_id=uuid.UUID(pipeline))
            elif isinstance(pipeline, str):
                execution.pipeline = self.get(pipeline_key=pipeline)
            elif isinstance(pipeline, Pipeline):
                execution.pipeline = pipeline
        if twin is not None:
            if execution.properties is None:
                execution.properties = {}
            if isinstance(twin, uuid.UUID) or (isinstance(twin, str) and is_valid_uuid(twin)):
                execution.properties["twinId"] = str(twin)
            elif isinstance(twin, str):
                execution.properties["twinId"] = str(self.get(twin_hardware_id=twin).twin_id)
            elif isinstance(twin, Twin):
                execution.properties["twinId"] = str(twin.twin_id)

        # Execute
        if isinstance(execution, Execution):
            response = requests.post(f"{self.__url()}execute/?mode={mode}",
                                     headers=self.__header(),
                                     data=json.dumps(execution.to_json(), cls=DSAPIEncoder))

            # Parse
            if response.status_code == 200:
                obj = response.json()
                result_execution = Execution()
                result_execution.from_json(obj)
                if "plots" in obj.keys():
                    for plot in obj["plots"]:
                        result_execution.plots.append(self.get(Plot(plot_id=plot["id"])))
                if "models" in obj.keys():
                    for mlmodel in obj["models"]:
                        result_execution.models.append(self.get(MLModel(model_id=mlmodel["id"])))
                if "resultDataframe" in obj.keys() and obj["resultDataframe"]["id"] is not None:
                    result_execution.output_ds_dataframe = self.get(DSDataFrame(df_id=obj["resultDataframe"]["id"]))
                if "anomaliesList" in obj.keys() and isinstance(obj["anomaliesList"], str):
                    result_execution.anomalies = json.loads(obj["anomaliesList"])
                return result_execution
            else:
                raise self.__raise_error(response)
        else:
            raise TypeError("No execution have been loaded from parameters.")

    def experiment(self, experiment, pipeline, twin=None, properties: dict = None) -> Execution:
        """
        experiment and train models with a pipeline.

        - existing experiment is required (use create or upsert_experiment(key, name)).
        - if your pipeline is templated please provide a twin.
        - please provide all variables and parameters required through properties.
        - return an execution
            - check status with "wizata_dsapi.api().get(execution).status"
            - see plots with "wizata_dsapi.api().plots(execution)"

        :param experiment: existing experiment identified by its id (uuid or wizata_dsapi.Experiment) or key (str).
        :param pipeline: pipeline identified by its id (uuid or wizata_dsapi.Pipeline) or key (str) .
        :param twin: twin identified by its id (uuid or wizata_dsapi.Twin) or hardware ID (str)(optional).
        :param properties: dictionary containing override for variables or additional parameters for your script.
        """
        return self.__execute(
            experiment=experiment,
            pipeline=pipeline,
            twin=twin,
            properties=properties,
            mode='experiment'
        )

    def run(self, pipeline, twin=None, properties: dict = None) -> Execution:
        """
        run a pipeline.

        - existing models are used for simulation and prediction.
        - caution this might affect data inside platform or trigger automation.
        - if your pipeline is templated please provide a twin.
        - please provide all variables and parameters required through properties.
        - return an execution
            - check status with "wizata_dsapi.api().get(execution).status"
            - check results in platform (dashboard/explorer) or perform queries.

        :param pipeline: pipeline identified by its id (uuid or wizata_dsapi.Pipeline) or key (str).
        :param twin: twin identified by its id (uuid or wizata_dsapi.Twin) or hardware ID (str).
        :param properties: dictionary containing override for variables or additional parameters for your script.
        """
        return self.__execute(
            pipeline=pipeline,
            twin=twin,
            properties=properties,
            mode='production'
        )

    def multi_run(self, pipeline_id, twin_ids: list, properties: dict = None):
        """
        run a pipeline against one or multiple twin in production.
        :param pipeline_id: UUID or str UUID of a pipeline.
        :param twin_ids: list of UUID or str UUID of asset registered on the pipeline.
        :param properties: optional properties of a pipeline (serializable as JSON).
        :return: list of executions IDs ("ids" key)
        """
        if isinstance(pipeline_id, uuid.UUID):
            pipeline_id = str(pipeline_id)
        else:
            pipeline_id = str(uuid.UUID(pipeline_id))

        if twin_ids is None or len(twin_ids) == 0:
            raise ValueError("please provide at least a valid twin id")

        formatted_ids = []
        for twin_id in twin_ids:
            if isinstance(twin_id, uuid.UUID):
                formatted_ids.append(str(twin_id))
            elif isinstance(twin_id, str):
                formatted_ids.append(str(uuid.UUID(twin_id)))
            else:
                raise TypeError(f'wrong type for twin-id')
        payload = {
            "pipelineId": pipeline_id,
            "twinIds": formatted_ids
        }
        if properties is not None:
            payload["properties"] = properties
        response = requests.post(f"{self.__url()}execute/pipelines/",
                                 headers=self.__header(),
                                 data=json.dumps(payload, cls=DSAPIEncoder))
        if response.status_code == 200:
            obj = response.json()
            return obj
        else:
            raise self.__raise_error(response)

    def plot(self, plot_id: str = None, plot: Plot = None, figure=None,):
        """
        Fetch and show plot.
        :param plot: Wizata Plot Object
        :param figure: JSON Figure
        :param plot_id: Plot Id
        :return: plotly figure
        """
        if plot is not None and plot.figure is not None:
            return plotly.io.from_json(plot.figure)
        elif plot is not None and plot.figure is None:
            plot = self.get(plot)
            if plot.figure is not None:
                return plotly.io.from_json(plot.figure)
            else:
                raise ValueError('No plot has been fetch.')
        elif figure is not None:
            return plotly.io.from_json(plot.figure)
        elif plot_id is not None:
            plot = self.get(Plot(plot_id=plot_id))
            if plot.figure is not None:
                return plotly.io.from_json(plot.figure)
            else:
                raise ValueError('No plot has been fetch.')
        else:
            raise KeyError('No valid arguments.')

    def plots(self, execution):
        """
        get all plot for an execution.
        :param execution: id or Execution.
        :return: list of plots.
        """

        if execution is None:
            raise ValueError("execution cannot be None to retrieve plot")
        if isinstance(execution, uuid.UUID):
            execution_id = execution
        elif isinstance(execution, str):
            execution_id = uuid.UUID(execution)
        elif isinstance(execution, Execution):
            execution_id = execution.execution_id
        else:
            raise Exception(f'unsupported type {execution}')

        response = requests.request("GET",
                                    self.__url() + f"plots/?generatedById={execution_id}",
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            plots = []
            for plot in response.json():
                plots.append(self.plot(plot_id=str(plot["id"])))
            return plots
        else:
            raise self.__raise_error(response)

    def register_model(self,
                       model_key,
                       train_model,
                       df: pandas.DataFrame,
                       scaler=None,
                       has_anomalies: bool = False,
                       has_target_feat: bool = False,
                       experiment_key = None) -> tuple[MLModel, pandas.DataFrame]:
        """
        Register a Machine Learning model to Wizata.
        Model is tested by the API against a sample dataframe.
        :param model_key: logical string id to identify the model.
        :param train_model: trained model (must be compatible with pickle library)
        :param df: sample dataframe.
        :param scaler: scaler (must be compatible with pickle library)
        :param has_anomalies: True is model generate Anomalies
        :param has_target_feat: True if model need a target feature to be selected
        :param experiment_key: Reference of an experiment to which link the generated ML Model
        :return: registered ML Model , pandas.DataFrame
        """
        if model_key is None and isinstance(model_key, str):
            raise ValueError('Please provide a str Model Key to identify the model.')
        if train_model is None:
            raise ValueError('Trained Machine Learning model should not be null')
        elif df is None:
            raise ValueError('A sample dataframe must be provided')

        # Create a ML Model object
        ml_model = MLModel()
        ml_model.trained_model = train_model
        if scaler is not None:
            ml_model.scaler = scaler
        ml_model.has_anomalies = has_anomalies
        ml_model.has_target_feat = has_target_feat
        ml_model.input_columns = df.columns
        ml_model.key = model_key

        if experiment_key is not None:
            ml_model.experimentId = self.get(experiment_key=experiment_key).experiment_id

        try:
            result_df = predict(df, ml_model)
            if result_df is not None:
                ml_model.status = "valid"
                self.upsert(ml_model)
                return ml_model, result_df
            else:
                raise RuntimeError('no dataframe was generated by your model while testing predict capabilities')
        except Exception as e:
            raise RuntimeError('not able to validated the model : ' + str(e))

    def upsert_experiment(self, key: str, name: str):
        """
        Upsert an experiment.
        :param key: unique key identifying the experiment.
        :param name: display name of the experiment
        :return: upserted experiment.
        """
        experiment = self.get(experiment_key=key)
        if experiment is not None:
            found = True
            experiment.name = name
        else:
            experiment = Experiment(
                key=key,
                name=name
            )
            found = False

        if not found:
            return self.create(experiment)
        else:
            return self.update(experiment)

    def upsert_template(self, key: str, name: str):
        """
        Upsert a template.
        :param key: unique key identifying the template.
        :param name: display name of the template
        :return: upserted template.
        """

        template = self.get(template_key=key)
        if template is not None:
            found = True
            template.name = name
        else:
            template = Template(
                key=key,
                name=name
            )
            found = False

        if not found:
            return self.create(template)
        else:
            return self.update(template)

    def upsert_pipeline(self, pipeline: Pipeline):
        """
        Upsert a template (ignore ID, use the key)
        :return: upserted template.
        """

        get = self.get(pipeline_key=pipeline.key)
        if get is not None:
            pipeline.pipeline_id = get.pipeline_id
            return self.update(pipeline)
        else:
            return self.create(pipeline)

    def upsert_datapoint(self, datapoint: DataPoint):
        """
        Upsert a datapoint (ignore ID, use the key)
        :return: upsert datapoint.
        """
        get = self.get(datapoint_hardware_id=datapoint.hardware_id)
        if get is not None:
            datapoint.datapoint_id = get.datapoint_id
            return self.update(datapoint)
        else:
            return self.create(datapoint)

    def upsert_twin(self, twin: Twin):
        """
        Upsert a twin (ignore ID, use the key)
        :return: upsert twin.
        """

        get = self.get(twin_hardware_id=twin.hardware_id)
        if get is not None:
            twin.twin_id = get.twin_id
            return self.update(twin)
        else:
            return self.create(twin)

    def add_template_property(self,
                              template,
                              property_name: str,
                              property_type: str = "datapoint",
                              is_required: bool = True) -> wizata_dsapi.TemplateProperty:

        # check type
        p_type = VarType(property_type)

        if isinstance(template, str):
            template_id = self.get(template_key=template).template_id
        elif isinstance(template, wizata_dsapi.Template):
            template_id = template.template_id
        elif isinstance(template, uuid.UUID):
            template_id = template
        else:
            raise TypeError('template should be a UUID or at least a key str referring template or a proper wizata_dsapi Template')

        template_property = wizata_dsapi.TemplateProperty(
            template_id=template_id,
            p_type=p_type,
            name=property_name,
            required=is_required
        )
        response = requests.post(self.__url() + "templateproperties/",
                                 headers=self.__header(),
                                 data=json.dumps(template_property.to_json()))
        if response.status_code == 200:
            return template_property
        else:
            raise self.__raise_error(response)

        # if isinstance(template, str):
        #     template = self.get(template_key=template)
        # elif not isinstance(template, Template):
        #     raise TypeError('template must be a key str referring template or a proper wizata_dsapi Template')
        #
        # if property_name is None:
        #     raise ValueError('please provide a valid name for the property')
        #
        # property_dict = {
        #     "type": p_type.value,
        #     "name": property_name,
        #     "required": is_required
        # }
        #
        # response = requests.post(self.__url() + "templates/" + str(template.template_id) + '/properties/',
        #                          headers=self.__header(),
        #                          data=json.dumps(property_dict))
        # if response.status_code == 200:
        #     return
        # else:
        #     raise self.__raise_error(response)

    def remove_template_property(self, template, property_name: str):

        if isinstance(template, str):
            template = self.get(template_key=template)
        elif not isinstance(template, Template):
            raise TypeError('template must be a key str referring template or a proper wizata_dsapi Template')

        if property_name is None:
            raise ValueError('please provide a valid name for the property')

        property_dict = {
            "name": property_name
        }

        response = requests.delete(self.__url() + "templates/" + str(template.template_id) + '/properties/',
                                   headers=self.__header(),
                                   data=json.dumps(property_dict))
        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def get_registrations(self, template) -> list:
        """
        retrieve all registrations for
        :param template: template object, UUID or str key.
        :return: list of twin registration.
        """

        if template is None:
            raise ValueError('template must be specified.')
        elif isinstance(template, uuid.UUID):
            template = self.get(wizata_dsapi.Template(template_id=template))
        elif isinstance(template, str):
            template = self.get(template_key=template)
        elif not isinstance(template, Template):
            raise TypeError('template must be UUID, a key str referring template or a proper wizata_dsapi Template')
        if template is None:
            raise ValueError('template cannot be found on server')

        response = requests.get(self.__url() + "templates/" + str(template.template_id) + '/registrations/',
                                headers=self.__header())
        if response.status_code == 200:
            registrations_json = response.json()
            registrations = []
            for twin_registration_json in registrations_json:
                registration = TwinRegistration()
                registration.from_json(twin_registration_json)
                registrations.append(registration)
            return registrations
        else:
            raise self.__raise_error(response)

    def register_twin(self, template, twin, properties: dict, override=True):
        """
        register a twin on a specific template using a map.
        :param template: template object, UUID or str key.
        :param twin: twin object, UUID or str key.
        :param properties: dict where key = template property and value = datapoint name or const value (str, int, float, relative or epoch datetime).
        :param override: by default at True - allow overriding any existing subscription
        """

        if template is None:
            raise ValueError('template must be specified.')
        elif isinstance(template, uuid.UUID):
            template = self.get(wizata_dsapi.Template(template_id=template))
        elif isinstance(template, str):
            template = self.get(template_key=template)
        elif not isinstance(template, Template):
            raise TypeError('template must be UUID, a key str referring template or a proper wizata_dsapi Template')

        if template is None:
            raise ValueError('template cannot be found on server')

        if twin is None:
            raise ValueError('twin must be specified.')
        elif isinstance(twin, uuid.UUID):
            twin_id = twin
        elif isinstance(twin, str):
            twin_id = self.get(twin_hardware_id=twin).twin_id
        elif isinstance(twin, Twin):
            twin_id = twin.twin_id
        else:
            raise TypeError('twin must be UUID, a key str referring hardware ID or a proper wizata_dsapi Twin')

        if template.properties is None or len(template.properties) == 0:
            raise ValueError('template chosen does not contains any properties')

        if properties is None or len(properties.keys()) == 0:
            raise ValueError('your map dictionary must contains properties matching template')

        twin_properties = {
            "properties": []
        }
        for key in properties.keys():
            property_type = None
            for template_property in template.properties:
                template_property: TemplateProperty
                if key == template_property.name:
                    property_type = template_property.p_type
            if property_type is None:
                raise ValueError(f'cannot find property {key} in template or cannot determine its type')
            twin_properties["properties"].append({
                'name': key,
                property_type.value: properties[key]
            })

        # Check if already exist
        exists = False
        response_exists = requests.get(self.__url() + "templates/" + str(template.template_id)
                                       + '/registrations/' + str(twin_id) + '/',
                                       headers=self.__header())
        if response_exists.status_code == 200:
            exists = True

        if exists and not override:
            raise ValueError("registration already exists and override not allowed.")

        if exists and override:
            response = requests.put(self.__url() + "templates/" + str(template.template_id)
                                    + '/registrations/' + str(twin_id) + '/',
                                    headers=self.__header(),
                                    data=json.dumps(twin_properties))
        else:
            response = requests.post(self.__url() + "templates/" + str(template.template_id)
                                     + '/registrations/' + str(twin_id) + '/',
                                     headers=self.__header(),
                                     data=json.dumps(twin_properties))

        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def unregister_twin(self, template, twin):
        """
        un-register a twin from a specific template.
        :param template: template object, UUID or str key.
        :param twin: twin object, UUID or str key.
        """

        if template is None:
            raise ValueError('template must be specified.')
        elif isinstance(template, uuid.UUID):
            template = self.get(wizata_dsapi.Template(template_id=template))
        elif isinstance(template, str):
            template = self.get(template_key=template)
        elif not isinstance(template, Template):
            raise TypeError('template must be UUID, a key str referring template or a proper wizata_dsapi Template')

        if twin is None:
            raise ValueError('twin must be specified.')
        elif isinstance(twin, uuid.UUID):
            twin_id = twin
        elif isinstance(twin, str):
            twin_id = self.get(twin_hardware_id=twin).twin_id
        elif isinstance(twin, Twin):
            twin_id = twin.twin_id
        else:
            raise TypeError('twin must be UUID, a key str referring hardware ID or a proper wizata_dsapi Twin')

        response = requests.delete(self.__url() + "templates/" + str(template.template_id)
                                   + '/registrations/' + str(twin_id) + '/',
                                   headers=self.__header())
        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def create_component(self, component: SolutionComponent):
        """
        create a component based on its ID.
        """
        if component is None:
            raise ValueError("component cannot be null")

        response = requests.post(self.__url() + "components/",
                                 headers=self.__header(),
                                 data=json.dumps(component.to_json()))

        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def update_component(self, component: SolutionComponent):
        """
        update a component based on its ID.
        """
        if component is None:
            raise ValueError("component cannot be null")

        response = requests.put(self.__url() + "components/" + str(component.solution_component_id) + "/",
                                 headers=self.__header(),
                                 data=json.dumps(component.to_json()))

        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def get_datapoint_mappings(self, registration):
        """
        get datapoint mapping from a registration.
        """
        if isinstance(registration, uuid.UUID):
            registration = str(registration)
        elif isinstance(registration, TwinRegistration):
            registration = str(registration.twin_registration_id)
        response = requests.request("GET",
                                    self.__url() + "registrations/" + registration + "/mapping/",
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            return response.json()
        else:
            raise self.__raise_error(response)

    def get_components(self,
                       label_id: uuid.UUID = None,
                       twin_id: uuid.UUID = None,
                       template_id: uuid.UUID = None,
                       owner_id: uuid.UUID = None,
                       organization_only: bool = False,
                       name: str = None):
        """
        get components
        :param label_id: filter on a specific label
        :param template_id: filter on a specific template
        :param twin_id: filter on a specific twin
        :param owner_id: filter on a specific owner_id
        :param organization_only: work only with organization components (by default - False)
        :param name: filter on a specific name (contains)
        """
        params = {}
        if label_id is not None:
            params['labelId'] = str(label_id)
        if twin_id is not None:
            params['twinId'] = str(twin_id)
        if template_id is not None:
            params['templateId'] = str(template_id)
        if owner_id is not None:
            params['ownerId'] = str(owner_id)
        if organization_only:
            params['organizatianOnly'] = True
        if name is not None:
            params['name'] = str(name)
        response = requests.request("GET",
                                    self.__url() + "components/",
                                    params=params,
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            components = []
            for json_model in response.json():
                component = SolutionComponent()
                component.from_json(json_model)
                components.append(component)
            return components
        else:
            raise self.__raise_error(response)

    def delete_component(self, component_id: uuid.UUID):
        response = requests.delete(self.__url() + "components/" + str(component_id) + '/',
                                   headers=self.__header())
        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def search_datapoints(self,
                          page: int = 1,
                          size: int = 20,
                          sort: str = "id",
                          direction: str = "asc",
                          hardware_id: str = None,
                          categories: list = None,
                          business_types: list = None,
                          twin=None,
                          recursive: bool = False) -> PagedQueryResult:
        """
        get datapoints with a paged query.
        :param page: numero of the page - default 1.
        :param size: quantity per page - default 20 max 100.
        :param sort: column to sort results - default id.
        :param direction: sorting direction by default asc, accept also desc.
        :param hardware_id: filter on a specific hardware ID name or partial name.
        :param business_types: list of BusinessType or str.
        :param categories: list of UUID or Category.
        :param twin: uuid or Twin element to search datapoints.
        :param recursive: set to True in combination of a twin to look inside all sub-twins recursively.
        :return: PagedQueryResults, check total for number of potential results and results for the list of entity.
        """
        query = PagedQueryResult(
            page=page,
            size=size,
            sort=sort,
            direction=direction
        )

        if sort not in ["id", "hardwareId", "createdDate", "createdById", "updatedDate", "updatedById",
                        "unitId", "businessType", "categoryId", "description"]:
            raise ValueError("invalid sort column")

        parameter_str = "?page=" + str(page) + "&size=" + str(size) + "&sort=" + str(sort) + "&direction=" + str(direction)
        if hardware_id is not None:
            parameter_str += "&hardwareId=" + sanitize_url_parameter(hardware_id)
        if business_types is not None and len(business_types) > 0:
            list_str = []
            for businessType in business_types:
                if isinstance(businessType, str):
                    list_str.append(businessType)
                elif isinstance(businessType, BusinessType):
                    list_str.append(businessType.value)
                else:
                    raise ValueError('business type must be a BusinessType or a str')
            parameter_str += "&businessTypes=" + sanitize_url_parameter(",".join(list_str))
        if categories is not None and len(categories) > 0:
            list_str = []
            for categoryId in categories:
                if isinstance(categoryId, uuid.UUID):
                    list_str.append(str(categoryId))
                if isinstance(categoryId, str):
                    list_str.append(categoryId)
                elif isinstance(categoryId, Category):
                    list_str.append(str(categoryId.category_id))
                else:
                    raise ValueError('category must be a Category, UUID or a str UUID')
            parameter_str += "&categoryIds=" + sanitize_url_parameter(",".join(list_str))

        if recursive is not None and recursive:
            parameter_str += "&recursive=" + sanitize_url_parameter("true")

        if twin is not None:
            if isinstance(twin, uuid.UUID):
                twin = str(twin)
            if isinstance(twin, str):
                twin = twin
            elif isinstance(twin, Twin):
                twin = str(twin.twin_id)
            else:
                raise ValueError('category must be a Twin, UUID or a str UUID')
            parameter_str += "&twinId=" + sanitize_url_parameter(twin)

        response = requests.request("GET",
                                    self.__url() + "datapoints/filter" + parameter_str,
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            response_obj = response.json()
            query.total = int(response_obj["total"])
            query.results = []
            for obj in response_obj["results"]:
                datapoint = DataPoint()
                datapoint.from_json(obj)
                query.results.append(datapoint)
            return query
        else:
            raise self.__raise_error(response)

    def search_twins(self,
                     page: int = 1,
                     size: int = 20,
                     sort: str = "id",
                     direction: str = "asc",
                     hardware_id: str = None,
                     name: str = None,
                     parents: list = None) -> PagedQueryResult:
        """
        get twins with a paged query.
        :param page: numero of the page - default 1.
        :param size: quantity per page - default 20 max 100.
        :param sort: column to sort results - default id.
        :param direction: sorting direction by default asc, accept also desc.
        :param hardware_id: filter on a specific hardware ID name or partial name.
        :param name: name or part of twin name.
        :param parents: list of all possible parents (Twin, UUID, or str UUID).
        :return: PagedQueryResults, check total for number of potential results and results for the list of entity.
        """
        query = PagedQueryResult(
            page=page,
            size=size,
            sort=sort,
            direction=direction
        )

        if sort not in ["id", "hardwareId", "createdDate", "createdById", "updatedDate", "updatedById",
                        "name", "description"]:
            raise ValueError("invalid sort column")

        parameter_str = "?page=" + str(page) + "&size=" + str(size) + "&sort=" + str(sort) + "&direction=" + str(direction)
        if hardware_id is not None:
            parameter_str += "&hardwareId=" + sanitize_url_parameter(hardware_id)
        if parents is not None and len(parents) > 0:
            list_str = []
            for parent in parents:
                if isinstance(parent, uuid.UUID):
                    list_str.append(str(parent))
                elif isinstance(parent, str):
                    list_str.append(parent)
                elif isinstance(parent, Twin):
                    list_str.append(str(parent.twin_id))
                else:
                    raise ValueError('parent must be a Twin or a str')
            parameter_str += "&parentIds=" + sanitize_url_parameter(",".join(list_str))

        if name is not None:
            parameter_str += "&name=" + sanitize_url_parameter(name)

        response = requests.request("GET",
                                    self.__url() + "twins/filter" + parameter_str,
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            response_obj = response.json()
            query.total = int(response_obj["total"])
            query.results = []
            for obj in response_obj["results"]:
                twin = Twin()
                twin.from_json(obj)
                query.results.append(twin)
            return query
        else:
            raise self.__raise_error(response)


def api() -> WizataDSAPIClient:
    """
    Create a WizataDSAPIClient from environment variables.
    :return: client
    """
    protocol = 'https'

    if os.environ.get('WIZATA_CLIENT_ID') is None:
        raise ValueError('please configure OS variables to authenticate with api() method')

    if os.environ.get('WIZATA_PROTOCOL') is not None:
        protocol = os.environ.get('WIZATA_PROTOCOL')

    if os.environ.get('WIZATA_CLIENT_SECRET') is not None:
        scope = os.environ.get('WIZATA_SCOPE')
        if scope is None:
            scope = os.environ.get('WIZATA_CLIENT_ID') + '/.default'
        return WizataDSAPIClient(
            tenant_id=os.environ.get('WIZATA_TENANT_ID'),
            client_id=os.environ.get('WIZATA_CLIENT_ID'),
            client_secret=os.environ.get('WIZATA_CLIENT_SECRET'),
            scope=scope,
            domain=os.environ.get('WIZATA_DOMAIN'),
            protocol=protocol
        )
    else:
        return WizataDSAPIClient(
            tenant_id=os.environ.get('WIZATA_TENANT_ID'),
            client_id=os.environ.get('WIZATA_CLIENT_ID'),
            scope=os.environ.get('WIZATA_SCOPE'),
            username=os.environ.get('WIZATA_USERNAME'),
            password=os.environ.get('WIZATA_PASSWORD'),
            domain=os.environ.get('WIZATA_DOMAIN'),
            protocol=protocol
        )


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
