"""Кастомные ошибки"""
class UserAlreadyExists:
    """Ошибка возникающая при попытке зарегестрировать с существующим username"""
    pass

class Unauthorized:
    """Ошибка возникающая при status_code==401"""
    pass

class PageNotFound:
    """Ошибка возникающая при некорректном url для keycloak"""
    pass

class BadRequest:
    """Ошибка возникающая при некорректном данных"""
    pass

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
