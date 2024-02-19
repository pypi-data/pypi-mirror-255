import uuid
from .api_dto import ApiDto
from enum import Enum
import re


def is_valid_hex_color(color):
    hex_color_pattern = r'^#([A-Fa-f0-9]{6})$'
    match = re.match(hex_color_pattern, color)
    if match is None:
        raise ValueError('color is not a proper hexadecimal color : e.g. #E64600')
    else:
        return True


class TwinBlockType(Enum):
    AREA = "area"
    MACHINE = "machine"
    EQUIPMENT = "equipment"
    FLOW = "flow"


class Twin(ApiDto):
    """
    Digital Twin item/asset declared and managed on Wizata.

    :ivar twin_id: UUID of the Digital Twin.
    :ivar hardware_id: str hardware id identifying the Asset.
    :ivar name: logical display name of the Asset.
    :ivar type: type (area, machine, equipment or flow).
    """

    def __init__(self, twin_id=None, hardware_id=None, name=None, parent_id=None, ttype=TwinBlockType.MACHINE,
                 latitude_id: uuid.UUID = None, longitude_id: uuid.UUID = None, color: str = None, icon: str = None,
                 latitude: float = None, longitude: float = None):
        if twin_id is None:
            self.twin_id = uuid.uuid4()
        else:
            self.twin_id = twin_id
        self.hardware_id = hardware_id
        self.name = name
        self.parent_id = parent_id
        self.type = ttype
        self.latitude = latitude
        self.longitude = longitude
        self.latitude_id = latitude_id
        self.longitude_id = longitude_id
        if color is not None:
            is_valid_hex_color(color)
        self.color = color
        self.icon = icon
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    def api_id(self) -> str:
        """
        Id of the experiment (experiment_id)

        :return: string formatted UUID of the Experiment.
        """
        return str(self.twin_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate execution.
        :return: Endpoint name.
        """
        return "Twins"

    def from_json(self, obj):
        """
        Load the Twin entity from a dictionary.

        :param obj: Dict version of the Twin.
        """
        if "id" in obj.keys():
            self.twin_id = uuid.UUID(obj["id"])
        if "hardwareId" in obj.keys() and obj["hardwareId"] is not None:
            self.hardware_id = obj["hardwareId"]
        if "name" in obj.keys() and obj["name"] is not None:
            self.name = obj["name"]
        if "parentId" in obj.keys() and obj["parentId"] is not None:
            self.parent_id = uuid.UUID(obj["parentId"])
        if "latitude" in obj.keys() and obj["latitude"] is not None:
            self.latitude = float(obj["latitude"])
        if "longitude" in obj.keys() and obj["longitude"] is not None:
            self.longitude = float(obj["longitude"])
        if "latitudeSensorId" in obj.keys() and obj["latitudeSensorId"] is not None:
            self.latitude_id = uuid.UUID(obj["latitudeSensorId"])
        if "longitudeSensorId" in obj.keys() and obj["longitudeSensorId"] is not None:
            self.longitude_id = uuid.UUID(obj["longitudeSensorId"])
        if "color" in obj.keys() and obj["color"] is not None:
            is_valid_hex_color(str(obj["color"]))
            self.color = str(obj["color"])
        if "icon" in obj.keys() and obj["icon"] is not None:
            self.icon = str(obj["icon"])
        if "type" in obj.keys():
            self.type = TwinBlockType(str(obj["type"]))
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
        Convert the twin to a dictionary compatible to JSON format.

        :return: dictionary representation of the Twin object.
        """
        obj = {
            "id": str(self.twin_id)
        }
        if self.hardware_id is not None:
            obj["hardwareId"] = str(self.hardware_id)
        if self.name is not None:
            obj["name"] = str(self.name)
        if self.parent_id is not None:
            obj["parentId"] = str(self.parent_id)
        if self.type is not None and isinstance(self.type, TwinBlockType):
            obj["type"] = self.type.value
        if self.color is not None:
            obj["color"] = str(self.color)
        if self.latitude is not None:
            obj["latitude"] = str(self.latitude)
        if self.longitude is not None:
            obj["longitude"] = str(self.longitude)
        if self.latitude_id is not None:
            obj["latitudeSensorId"] = str(self.latitude_id)
        if self.longitude_id is not None:
            obj["longitudeSensorId"] = str(self.longitude_id)
        if self.icon is not None:
            obj["icon"] = str(self.icon)
        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)
        return obj
