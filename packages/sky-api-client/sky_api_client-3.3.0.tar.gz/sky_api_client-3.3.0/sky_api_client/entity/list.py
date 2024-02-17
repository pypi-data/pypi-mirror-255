from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('list')
class List(Entity):
    LIST_URL = '/list/v1/lists'
