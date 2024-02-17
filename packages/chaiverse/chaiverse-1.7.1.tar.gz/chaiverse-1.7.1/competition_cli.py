from chaiverse.http_client import SubmitterClient
from chaiverse.login_cli import auto_authenticate
from chaiverse.schemas import Competition
from chaiverse import config


@auto_authenticate
def get_competitions(developer_key):
    submitter_client = SubmitterClient(developer_key=developer_key)
    competitions = submitter_client.get(config.COMPETITIONS_ENDPOINT)
    competitions = [Competition(**competition) for competition in competitions]
    return competitions
