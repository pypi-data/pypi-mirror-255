import uuid
from .api_dto import ApiDto
from enum import Enum
import json


class SolutionType(Enum):
    GRAFANA = "Grafana"
    DASHBOARD = "Dashboard"
    IFRAME = "Iframe"


class SolutionComponent(ApiDto):
    """
    A solution components handle an element giving to end-users to interact with solution.
    :ivar label_id: Business Label identification to set the menu and category.
    :ivar dashboard_id: Used only for type DASHBOARD as link to the dashboard.
    """

    def __init__(self,
                 solution_component_id=None,
                 label_id=None,
                 name=None,
                 solution_type=None,
                 content=None,
                 order=None,
                 dashboard_id=None,
                 twin_id=None,
                 template_id=None,
                 owner_id=None):
        if solution_component_id is None:
            self.solution_component_id = uuid.uuid4()
        else:
            self.solution_component_id = solution_component_id

        self.label_id = label_id
        self.name = name

        self.order = order
        if self.order is not None and not isinstance(self.order, int):
            raise TypeError(f'order must be None or a valid integer')

        self.solution_type = solution_type
        if self.solution_type is not None and not isinstance(self.solution_type, SolutionType):
            raise TypeError(f'solution type must be None or a valid SolutionType')

        self.content = content
        self.dashboard_id = dashboard_id

        self.owner_id = owner_id

        self.twin_id = twin_id
        self.template_id = template_id

        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    def api_id(self) -> str:
        return str(self.solution_component_id).upper()

    def endpoint(self) -> str:
        return "Components"

    def to_json(self, target: str = None):
        if self.label_id is None:
            raise ValueError("label ID is required when creating/updating a component.")
        if self.name is None:
            raise ValueError("name is required when creating/updating a component.")
        if self.solution_type is None or not isinstance(self.solution_type, SolutionType):
            raise ValueError("solution type must be a valid solution type.")
        obj = {
            "id": str(self.solution_component_id),
            "labelId": str(self.label_id),
            "name": self.name,
            "type": self.solution_type.value
        }

        if self.order is not None:
            if not isinstance(self.order, int):
                raise ValueError('order must be None or a valid integer.')
            obj["order"] = self.order

        if self.content is not None:
            obj["content"] = self.content
        if self.solution_type == SolutionType.DASHBOARD:
            if self.dashboard_id is None or not isinstance(self.dashboard_id, uuid.UUID):
                raise ValueError("dashboard Id of type UUID must be on component type dashboard")
            obj["dashboardId"] = self.dashboard_id

        if self.owner_id is not None:
            obj["ownerId"] = str(self.owner_id)
        if self.twin_id is not None:
            obj["twinId"] = str(self.twin_id)
        if self.template_id is not None:
            obj["templateId"] = str(self.template_id)

        return obj

    def from_json(self, obj):
        if "id" in obj.keys():
            self.solution_component_id = uuid.UUID(obj["id"])
        if "labelId" in obj.keys() and obj["labelId"] is not None:
            self.label_id = uuid.UUID(obj["labelId"])
        if "name" in obj.keys() and obj["name"] is not None:
            self.name = obj["name"]
        if "ownerId" in obj.keys() and obj["ownerId"] is not None:
            self.owner_id = uuid.UUID(obj["ownerId"])
        if "order" in obj.keys() and obj["order"] is not None:
            self.order = int(obj["order"])
        if "content" in obj.keys() and obj["content"] is not None:
            self.content = obj["content"]
        if "type" in obj.keys():
            self.solution_type = SolutionType(str(obj["type"]))
        if "twinId" in obj.keys() and obj["twinId"] is not None:
            self.twin_id = uuid.UUID(obj["twinId"])
        if "dashboardId" in obj.keys() and obj["dashboardId"] is not None:
            self.dashboard_id = uuid.UUID(obj["dashboardId"])
        if "templateId" in obj.keys() and obj["templateId"] is not None:
            self.template_id = uuid.UUID(obj["templateId"])
        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]
