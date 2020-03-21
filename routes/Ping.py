import falcon

class Ping:
    def on_get(self, req, resp):
        resp.status = resp.status = falcon.HTTP_200
        resp.body = 'Im still breathing :-)'