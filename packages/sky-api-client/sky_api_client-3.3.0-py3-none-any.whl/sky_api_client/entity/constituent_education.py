from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('constituent_education')
class ConstituentEducation(Entity):
    LIST_URL = '/constituent/v1/constituents/{id}/educations'
