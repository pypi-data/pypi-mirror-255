from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('gift')
class Gift(Entity):
    LIST_URL = '/gift/v1/gifts'
    CREATE_URL = '/gift/v1/gifts'
    GET_URL = '/gift/v1/gifts/{id}'
    UPDATE_URL = '/gift/v1/gifts/{id}/'
    DELETE_URL = '/gift/v1/gifts/{id}/'
