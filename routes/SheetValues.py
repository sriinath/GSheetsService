import json
from json.decoder import JSONDecodeError
from falcon import HTTPServiceUnavailable, \
    HTTPInternalServerError, \
    HTTP_200, \
    HTTPError, \
    HTTP_201, \
    HTTPPreconditionFailed, \
    HTTPUnprocessableEntity

from routes.Base import Base
from processes.datastore import DataStore

class SheetValues(Base):
    @staticmethod
    def __construct_mapped_dict(lists, fields, row_info):
        constructed_data_list=list()
        available_attr_index=list()
        list_len=len(lists)
        if list_len:
            constructed_mapping=dict()
            constructed_mapping['index']=dict()
            for row_index, row in enumerate(lists):
                if row_info:
                    temp_dict=dict(row=row_index)
                else:
                    temp_dict=dict()
                for attr_index, attr in enumerate(row):
                    if row_index == 0:
                        if fields is not None and len(fields):
                            if attr in fields:
                                available_attr_index.append(attr_index)
                                constructed_mapping['index'][attr_index]=attr
                        else:
                            available_attr_index.append(attr_index)
                            constructed_mapping['index'][attr_index]=attr
                    else:
                        if attr_index in constructed_mapping['index']:
                            temp_dict[constructed_mapping['index'][attr_index]]=attr
                if row_index != 0:
                    constructed_data_list.append(temp_dict)
        return constructed_data_list

    def on_get(self, req, resp, spreadsheet_id):
        sheet_range=req.get_param('range', required=True)
        data_format=req.get_param('format')
        data_fields=req.get_param('fields')
        row_info=req.get_param_as_bool('row_info')
        try:
            spreadsheets=DataStore.get_sheet_instance()
        except Exception as e:
            print('Datastore is not configured properly', e)
            raise HTTPServiceUnavailable(description='Datastore is not configured properly')
        def run():
            value=spreadsheets.values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute()
            value=list(value['values'])
            response_data=[]
            if len(value):
                if data_format=='raw':
                    response_data=value
                else:
                    data_fields_list=list()
                    if data_fields:
                        data_fields_list=data_fields.split(',')
                    response_data=SheetValues.__construct_mapped_dict(value, data_fields_list, row_info)
            resp.status=HTTP_200
            resp.body=json.dumps(response_data)
        super().main(run)

    def on_post(self, req, resp, spreadsheet_id):
        sheet_range=req.get_param('range', required=True)
        try:
            req_body=json.load(req.bounded_stream)
            if 'values' in req_body and isinstance(req_body['values'], list) and len(req_body['values']):
                dimensions='dimensions' in req_body and req_body['dimensions'] or 'ROWS'
                value_input='value_input_option' in req_body and req_body['value_input_option'] or 'USER_ENTERED'
                insert_option='insert_option' in req_body and req_body['insert_option'] or 'INSERT_ROWS'
                try:
                    spreadsheets=DataStore.get_sheet_instance()
                except Exception as e:
                    print('Datastore is not configured properly', e)
                    raise HTTPServiceUnavailable(description='Datastore is not configured properly')
                def run():
                    sheet_body={
                        "values": req_body['values'],
                        "majorDimension": dimensions
                    }
                    response=spreadsheets.values().append(
                        spreadsheetId=spreadsheet_id, body=sheet_body,
                        range=sheet_range, valueInputOption=value_input,
                        insertDataOption=insert_option
                    ).execute()
                    resp.body=json.dumps(dict(
                        status='Success',
                        message='Successfully Inserted data into sheet',
                        spreadsheet_id=response['spreadsheetId'],
                    ))
                    resp.status=HTTP_201
                super().main(run)
            else:
                raise HTTPPreconditionFailed(description='Values is a mandatory and must be valid for this request')
        except JSONDecodeError as err:
            print('Request body received', req.bounded_stream.read())
            print('Error while processing request', err)
            raise HTTPUnprocessableEntity(description='Cannot parse the body from the request')
        except (HTTPServiceUnavailable, HTTPPreconditionFailed, HTTPError) as err:
            raise err
        except Exception as e:
            print('Exception in creating sheet', e)
            raise HTTPInternalServerError(description='Something went wrong while creating sheet')

    def on_delete(self, req, resp, spreadsheet_id):
        sheet_id=req.get_param('sheet_id', required=True)
        dimensions=req.get_param('dimensions', default='ROWS')
        start_index=req.get_param('start_index', required=True)
        end_index=req.get_param('end_index', required=True)
        try:
            spreadsheets=DataStore.get_sheet_instance()
        except Exception as e:
            print('Datastore is not configured properly', e)
            raise HTTPServiceUnavailable(description='Datastore is not configured properly')
        def run():
            sheet_body={
                "requests": [
                    {
                        "deleteDimension": {
                            "range": {
                            "sheetId": sheet_id,
                            "dimension": dimensions,
                            "startIndex": start_index,
                            "endIndex": end_index
                            }
                        }
                    }
                ]
            }
            response=spreadsheets.batchUpdate(
                spreadsheetId=spreadsheet_id, body=sheet_body
            ).execute()
            resp.body=json.dumps(dict(
                status='Success',
                message='Successfully deleted {} from {} to {} in the sheet with id {}'.format(dimensions, start_index, end_index, sheet_id),
                spreadsheet_id=response['spreadsheetId']
            ))
            resp.status=HTTP_200
        super().main(run)

    def on_put(self, req, resp, spreadsheet_id):
        value_input=req.get_param('value_input_option', default='USER_ENTERED')
        try:
            req_body=json.load(req.bounded_stream)
            if 'data' in req_body and isinstance(req_body['data'], list) and len(req_body['data']):
                try:
                    spreadsheets=DataStore.get_sheet_instance()
                except Exception as e:
                    print('Datastore is not configured properly', e)
                    raise HTTPServiceUnavailable(description='Datastore is not configured properly')
                def run():
                    sheet_body={
                        "data": req_body['data'],
                        "valueInputOption": value_input
                    }
                    response=spreadsheets.values().batchUpdate(
                        spreadsheetId=spreadsheet_id, body=sheet_body
                    ).execute()
                    resp.body=json.dumps(dict(
                        status='Success',
                        message='Successfully updated the data in the sheet',
                        spreadsheet_id=response['spreadsheetId'],
                    ))
                    resp.status=HTTP_200
                super().main(run)
            else:
                raise HTTPPreconditionFailed(description='Data is a mandatory and must be valid for this request')
        except JSONDecodeError as err:
            print('Request body received', req.bounded_stream.read())
            print('Error while processing request', err)
            raise HTTPUnprocessableEntity(description='Cannot parse the body from the request')
        except (HTTPServiceUnavailable, HTTPPreconditionFailed, HTTPError) as err:
            raise err
        except Exception as e:
            print('Exception in updating sheet info', e)
            raise HTTPInternalServerError(description='Something went wrong while updating sheet')