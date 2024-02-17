from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('fundraising_appeal')
class FundraisingAppeal(Entity):
    LIST_URL = '/fundraising/v1/appeals/'
    GET_URL = '/fundraising/v1/appeals/{id}'
