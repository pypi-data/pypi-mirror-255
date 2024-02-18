
import requests

class Client:
    """A class for interacting with Zoom API."""
    def __init__(self, zoom_account_id="", zoom_client_id="", zoom_client_secret="", topic="Sample topic", date="", time=""):
        """Initialize the Client object.

        Args:
            zoom_account_id (str): The Zoom account ID.
            zoom_client_id (str): The Zoom client ID.
            zoom_client_secret (str): The Zoom client secret.
            topic (str): The topic of the Zoom meeting.
            date (str): The date of the Zoom meeting.
            time (str): The time of the Zoom meeting.
        """
        self.zoom_account_id = zoom_account_id
        self.zoom_client_id = zoom_client_id
        self.zoom_client_secret = zoom_client_secret
        self.topic = topic
        self.date = date
        self.time = time
        self._access_token = None


    def set_account_id(self, account_id):
        """sets the given id to the client account ID"""
        self.zoom_account_id = account_id
    
    def set_client_id(self, client_id):
        """sets the given id to the packages client id"""
        self.zoom_client_id = str(client_id)

    def set_client_secret(self, client_secret):
        """sets the given string to the packages client secret"""
        self.zoom_client_secret = str(client_secret)

    def set_topic(self, topic):
        """sets topic for the meeting"""
        if not self._access_token:
            raise Exception("please authenticate first")
        self.topic = topic

    def set_date(self, date):
        """sets date of the meeting"""
        if not self._access_token:
            raise Exception("please authenticate first")
        self.date = date

    def set_time(self, time):
        """sets time of the meeting"""
        if not self._access_token:
            raise Exception("please authenticate first")
        self.time = time

    def authenticate(self):
        """Authenticate the client instance"""
        if self.zoom_account_id is None or self.zoom_client_id is None or self.zoom_client_secret is None:
            raise ValueError("make sure you provide all credentials")
        
        if self.date is None or self.time is None:
            raise ValueError("Please provide date and time")
        
        try:
            auth_token_url = "https://zoom.us/oauth/token"
            api_base_url = "https://api.zoom.us/v2"

            data = {
                "grant_type": "account_credentials",
                "account_id": self.zoom_account_id,
                "client_secret": self.zoom_client_secret,
            }

            response = requests.post(auth_token_url, 
                                     auth=(self.zoom_client_id, 
                                           self.zoom_client_secret),
                                    data=data)
            if response.status_code!=200:
                raise Exception("Unable to get access token")
            response_data = response.json()
            self._access_token = response_data["access_token"]
            return True
        except Exception as e:
            raise Exception(f'{e}')
        
    
    def get_link(self):
        """Generates zoom link with additional informations"""
        if not self._access_token:
            raise Exception("please authenticate first")
        api_base_url = "https://api.zoom.us/v2"

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "topic": f'{self.topic}',
            "duration": '45',
            'start_time': f'{self.date}T10: {self.time}',
            "type": 2
        }

        resp = requests.post(f"{api_base_url}/users/me/meetings",
                             headers=headers,
                             json=payload)
        
        if resp.status_code != 201:
            raise Exception("Unable to generate meeting link")
        response_data = resp.json()

        content = {
            "meeting_url": response_data["join_url"],
            "password": response_data["password"],
            "meetingTime": response_data["start_time"],
            "purpose": response_data["topic"],
            "duration": response_data["duration"],
            "message": "Success",
            "status": 1
        }

        return content
    