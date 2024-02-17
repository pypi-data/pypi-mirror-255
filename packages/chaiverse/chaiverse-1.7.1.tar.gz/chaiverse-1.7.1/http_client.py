import requests

from chaiverse.login_cli import auto_authenticate
from chaiverse.config import BASE_SUBMITTER_URL, BASE_FEEDBACK_URL
from chaiverse.utils import get_url


class _ChaiverseHTTPClient():
    def __init__(self, developer_key=None, hostname=None, debug_mode=False):
        self.developer_key = developer_key
        self.hostname = hostname
        self.debug_mode = debug_mode

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.developer_key}"}

    def get(self, endpoint, submission_id=None, **kwargs):
        url = get_url(endpoint, hostname=self.hostname, submission_id=submission_id)
        response = self._request(requests.get, url=url, **kwargs)
        return response

    def put(self, endpoint, data):
        url = get_url(endpoint, hostname=self.hostname)
        response = self._request(requests.post, url=url, json=data)
        return response

    def post(self, endpoint, data, submission_id=None, **kwargs):
        url = get_url(endpoint, hostname=self.hostname, submission_id=submission_id)
        response = self._request(requests.post, url=url, json=data, **kwargs)
        return response

    def delete(self, endpoint):
        url = get_url(endpoint, hostname=self.hostname)
        response = self._request(requests.post, url=url)
        return response

    def _request(self, func, url, **kwargs):
        response = func(url=url, headers=self.headers, **kwargs)
        if not self.debug_mode:
            assert response.status_code == 200, response.json()
            response = response.json()
        return response


@auto_authenticate
class SubmitterClient(_ChaiverseHTTPClient):
    def __init__(self,
            developer_key=None,
            hostname=None,
            debug_mode=False):
        hostname = BASE_SUBMITTER_URL if not hostname else hostname
        super().__init__(developer_key, hostname, debug_mode)


@auto_authenticate
class FeedbackClient(_ChaiverseHTTPClient):
    def __init__(self,
            developer_key=None,
            hostname=None,
            debug_mode=False):
        hostname = BASE_FEEDBACK_URL if not hostname else hostname
        super().__init__(developer_key, hostname, debug_mode)

