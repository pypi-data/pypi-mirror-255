from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('gift_aid')
class GiftAid(Entity):
    LIST_URL = 'nxt-data-integration/v1/re/giftaid/constituents/{id}/taxdeclarations'
    CREATE_URL = 'nxt-data-integration/v1/re/giftaid/taxdeclarations'
    UPDATE_URL = 'nxt-data-integration/v1/re/giftaid/taxdeclarations/{id}'
