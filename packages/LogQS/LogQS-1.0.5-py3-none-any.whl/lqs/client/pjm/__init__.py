from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lqs.client import RESTClient
from lqs.client.pjm.list import List
from lqs.client.pjm.fetch import Fetch
from lqs.client.pjm.create import Create
from lqs.client.pjm.update import Update
from lqs.client.pjm.delete import Delete


class ProcessJobManager:
    def __init__(self, app: "RESTClient"):
        self.app = app

        self.list = List(app=app)
        self.fetch = Fetch(app=app)
        self.create = Create(app=app)
        self.update = Update(app=app)
        self.delete = Delete(app=app)
