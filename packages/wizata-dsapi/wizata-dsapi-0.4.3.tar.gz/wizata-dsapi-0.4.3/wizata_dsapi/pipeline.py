import uuid
import json

from .api_dto import ApiDto
from .script import ScriptConfig, Script
from .request import Request
from .mlmodel import MLModelConfig

from enum import Enum


class VarType(Enum):
    STRING = "string"
    INTEGER = "integer"
    DATETIME = "datetime"
    RELATIVE = "relative"
    DATAPOINT = "datapoint"
    FLOAT = "float"
    JSON = "json"


class StepType(Enum):
    QUERY = 'query'
    SCRIPT = 'script'
    MODEL = 'model'
    WRITE = 'write'
    PLOT = 'plot'
    DF_SAVE = 'df_save'


class WriteConfig:

    def __init__(self, config_id = None, datapoints: dict = None, map_property_name: str = None):
        if config_id is None:
            config_id = uuid.uuid4()
        self.config_id = config_id
        self.datapoints = datapoints
        self.map_property_name = map_property_name

    def from_json(self, obj):
        if "id" in obj:
            self.config_id = obj["id"]
        if "datapoints" in obj:
            self.datapoints = obj["datapoints"]
        if "map_property_name" in obj and obj["map_property_name"] is not None:
            self.map_property_name = str(obj["map_property_name"])

    def to_json(self):
        obj = {
            "id": str(self.config_id)
        }
        if self.datapoints is not None:
            obj["datapoints"] = self.datapoints
        if self.map_property_name is not None:
            obj["map_property_name"] = self.map_property_name
        return obj


class PipelineStep(ApiDto):
    """
    Step of a pipeline.
    """

    def __init__(self,
                 step_id: uuid.UUID = None,
                 step_type: StepType = None,
                 config=None,
                 inputs=None,
                 outputs=None):

        if outputs is None:
            outputs = []
        if inputs is None:
            inputs = []
        if step_id is None:
            step_id = uuid.uuid4()
        self.step_id = step_id
        self.step_type = step_type
        self.config = config
        self.inputs = inputs
        self.outputs = outputs

    def from_json(self, obj):
        """
        load from JSON dictionary representation
        """
        if "id" in obj.keys():
            self.step_id = uuid.UUID(obj["id"])

        if "type" in obj.keys():
            self.step_type = StepType(obj["type"])
        else:
            raise TypeError(f'pipeline step must have a type.')
        if "config" in obj.keys():
            if self.step_type == StepType.SCRIPT:
                self.config = ScriptConfig()
                self.config.from_json(obj['config'])
            elif self.step_type == StepType.QUERY:
                self.config = Request()
                self.config.from_json(obj['config'])
            elif self.step_type == StepType.WRITE:
                self.config = WriteConfig()
                self.config.from_json(obj['config'])
            elif self.step_type == StepType.MODEL:
                self.config = MLModelConfig()
                self.config.from_json(obj['config'])
            else:
                self.config = obj['config']
        self.inputs = []
        if "inputs" in obj.keys():
            for step_input in obj["inputs"]:
                if isinstance(step_input, dict):
                    self.inputs.append(step_input)
                else:
                    raise TypeError(f'unsupported input type {step_input.__class__.__name__}')

        self.outputs = []
        if "outputs" in obj.keys():
            for step_output in obj["outputs"]:
                if isinstance(step_output, dict):
                    self.outputs.append(step_output)
                else:
                    raise TypeError(f'unsupported output type {step_output.__class__.__name__}')

    def to_json(self, target: str = None):
        obj = {
            "id": str(self.step_id)
        }
        if self.step_type is not None:
            obj["type"] = str(self.step_type.value)
        if self.config is not None:
            if self.step_type == StepType.SCRIPT:
                obj["config"] = self.config.to_json()
            elif self.step_type == StepType.QUERY:
                obj["config"] = self.config.to_json()
            elif self.step_type == StepType.WRITE:
                obj["config"] = self.config.to_json()
            elif self.step_type == StepType.MODEL:
                obj["config"] = self.config.to_json()
            else:
                obj["config"] = self.config
        if self.inputs is not None:
            obj["inputs"] = self.inputs
        if self.outputs is not None:
            obj["outputs"] = self.outputs
        return obj

    def inputs_names(self, f_type: str = None) -> list:
        """
        get a list str representing inputs names
        :param f_type: filter on a type
        :return: list str
        """
        names = []
        for d_key in self.inputs:
            if not isinstance(d_key, dict):
                raise TypeError(f'unsupported output type {d_key} expected dataframe or model')
            if "dataframe" in d_key.keys() and (f_type is None or f_type == 'dataframe'):
                names.append(d_key["dataframe"])
            elif "model" in d_key.keys() and (f_type is None or f_type == 'model'):
                names.append(d_key["model"])
            elif f_type is None:
                raise TypeError(f'unsupported input type {d_key} expected dataframe or model')
        return names

    def outputs_names(self, f_type: str = None) -> list:
        """
        get a list str representing outputs names
        :param f_type: filter on a type
        :return: list str
        """
        names = []
        for d_key in self.outputs:
            if not isinstance(d_key, dict):
                raise TypeError(f'unsupported output type {d_key} expected dataframe or model')
            elif "dataframe" in d_key.keys() and (f_type is None or f_type == 'dataframe'):
                names.append(d_key["dataframe"])
            elif "model" in d_key.keys() and (f_type is None or f_type == 'model'):
                names.append(d_key["model"])
            elif f_type is None:
                raise TypeError(f'unsupported output type {d_key} expected dataframe or model')
        return names

    def get_input(self, name: str) -> dict:
        """
        get input dict based on value name.
        :param name: value name to find.
        :return: input dict
        """
        for d_input in self.inputs:
            if name in d_input.values():
                return d_input

    def get_output(self, name: str) -> dict:
        """
        get output dict based on value name.
        :param name: value name to find.
        :return: input dict
        """
        for d_output in self.outputs:
            if name in d_output.values():
                return d_output


class Pipeline(ApiDto):

    def __init__(self,
                 pipeline_id: uuid.UUID = None,
                 key: str = None,
                 variables: dict = None,
                 steps: list = None,
                 plots: list = None,
                 template_id: uuid.UUID = None,
                 experiment_id: uuid.UUID = None):

        if pipeline_id is None:
            pipeline_id = uuid.uuid4()
        self.pipeline_id = pipeline_id
        self.key = key
        if variables is None:
            variables = {}
        self.variables = variables
        self.template_id = template_id
        self.experiment_id = experiment_id
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None
        self.plots = plots
        if plots is None:
            self.plots = []
        if steps is not None:
            for step in steps:
                if not isinstance(step, PipelineStep):
                    raise TypeError(f'step expected PipelineStep but received {step.__class__.__name__}')
            self.steps = steps
        else:
            self.steps = []

    def check_path(self) -> bool:
        """
        validate that steps create a valid path.
        return true if path is valid, otherwise raise errors
        """

        followed = []  # all steps already followed
        produced = []  # all outputs already produced

        steps_to_follow = self._next_steps(followed, produced)
        if len(steps_to_follow) == 0:
            raise ValueError('path does not contains any initial steps producing outputs')

        while len(steps_to_follow) > 0:
            for step in steps_to_follow:
                self._follow_step(step, followed, produced)
            steps_to_follow = []
            if len(followed) < len(self.steps):
                steps_to_follow = self._next_steps(followed, produced)

        if len(followed) == len(self.steps):
            return True
        else:
            raise RuntimeError(f'missing {len(self.steps)-len(followed)} step(s) that could not be followed')

    def _follow_step(self,
                     step: PipelineStep,
                     followed: list,
                     produced: list):
        """
        simulate that step have been followed.
        """
        if step in followed:
            raise RuntimeError(f'path cannot pass two times through same step {step.step_id}')
        followed.append(step)
        if step.step_type == StepType.QUERY and len(step.outputs) != 1:
            raise RuntimeError(f'query step must have exactly one output and be of type dataframe')
        if step.step_type == StepType.WRITE and (len(step.inputs) != 1 or len(step.outputs) > 0):
            raise RuntimeError(f'write step must have exactly one input and no outputs')
        for output in step.outputs_names():
            if output in produced:
                raise RuntimeError(f'output {output} is already produced.')
            produced.append(output)

    def _next_steps(self, followed, produced):
        """
        find all next steps that are ready to be executed
        """
        next_steps = []
        step: PipelineStep
        for step in self.steps:
            if all(s_input in produced for s_input in step.inputs_names()) and step not in followed:
                next_steps.append(step)
        return next_steps

    def add_query(self, request: Request, df_name: str, use_template: bool = True):
        """
        add a query step
        :param request: request definition to add.
        :param df_name: output name ot use for the dataframe.
        :param use_template: by default, if pipeline is link to a template, the query will be too. set to false to disable forcing it.
        """
        if request is None:
            raise ValueError('please provide a request.')
        if df_name is None:
            raise ValueError('please name the output')
        if use_template and self.template_id is not None:
            request.select_template(template_id=self.template_id)
        step = PipelineStep()
        step.step_type = StepType.QUERY
        step.config = request
        step.outputs.append({'dataframe': df_name})
        self.steps.append(step)

    def add_transformation(self, script, input_df_names: list, output_df_names: list):
        """
        add a transformation script
        :param script: name, Script or ScriptConfig.
        :param input_df_names: list of str for dataframe input.
        :param output_df_names: list of str for dataframe output.
        """
        if script is None:
            raise ValueError('please provide a script.')

        step = PipelineStep()
        step.step_type = StepType.SCRIPT
        if isinstance(script, str):
            step.config = ScriptConfig(function=script)
        elif isinstance(script, ScriptConfig):
            step.config = script
        elif isinstance(script, Script):
            name = script.name
            if name is None:
                raise ValueError('please fetch your script or set a function name directly')
            step.config = ScriptConfig(function=name)
        else:
            raise TypeError(f'unsupported type of script {script.__class__.__name__}')
        for input_df_name in input_df_names:
            if not isinstance(input_df_name, str):
                raise TypeError(f'unsupported type of input df name {input_df_name.__class__.__name__}')
            step.inputs.append({'dataframe': input_df_name})
        for output_df_name in output_df_names:
            if not isinstance(output_df_name, str):
                raise TypeError(f'unsupported type of input df name {output_df_name.__class__.__name__}')
            step.outputs.append({'dataframe': output_df_name})
        self.steps.append(step)

    def add_model(self, config:MLModelConfig, input_df: str, output_df: str = None):

        if config is None:
            raise ValueError('please provide a config.')
        if input_df is None:
            raise ValueError('please provide a input_df name.')

        step = PipelineStep()
        step.step_type = StepType.MODEL
        step.inputs.append({'dataframe': input_df})
        if output_df is not None:
            step.outputs.append({'dataframe': output_df})
        step.config = config
        self.steps.append(step)

    def add_writer(self, config: WriteConfig, input_df: str):

        if config is None:
            raise ValueError('please provide a config.')
        if input_df is None:
            raise ValueError('please provide a input_df name.')

        step = PipelineStep()
        step.step_type = StepType.WRITE
        step.inputs.append({'dataframe': input_df})
        step.config = config
        self.steps.append(step)

    def add_plot(self, script, df_name: str):
        """
        add a plot to the pipeline.
        :param script: name, Script or ScriptConfig.
        :param df_name: name of the dataframe to plot.
        """

        if script is None:
            raise ValueError('please provide a script.')

        if isinstance(script, ScriptConfig):
            script_name = ScriptConfig(function=script)
        elif isinstance(script, str):
            script_name = script
        elif isinstance(script, Script):
            script_name = script.name
            if script_name is None:
                raise ValueError('please fetch your script or set a function name directly')
        else:
            raise TypeError(f'unsupported type of script {script.__class__.__name__}')

        if df_name is None:
            raise ValueError(f'please provide a dataframe name')

        self.plots.append({'dataframe': df_name, 'script': script_name})

    def check_variables(self):
        """
        verify that variables dict is a valid { "name" : "VarType" } dictionary.
        """
        if self.variables is None:
            self.variables = {}
        elif not isinstance(self.variables, dict):
            raise TypeError(f'variables must be empty nor a valid dictionary')
        for key in self.variables:
            # check if valid type (trigger an error if not)
            VarType(self.variables[key])

    def api_id(self) -> str:
        """
        Id of the pipeline

        :return: string formatted UUID of the Pipeline.
        """
        return str(self.pipeline_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate pipeline.
        :return: Endpoint name.
        """
        return "Pipelines"

    def from_json(self, obj):
        """
        load from JSON dictionary representation
        """
        if "id" in obj.keys():
            self.pipeline_id = uuid.UUID(obj["id"])
        if "key" in obj.keys():
            self.key = str(obj['key'])
        if "id" not in obj.keys() and "key" not in obj.keys():
            raise KeyError("at least id or key must be set on a pipeline")
        if "templateId" in obj.keys() and obj["templateId"] is not None:
            self.template_id = uuid.UUID(obj["templateId"])
        if "experimentKey" in obj.keys() and obj["experimentKey"] is not None:
            self.experiment_id = uuid.UUID(obj["experimentKey"])
        if "variables" in obj.keys():
            if isinstance(obj["variables"], str):
                self.variables = json.loads(obj["variables"])
            else:
                self.variables = obj["variables"]
            if self.variables is not None or not isinstance(self.variables, dict):
                if isinstance(self.variables, list) and len(self.variables) == 0:
                    self.variables = {}
            self.check_variables()
        if "steps" in obj.keys():
            if isinstance(obj["steps"], str):
                steps = json.loads(obj["steps"])
            else:
                steps = obj["steps"]
            for obj_step in steps:
                step = PipelineStep()
                step.from_json(obj_step)
                self.steps.append(step)
        if "plots" in obj.keys():
            if isinstance(obj["plots"], str):
                self.plots = json.loads(obj["plots"])
            else:
                self.plots = obj["plots"]
        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]

    def to_json(self, target: str = None):
        """
        Convert to a json version of Execution definition.
        By default, use DS API format.
        """
        obj = {
            "id": str(self.pipeline_id)
        }
        if self.key is not None:
            obj["key"] = self.key
        if self.steps is not None:
            obj_steps = []
            step: PipelineStep
            for step in self.steps:
                obj_steps.append(step.to_json())
            obj["steps"] = json.dumps(obj_steps)
        if self.plots is not None:
            obj["plots"] = json.dumps(self.plots)
        if self.variables is not None:
            self.check_variables()
            obj["variables"] = json.dumps(self.variables)
        if self.template_id is not None:
            obj["templateId"] = str(self.template_id)
        if self.experiment_id is not None:
            obj["experimentKey"] = str(self.experiment_id)
        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)
        return obj




