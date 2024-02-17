from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('gift_custom_field_values')
class GiftCustomFieldValues(Entity):
    LIST_URL = '/gift/v1/gifts/customfields/categories/values'
