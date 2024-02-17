class ConverterError(Exception):
    pass


class SigningInDisabledError(RuntimeError):
    def __init__(self, code_type: str):
        super().__init__("Session is not signed in")
        self.code_type = code_type
