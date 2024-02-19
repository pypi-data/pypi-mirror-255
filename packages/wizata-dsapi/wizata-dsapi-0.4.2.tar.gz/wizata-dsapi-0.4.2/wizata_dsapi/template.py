import uuid
import json

import wizata_dsapi

from .api_dto import ApiDto
from .pipeline import VarType


class TemplateProperty(ApiDto):

    def __init__(self,
                 template_property_id: uuid.UUID = None,
                 name: str = None,
                 description: str = None,
                 p_type: VarType = None,
                 required: bool = True,
                 template_id: uuid.UUID = None):
        if template_property_id is None:
            self.template_property_id = uuid.uuid4()
        else:
            self.template_property_id = template_property_id
        self.description = description
        self.template_id = template_id
        self.name = name
        self.p_type = p_type
        self.required = required
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    def api_id(self) -> str:
        """
        Id of the Template Property (template_property_id)

        :return: string formatted UUID of the template property.
        """
        return str(self.template_property_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate template properties.
        :return: Endpoint name.
        """
        return "TemplateProperties"

    def from_json(self, obj):
        if "id" in obj.keys():
            self.template_property_id = uuid.UUID(obj["id"])
        if "name" in obj.keys():
            self.name = obj["name"]
        if "type" in obj.keys() and obj["type"] is not None:
            self.p_type = VarType(obj["type"])
        if "required" in obj.keys() and obj["required"] is not None:
            if not isinstance(obj["required"], bool):
                raise TypeError(f'template property field "required" should be a valid boolean')
            self.required = obj["required"]
        else:
            self.required = True
        if "description" in obj.keys():
            self.description = obj["description"]
        if "templateId" in obj.keys():
            self.template_id = uuid.UUID(obj["templateId"])
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
        Convert the template to a dictionary compatible to JSON format.

        :return: dictionary representation of the Template object.
        """
        obj = {
            "id": str(self.template_property_id)
        }
        if self.name is not None:
            obj["name"] = str(self.name)
        if self.description is not None:
            obj["description"] = str(self.description)
        if self.p_type is not None:
            obj["type"] = str(self.p_type.value)
        if self.required is not None:
            if not isinstance(self.required, bool):
                raise TypeError(f'template property field "required" should be a valid boolean')
            obj["required"] = self.required
        if self.template_id is not None:
            obj["templateId"] = str(self.template_id)
        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)
        return obj


class Template(ApiDto):
    """
    Template of a solution and/or asset.

    :ivar template_id: UUID of the Template.
    :ivar key: str unique id identifying the Template.
    :ivar name: logical display name of the Template.
    :ivar properties: list of Property { type , name } of the solution.

    Properties only support type 'datapoint', 'float', 'integer', 'json', 'datetime', 'relative' or 'string'
    """

    def __init__(self, template_id=None, key=None, name=None, properties=None):
        if template_id is None:
            self.template_id = uuid.uuid4()
        else:
            self.template_id = template_id
        self.key = key
        self.name = name
        if properties is None:
            properties = []
        self.properties = properties
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    def api_id(self) -> str:
        """
        Id of the Template (template_id)

        :return: string formatted UUID of the template.
        """
        return str(self.template_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate templates.
        :return: Endpoint name.
        """
        return "Templates"

    def from_json(self, obj):
        """
        Load the Template entity from a dictionary.

        :param obj: Dict version of the Template.
        """
        if "id" in obj.keys():
            self.template_id = uuid.UUID(obj["id"])
        if "key" in obj.keys() and obj["key"] is not None:
            self.key = obj["key"]
        if "name" in obj.keys() and obj["name"] is not None:
            self.name = obj["name"]
        if "properties" in obj.keys() and obj["properties"] is not None:
            if isinstance(obj["properties"], str):
                properties = json.loads(obj["properties"])
            else:
                properties = obj["properties"]
            # add properties to add method to ensure unicity of name and validity of type
            for to_add in properties:
                self.add_property(to_add)
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
        Convert the template to a dictionary compatible to JSON format.

        :return: dictionary representation of the Template object.
        """
        obj = {
            "id": str(self.template_id)
        }
        if self.key is not None:
            obj["key"] = str(self.key)
        if self.name is not None:
            obj["name"] = str(self.name)
        if self.properties is not None:
            obj_properties = []
            template_property: TemplateProperty
            for template_property in self.properties:
                obj_properties.append(template_property.to_json())
            obj["properties"] = json.dumps(obj_properties)
        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)
        return obj

    def add(self, name: str, p_type: VarType, required: bool = True,
            template_property_id: uuid.UUID = None, description: str = None):
        """
        add a property from detailed information.
        """

        if self.properties is None:
            self.properties = []

        if name is None or p_type is None:
            raise ValueError('please set a name and a type for property')

        property_value = TemplateProperty(
            template_property_id=template_property_id,
            name=name,
            p_type=p_type,
            required=required,
            description=description
        )
        property_value.template_id = self.template_id

        existing_property: TemplateProperty
        for existing_property in self.properties:
            if existing_property.name == property_value.name:
                raise ValueError(f'property {property_value.name} already exists in template.')

        self.properties.append(property_value)

    def get_property(self, property_name) -> TemplateProperty:
        """
        get a property from its name.
        :param property_name: name of the property.
        """
        for t_property in self.properties:
            if t_property.name == property_name:
                return t_property

    def add_property(self, property_value):
        """
        add a property in list of properties
        by default - a property is required
        :param property_value: dict or TemplateProperty
        """
        if isinstance(property_value, dict):
            if "type" not in property_value:
                raise KeyError("property must have a type.")
            p_type = VarType(property_value['type'])

            if "name" not in property_value:
                raise KeyError("property must have a name")
            name = property_value["name"]

            template_property_id = None
            if "id" in property_value:
                if isinstance(property_value['id'], str):
                    template_property_id = uuid.UUID(property_value['id'])
                elif isinstance(property_value['id'], uuid.UUID):
                    template_property_id = property_value['id']
                else:
                    raise ValueError('id must be a valid str or UUID')

            required = True
            if "required" in property_value:
                required = property_value["required"]

            description = None
            if "description" in property_value:
                description = property_value["description"]

            self.add(template_property_id=template_property_id,
                     name=name,
                     p_type=p_type,
                     required=required,
                     description=description)
        elif isinstance(property_value, TemplateProperty):
            property_value.template_id = self.template_id

            for existing_property in self.properties:
                if existing_property.name == property_value.name:
                    raise ValueError(f'property {property_value.name} already exists in template.')

            self.properties.append(property_value)
        else:
            raise ValueError('property must be a dict or a TemplateProperty')

    def remove_property(self, name: str):
        """
        remove a property from the list based on its name
        :param name: property to remove
        """
        found_property = None

        existing_property: TemplateProperty
        for existing_property in self.properties:
            if existing_property.name == name:
                found_property = existing_property

        if self.properties is not None and found_property is not None:
            self.properties.remove(found_property)


