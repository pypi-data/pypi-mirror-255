from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('event_participant_fee_payment')
class EventParticipantFeePayment(Entity):
    LIST_URL = '/event/v1/participants/{id}/feepayments'
    CREATE_URL = '/event/v1/participants/{id}/feepayments'
    DELETE_URL = '/event/v1/participantfeepayments/{id}'
