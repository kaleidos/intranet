# -*- coding: utf-8 -*-
import requests

class Session(requests.Session):

    def parse_response(self, response):
        status_code = response.status_code
        if status_code == 200:
            return response
        elif status_code in [403, 400]:
            raise requests.exceptions.HTTPError(response.json()['detail'])
        else:
            raise requests.exceptions.HTTPError('Not so unexpected error')
        return


    def get(self, url, **kwargs):
        response = super().get(url, **kwargs)
        return self.parse_response(response)


    def post(self, url, data=None, **kwargs):
        response = super().post(url, data, **kwargs)
        return self.parse_response(response)


    def patch(self, url, data=None, **kwargs):
        response = super().patch(url, data, **kwargs)
        return self.parse_response(response)
