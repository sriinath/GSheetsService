import falcon

from processes.datastore import DataStore
from processes.redis import Redis

from middleware.Auth import AuthMiddleware

from routes.Ping import Ping
from routes.Sheets import Sheets
from routes.SheetValues import SheetValues
from routes.User import User
from routes.Auth import Auth

api = falcon.API(middleware=[AuthMiddleware()])

api.add_route('/ping', Ping())
api.add_route('/api/sheets/{spreadsheet_id}/{sheet_id}', Sheets())
api.add_route('/api/sheet/{spreadsheet_id}/values', SheetValues())
api.add_route('/api/user/{username}', User())
api.add_route('/api/user/auth/{auth_type}', Auth())

try:
    DataStore.connect_datastore()
except Exception as e:
    print('Exception while configuring datastore', e)

try:
    Redis.connect()
except Exception as e:
    print('Exception while connecting redis', e)