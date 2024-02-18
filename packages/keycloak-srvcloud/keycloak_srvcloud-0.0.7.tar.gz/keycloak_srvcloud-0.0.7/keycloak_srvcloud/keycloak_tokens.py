'''Модуль обработки токенов'''
import requests
import keycloak_srvcloud.exeptions as exeptions

class KeycloackToken():
    '''Класс для обработки токенов'''
    client_name = ""
    client_secret = ""
    api_url = ""

    def refresh_token(self, access_token: str, refresh_token: str) -> dict:
        '''Обновление токена'''
        data = {
            'client_id': self.client_name,
            'client_secret': self.client_secret,
            'accesss_token': access_token,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        response = requests.post(f'{self.api_url}/token', data=data, timeout=3)
        exeptions.check_status_code(response.status_code)
        return response.json()

    def revoke_token(self, access_token: str) -> None:
        '''Отозвать токен'''
        data = {
            'client_id': self.client_name,
            'client_secret': self.client_secret,
            'token': access_token,
            'token_type_hint': 'access_token'
        }
        response = requests.post(f'{self.api_url}/revoke', data=data, timeout=3)
        exeptions.check_status_code(response.status_code)

    def introspect_token(self, access_token: str) -> dict:
        '''Получение интроспекции токена'''
        data = {
            'client_id': self.client_name,
            'client_secret': self.client_secret,
            'token': access_token
        }
        response = requests.post(f'{self.api_url}/token/introspect', data=data, timeout=3)
        exeptions.check_status_code(response.status_code)
        return response.json()
