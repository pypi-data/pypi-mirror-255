import biolib.api

class BiolibAccountApi:

    @staticmethod
    def fetch_by_handle(account_handle):
        response = biolib.api.client.get(path=f'/account/{account_handle}')
        return response.json()
