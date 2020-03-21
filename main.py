import falcon

from routes.Ping import Ping
from routes.Sheets import Sheets
from routes.SheetValues import SheetValues
from processes.datastore import DataStore

api = falcon.API()
api.add_route('/ping', Ping())
api.add_route('/api/sheets/{spreadsheet_id}/{sheet_id}', Sheets())
api.add_route('/api/sheet/{spreadsheet_id}/values', SheetValues())

try:
    DataStore.connect_datastore()
except Exception as e:
    print('Exception while configuring datastore', e)