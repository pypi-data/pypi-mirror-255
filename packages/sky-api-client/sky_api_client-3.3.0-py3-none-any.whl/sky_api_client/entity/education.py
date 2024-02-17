from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry
from sky_api_client.exceptions.exception import MethodNotDefined


@EntityRegistry.register('education')
class Education(Entity):
    LIST_URL = '/constituent/v1/educations/'
    CREATE_URL = '/constituent/v1/educations/'
    GET_URL = '/constituent/v1/constituents/educations/{id}'
    UPDATE_URL = '/constituent/v1/educations/{id}'
    DELETE_URL = '/constituent/v1/educations/{id}'
    SUBJECTS_URL = '/constituent/v1/educations/subjects'
    DEGREES_URL = '/constituent/v1/educations/degrees'

    def subjects(self):
        if self.SUBJECTS_URL:
            return self._api.request(method='GET', path=self.SUBJECTS_URL).get('value', [])
        raise MethodNotDefined('subjects')

    def degrees(self):
        if self.DEGREES_URL:
            return self._api.request(method='GET', path=self.DEGREES_URL).get('value', [])
        raise MethodNotDefined('degrees')
