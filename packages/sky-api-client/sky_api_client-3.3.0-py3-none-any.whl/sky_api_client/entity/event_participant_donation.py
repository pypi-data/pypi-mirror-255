from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('event_participant_donation')
class EventParticipantFeePayment(Entity):
    LIST_URL = '/event/v1/participants/{id}/donations'
    CREATE_URL = '/event/v1/participants/{id}/donations'
    DELETE_URL = '/event/v1/participantdonations/{id}'
