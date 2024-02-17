from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry
from sky_api_client.exceptions.exception import MethodNotDefined


@EntityRegistry.register('solicit_code')
class SolicitCode(Entity):
    CREATE_URL = '/commpref/v1/constituentsolicitcodes'
    GET_URL = '/commpref/v1/constituentsolicitcodes/{id}'
    UPDATE_URL = '/commpref/v1/constituentsolicitcodes/{id}'
    DELETE_URL = '/commpref/v1/constituentsolicitcodes/{id}'
    TYPES_URL = '/commpref/v1/solicitcodes'

    def types(self):
        if self.TYPES_URL:
            results = self._api.request(method='GET', path=self.TYPES_URL).get('value', [])
            return [result['description'] for result in results]
        raise MethodNotDefined('Types')
