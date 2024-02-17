from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('event_participant_levels')
class EventParticipantLevels(Entity):
    LIST_URL = '/event/v1/participationlevels'
