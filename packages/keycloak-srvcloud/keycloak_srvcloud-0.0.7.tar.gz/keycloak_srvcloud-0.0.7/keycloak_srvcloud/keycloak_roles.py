'''Модуль обработки ролей'''
import json

import requests
import keycloak_srvcloud.exeptions as exeptions

class KeycloackRole():
    '''Класс для работы с ролями'''
    client_name = ""
    client_secret = ""
    admin_url = ""
    client_id = ""

    def get_roles(self, access_token: str) -> list or Exception:
        """
        Получение ролей
        Args:
            id_client (str): id клиента
            access_token (str): токен администратора

        Returns:
            list or Exception: _description_
        """
        url = f"{self.admin_url}/clients/{self.client_id}/roles"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        exeptions.check_status_code(response.status_code)
        return response.json()

    def assign_role_to_user(self, user_id: str, role: dict, access_token: str):
        """
        Добавление роли пользователю
        Args:
            user_id (str): user id
            role (dict): роль
            id_client (str): ид клиента
            access_token (str): токен администратора
        """

        url = f"{self.admin_url}/users/{user_id}/role-mappings/clients/{self.client_id}"
        headers = {
            "Accept": "application/json",
            'Content-Type': 'application/json',
            "Authorization": f"bearer {access_token}"
        }
        data = json.dumps([role])
        response = requests.post(url, headers=headers, data=data)
        exeptions.check_status_code(response.status_code)
