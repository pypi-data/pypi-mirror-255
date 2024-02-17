from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('gender')
class Gender(Entity):
    LIST_URL = '/constituent/v1/genders/'
