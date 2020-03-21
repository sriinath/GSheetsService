from processes.datastore import DataStore
from falcon import HTTPServiceUnavailable, HTTPInternalServerError, HTTP_200, HTTPError, HTTP_201, HTTPBadRequest
import json
from routes.Base import Base

class Sheets(Base):
    def on_get(self, req, resp, spreadsheet_id, sheet_id):
        spreadsheet_id=spreadsheet_id
        try:
            spreadsheets=DataStore.get_sheet_instance()
        except Exception as e:
            print('Datastore is not configured properly', e)
            raise HTTPServiceUnavailable(description='Datastore is not configured properly')
        def run():
            value=spreadsheets.get(spreadsheetId=spreadsheet_id, fields='sheets.properties').execute()
            resp.body=json.dumps(dict(
                status='Success',
                spreadsheet_id=spreadsheet_id,
                data='sheets' in value and value['sheets'] or []
            ))
            resp.status=HTTP_200
        super().main(run)

    def on_post(self, req, resp, spreadsheet_id, sheet_id):
        spreadsheet_id=spreadsheet_id
        title=sheet_id
        body_props={
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": title
                        }
                    }
                }
            ]
        }
        try:
            spreadsheets=DataStore.get_sheet_instance()
        except Exception as e:
            print('Datastore is not configured properly', e)
            raise HTTPServiceUnavailable(description='Datastore is not configured properly')
        def run():
            value=spreadsheets.batchUpdate(spreadsheetId=spreadsheet_id, body=body_props).execute()
            sheet_info=dict()
            if 'replies' in value:
                sheet_props=dict()
                if value['replies'][0] and 'addSheet' in value['replies'][0] and 'properties' in value['replies'][0]['addSheet']:
                    sheet_props=value['replies'][0]['addSheet']['properties']
                if 'sheetId' in sheet_props:
                    sheet_info['id']=sheet_props['sheetId']
                if 'title' in sheet_props:
                    sheet_info['title']=sheet_props['title']
            resp.body=json.dumps(dict(
                status='Success',
                message='Successfully Created a new sheet',
                spreadsheet_id=value['spreadsheetId'],
                data=sheet_info
            ))
            resp.status=HTTP_201
        super().main(run)

    def on_delete(self, req, resp, spreadsheet_id, sheet_id):
        if sheet_id:
            try:
                spreadsheets=DataStore.get_sheet_instance()
            except Exception as e:
                print('Datastore is not configured properly', e)
                raise HTTPServiceUnavailable(description='Datastore is not configured properly')
            def run():
                body_props={
                    "requests": [
                        {

                            "deleteSheet": {
                                "sheetId": sheet_id
                            }
                        }
                    ]
                }
                value=spreadsheets.batchUpdate(spreadsheetId=spreadsheet_id, body=body_props).execute()
                resp.body=json.dumps(dict(
                    status='Success',
                    message='Successfully deleted the sheet with id {}'.format(sheet_id),
                    spreadsheet_id=value['spreadsheetId']
                ))
                resp.status=HTTP_200
            super().main(run)
        else:
            raise HTTPBadRequest(description='Sheet identifier is mandatory for this request')