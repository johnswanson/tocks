import requests
import time

class Beeminder:
    def __init__(self, username=None, auth_token=None):
        self.auth_token = auth_token
        self.username = username
    def post_datapoint(self, goal, value=1, comment='', timestamp=None):
        timestamp = timestamp or int(time.time())
        payload = {
            'auth_token': self.auth_token,
            'timestamp': timestamp or int(time.time()),
            'value': value,
            'comment': comment
        }
        response = requests.post(
            'https://www.beeminder.com/api/v1/users/{}/goals/{}/datapoints.json'.format(
                self.username,
                goal,
            ),
            data=payload)
        return response
