import json


class GeneralError(Exception):
    def __init__(self, text: str) -> None:
        try:
            json.loads(self.text)
            super().__init__(text)
        except json.JSONDecodeError as exc:
            super().__init__(
                [{'error_code': 500, 'error_name': 'JSONDecodeError', 'message': text, 'raw_message': exc.msg}]
            )


class MethodNotDefined(Exception):
    def __init__(self, method: str) -> None:
        self.method = method
        super().__init__('{} method is not available for this entity'.format(self.method))


class InvalidArguments(Exception):
    def __init__(self) -> None:
        super().__init__('Invalid Arguments')
