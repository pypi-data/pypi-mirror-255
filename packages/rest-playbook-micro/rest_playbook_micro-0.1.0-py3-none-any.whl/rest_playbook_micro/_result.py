import uuid
import time

def get_uuid_id():
    return str(uuid.uuid4())


class Result():

    status: int
    body: str
    outbound: str
    timestamp: float
    uuid: str

    def __init__(self, response: str = '', status: int = 0) -> None:
        self.uuid = get_uuid_id()
        self.timestamp = time.time()
        self.status = status
        self.body = response

    def __str__(self):
        return f"{self.status} - {self.body[:100]}"

    def __repr__(self):
        return f"{self.uuid} - {self.body[:100]}"
