from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('gift_subtype')
class GiftSubtype(Entity):
    LIST_URL = '/gift/v1/giftsubtypes'
