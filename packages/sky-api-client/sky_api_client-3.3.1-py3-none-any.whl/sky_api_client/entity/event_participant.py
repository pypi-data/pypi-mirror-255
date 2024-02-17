from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('event_participant')
class EventParticipant(Entity):
    LIST_URL = '/event/v1/events/{id}/participants'
    CREATE_URL = '/event/v1/events/{id}/participants'
    GET_URL = '/event/v1/participants/{id}'
    UPDATE_URL = '/event/v1/participants/{id}'
    DELETE_URL = '/event/v1/participants/{id}'
