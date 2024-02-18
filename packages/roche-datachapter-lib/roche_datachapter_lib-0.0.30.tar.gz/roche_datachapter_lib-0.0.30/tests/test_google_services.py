"""Tests for google services module"""
from roche_datachapter_lib.google_services import GoogleServices
from roche_datachapter_lib.result_type import ResultType as R

GSHEET_FILE_ID = '10E9BcyglqUr14fs0nHgpNggO-x9WLBA3mronLa1a5FE'
XLS_FILE_ID = '1RWeuEPQiHgyLlD9KVSmUv3IhaNayqj6c'
SHEET_NAME = 'Sheet1'

GS= GoogleServices()

gs= GS.read_gsheet_data(GSHEET_FILE_ID, SHEET_NAME, R.JSON_LIST)
print(gs)

xls=GS.read_excel_data_from_google_drive(XLS_FILE_ID,SHEET_NAME, result_type=R.JSON_LIST)
print(xls)
