from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('event_participant_fee')
class EventParticipantFee(Entity):
    LIST_URL = '/event/v1/participants/{id}/fees'
    CREATE_URL = '/event/v1/participants/{id}/fees'
    DELETE_URL = '/event/v1/participantfees/{id}'
