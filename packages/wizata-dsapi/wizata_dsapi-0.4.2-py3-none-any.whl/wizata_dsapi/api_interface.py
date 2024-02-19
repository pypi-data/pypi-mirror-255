import uuid
from .solution_component import SolutionComponent
from .paged_query_result import PagedQueryResult


class ApiInterface:
    """
    Interface with all methods available both to the pipeline runners and the Data Science API.
    """

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
        pass

    def create_component(self, component: SolutionComponent):
        """
        create a component based on its ID.
        """
        pass

    def update_component(self, component: SolutionComponent):
        """
        update a component based on its ID.
        """
        pass

    def delete_component(self, component_id: uuid.UUID):
        """
        delete component
        """
        pass

    def get_business_labels(self) -> dict:
        """
        get a name / uuid dictionary with all business labels in platform.
        """
        pass

    def get_datapoint_mappings(self, registration):
        """
        get datapoint mapping from a registration.
        """
        pass

    def get_registrations(self, template) -> list:
        """
        retrieve all registrations for
        :param template: template object, UUID or str key.
        :return: list of twin registration.
        """
        pass

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
        pass

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
        pass
