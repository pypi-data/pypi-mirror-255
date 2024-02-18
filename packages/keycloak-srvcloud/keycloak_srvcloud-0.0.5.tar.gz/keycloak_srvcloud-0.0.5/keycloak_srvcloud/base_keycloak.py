import json
import requests
import keycloak_srvcloud.exeptions as exeptions
from keycloak_srvcloud.keycloak_roles import KeycloackRole
from keycloak_srvcloud.keycloak_tokens import KeycloackToken
from keycloak_srvcloud.keycloak_users import KeycloackUsers

class Keycloak(KeycloackRole, KeycloackToken, KeycloackUsers):
    '''Класс для работы с keycloak'''
    keycloak_host = ""
    keycloak_port = ""
    client_name = ""
    client_id = ""
    client_secret = ""
    admin_user = ""
    admin_password = ""
    api_url = ""
    admin_url = ""

    def __init__(self,
                 keycloak_host: str,
                 keycloak_port: str,
                 realm_name: str,
                 client_name: str,
                 client_id: str,
                 client_secret: str,
                 admin_user: str,
                 admin_password: str) -> None:
        """
        Инициализация класса
        Args:
            keycloak_host (str): ip keycloak
            keycloak_port (str): port keycloak
            realm_name (str): Название realm
            client_id (str): id клиента
            client_secret (str): secret клиента
            admin_user (str): username admin user
            admin_password (str): password admin user
        """
        self.keycloak_host = keycloak_host
        self.keycloak_port = keycloak_port
        self.realm_name = realm_name
        self.client_name = client_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.api_url = f"http://{keycloak_host}:{keycloak_port}/realms/{realm_name}/protocol/openid-connect"
        self.admin_url = f"http://{keycloak_host}:{keycloak_port}/admin/realms/{realm_name}"

    def login(self, username: str, password: str) -> dict:
        '''Авторизация в keycloak'''
        data = {
            'client_id': self.client_name,
            'client_secret': self.client_secret,
            'username': username,
            'password': password,
            'grant_type': "password"
        }
        response = requests.post(f'{self.api_url}/token', data=data, timeout=3)
        exeptions.check_status_code(response.status_code)
        return response.json()

    def logout(self, access_token: str, refresh_token: str) -> None:
        '''Завершает сессию'''
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'client_id': self.client_name,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token
        }
        response = requests.post(f'{self.api_url}/logout', data=data, headers=headers, timeout=3)
        exeptions.check_status_code(response.status_code)


    def userinfo(self, access_token: str) -> dict:
        '''Получение userinfo'''
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json'
        }
        response = requests.get(f'{self.api_url}/userinfo', headers=headers, timeout=3)
        exeptions.check_status_code(response.status_code)
        return response.json()


    def sign_up(self, access_token: str, username: str, password: str,
                first_name: str = "", last_name: str = "", email="") -> None or Exception:
        """
        Регистрация пользователя
        Args:
            access_token (str): токен админстраторв
            username (str): логин
            password (str): пароль
            first_name (str, optional): Имя. Defaults to "".
            last_name (str, optional): Фамилия. Defaults to "".

        Returns:
            None or Exception: При успешной регистрации ничего не возвращается
        """
        headers = {
            "Accept": "application/json",
            'Content-Type': 'application/json',
            "Authorization": f"bearer {access_token}"
        }
        data = json.dumps({
            "email": email,
            "emailVerified": False,
            "enabled": True,
            "firstName": first_name,
            "groups": [],
            "lastName": last_name,
            "requiredActions": [],
            "username": username,
            "credentials": [{"type": "password", "value": password, "temporary": False}]
        })
        response = requests.post(
            f'http://{self.keycloak_host}:{self.keycloak_port}/admin/realms/{self.realm_name}/users',
            data=data, headers=headers, timeout=3)
        exeptions.check_status_code(response.status_code)

