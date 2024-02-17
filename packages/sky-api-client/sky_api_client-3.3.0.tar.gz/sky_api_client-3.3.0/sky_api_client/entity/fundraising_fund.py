from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('fundraising_fund')
class FundraisingFund(Entity):
    LIST_URL = '/fundraising/v1/funds/'
    GET_URL = '/fundraising/v1/funds/{id}'
