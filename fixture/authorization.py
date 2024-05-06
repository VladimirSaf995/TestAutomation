import requests

class Authorization:
    def __init__(self, base_url, xnodeid, api_base_url, sso_url):
        """Initialize Authorization class with base URL, xNode ID, API base URL, and SSO URL."""
        self.base_url = base_url
        self.xnodeid = xnodeid
        self.api_base_url = api_base_url
        self.sso_url = sso_url

    def _normalize_base_url(self, url):
        """Normalize base URL by removing "https://" and trailing slashes."""
        if url.startswith("https://"):
            url = url[8:]  # Remove "https://"

        if url.endswith("/"):
            url = url[:-1]  # Remove last slash "/"

        return url

    def get_api_token(self, login, password):
        """ Get API token using login credentials."""

        base_url = self._normalize_base_url(self.base_url)

        headers = {
            'accept': 'application/json',
            'x-Node-Id': self.xnodeid,
            'accept-version': '5',
            'Content-Type': 'application/json'
        }

        data = {
            "captchaToken": "string",
            "domain": base_url,
            "login": login,
            "timezoneId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "password": password,
            "playersDeviceInfo": {
                "userAgent": "string",
                "language": "string",
            }
        }

        try:
            response = requests.post(self.sso_url, json=data, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_json = response.json()
            token = response_json.get('token', '')
            return token
        except requests.exceptions.RequestException as e:
            print('Failed to get token:', e)
            return None

    def get_matrix_token(self, api_token):
        """ Get matrix token using API token."""

        headers = {
            'x-Node-Id': self.xnodeid,
            'Content-Type': 'application/json',
        }

        data = {"token": api_token}

        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/synapse/auth?token={api_token}&nodeId={self.xnodeid}",
                json=data,
                headers=headers
            )
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_json = response.json()
            access_token = response_json.get('accessToken')
            user_id = response_json.get('userId')
            user_id = user_id.replace('@', '').split(':')[0]
            return access_token, user_id
        except requests.exceptions.RequestException as e:
            print(f"Error in request: {e}")
            return None, None

    def get_rooms_id(self):
        """Get rooms ID from API."""

        try:
            response = requests.get(f"{self.api_base_url}/api/v1/correspondence/rooms/{self.xnodeid}")
            response.raise_for_status()  # Raise an exception for HTTP errors

            response_json = response.json()
            matrix_uids = [(item['matrixUid'].split(':')[0], item['matrixUid'].split(':')[1]) for item in
                           response_json[:2]]

            if len(matrix_uids) >= 2:
                roomA, room_second_part = matrix_uids[0]
                roomB = matrix_uids[1][0]
                return roomA, room_second_part, roomB
        except requests.exceptions.RequestException as e:
            print(f"Error in request: {e}")
        return None, None, None