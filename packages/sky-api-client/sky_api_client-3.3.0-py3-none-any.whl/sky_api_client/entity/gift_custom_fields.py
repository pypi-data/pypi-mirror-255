from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('gift_custom_fields')
class GiftCustomFields(Entity):
    LIST_URL = '/gift/v1/gifts/customfields/categories'
