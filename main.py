import falcon
from threading import Thread

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
    redisThread=Thread(target=Redis.connect)
    print('starting redis')
    redisThread.start()
    print('joining redis')
except Exception as e:
    print('Exception while connecting redis', e)

try:
    data_store_thread=Thread(target=DataStore.connect_datastore)
    print('Conecting datastore')
    data_store_thread.start()
    print('joining datastore')
except Exception as e:
    print('Exception while configuring datastore', e)

redisThread.join()
print('joined redis')
data_store_thread.join()
print('joined datastore')

if __name__ == "__main__":
    from wsgiref import simple_server
    httpd = simple_server.make_server('127.0.0.1', 8000, api)
    httpd.serve_forever()