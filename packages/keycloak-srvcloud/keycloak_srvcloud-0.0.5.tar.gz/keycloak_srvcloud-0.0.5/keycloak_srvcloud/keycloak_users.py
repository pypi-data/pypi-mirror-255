'''Модуль обработки токенов'''
import requests
import exeptions

class KeycloackUsers():
    '''Класс для обработки токенов'''
    client_name = ""
    client_secret = ""
    admin_url = ""

    def get_all_users(self, access_token: str):
        """
        Получение всех пользователей
        Args:
            access_token (str): токен администратора

        Returns:
            List[Dict[str, Any]]: Список пользователей
        """
        headers = {
            "Accept": "application/json",
            "Authorization": f"bearer {access_token}"
        }
        response = requests.get(
            f'{self.admin_url}/users',
            headers=headers, timeout=3)
        exeptions.check_status_code(response.status_code)
        users = response.json()
        return users
