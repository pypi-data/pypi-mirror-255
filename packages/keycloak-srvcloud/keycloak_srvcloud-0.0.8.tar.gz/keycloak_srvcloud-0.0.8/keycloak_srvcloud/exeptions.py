"""Кастомные ошибки"""
class UserAlreadyExists(Exception):
    """Ошибка возникающая при попытке зарегестрировать с существующим username"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class Unauthorized(Exception):
    """Ошибка возникающая при status_code==401"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class PageNotFound(Exception):
    """Ошибка возникающая при некорректном url для keycloak"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class BadRequest(Exception):
    """Ошибка возникающая при некорректном данных"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def check_status_code(status_code):
    '''Проверка status code'''
    if status_code == 401:
        raise Unauthorized('Incorrect login/password')
    elif status_code == 404:
        raise PageNotFound('Incorrect API keyckloak')
    elif status_code == 400:
        raise BadRequest("Invalid credentionals")
    elif status_code == 409:
        raise UserAlreadyExists("User allredy exists")
    elif status_code == 403:
        raise Unauthorized('Method not allowed')
