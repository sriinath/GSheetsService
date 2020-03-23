AUTHENTICATION_VALIDATION_PATHS={
    '/api/sheets/{spreadsheet_id}/{sheet_id}': ['GET', 'POST', 'DELETE'],
    '/api/sheet/{spreadsheet_id}/values': ['GET', 'POST', 'DELETE', 'POST'],
    '/api/user/{username}': ['GET'],
    '/api/user/auth/{auth_type}': ['POST']
}

ACCESS_TOKEN_VALIDATION_PATHS={
    '/api/sheets/{spreadsheet_id}/{sheet_id}': ['GET', 'POST', 'DELETE'],
    '/api/sheet/{spreadsheet_id}/values': ['GET', 'POST', 'DELETE', 'POST'],
    '/api/user/{username}': ['GET'],
    '/api/user/auth/{auth_type}': ['POST']
}