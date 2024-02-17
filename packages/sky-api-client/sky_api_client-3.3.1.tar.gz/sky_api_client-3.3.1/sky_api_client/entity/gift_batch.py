from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('gift_batch')
class GiftBatch(Entity):
    LIST_URL = '/gift-batch/v1/giftbatches'
    CREATE_URL = '/gift-batch/v1/giftbatches'
    DELETE_URL = '/gift-batch/v1/giftbatches/{id}'
