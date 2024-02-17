from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('fundraising_campaign')
class FundraisingCampaign(Entity):
    LIST_URL = '/fundraising/v1/campaigns/'
    GET_URL = '/fundraising/v1/campaigns/{id}'
