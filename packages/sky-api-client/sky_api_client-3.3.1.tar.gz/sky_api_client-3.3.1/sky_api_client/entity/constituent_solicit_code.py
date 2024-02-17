from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('constituent_solicit_code')
class ConstituentSolicitCode(Entity):
    LIST_URL = '/commpref/v1/constituents/{id}/constituentsolicitcodes'
