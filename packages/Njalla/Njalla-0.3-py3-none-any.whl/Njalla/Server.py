import requests
from .API import NjallaAPI

class NjallaServer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://njal.la/api/1/"

        # will be added later on