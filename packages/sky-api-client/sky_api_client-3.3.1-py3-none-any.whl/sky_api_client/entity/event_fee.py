from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('event_fee')
class EventFee(Entity):
    LIST_URL = '/event/v1/events/{id}/eventfees'
    CREATE_URL = '/event/v1/events/{id}/eventfees'
    UPDATE_URL = '/event/v1/eventfees/{id}'
    DELETE_URL = '/event/v1/eventfees/{id}'
