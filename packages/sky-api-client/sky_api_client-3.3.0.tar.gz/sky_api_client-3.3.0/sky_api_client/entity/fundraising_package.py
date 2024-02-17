from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('fundraising_package')
class FundraisingPackage(Entity):
    LIST_URL = '/fundraising/v1/packages/'
    GET_URL = '/fundraising/v1/packages/{id}'
