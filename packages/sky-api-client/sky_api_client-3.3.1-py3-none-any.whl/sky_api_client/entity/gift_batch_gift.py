from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('gift_batch_gift')
class GiftBatchGift(Entity):
    CREATE_URL = '/gift/v1/giftbatches/{id}/gifts'
