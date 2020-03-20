import falcon
from routes.Ping import Ping

api = falcon.API()
api.add_route('/ping', Ping())
