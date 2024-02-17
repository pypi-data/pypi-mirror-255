"""Google Services Adapter module"""
from typing import List, Dict, Any
from os import environ, path as os_path
from io import BytesIO
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.discovery import Resource
from googleapiclient.discovery import HttpRequest
import pandas as pd
from .result_type import ResultType
from .value_input_option import ValueInputOption

# Considerar gspread como biblioteca a implementar para las funcionalidades que requieran interacción con google sheets

SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
ENV_VAR_NAMES = ["GOOGLE_TOKEN_PATH", "GOOGLE_CREDENTIALS_PATH"]

for env_var_name in ENV_VAR_NAMES:
    value = environ.get(env_var_name)
    if value is not None:
        globals()[env_var_name] = value
    else:
        raise EnvironmentError(
            f'Environment variable "{env_var_name}" is NOT set')


class GoogleServices():
    """Decorator for Google Services"""

    @classmethod
    def __get_google_credentials__(cls):
        creds = None
        try:
            if os_path.exists(GOOGLE_TOKEN_PATH):  # pylint:disable=undefined-variable
                creds = Credentials.from_authorized_user_file(
                    GOOGLE_TOKEN_PATH, SCOPES)  # pylint:disable=undefined-variable
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        GOOGLE_CREDENTIALS_PATH, SCOPES)  # pylint:disable=undefined-variable
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(GOOGLE_TOKEN_PATH, 'w', encoding="utf-8") as token:  # pylint:disable=undefined-variable
                    token.write(creds.to_json())
        except Exception as err:
            raise ValueError(
                f'Google Authentication Error {err}') from err
        return creds

    @classmethod
    def __standarized_dataframe__(cls, p_df: pd.DataFrame) -> pd.DataFrame:
        p_df.columns = p_df.columns.astype(str)
        p_df.columns = p_df.columns.str.lower()
        p_df.columns = p_df.columns.str.strip()
        p_df = p_df.dropna(how='all')
        return p_df

    @classmethod
    def get_spreadsheet_values(cls, spreadsheet_id: str, range_name: str) -> List[List[Any]]:
        """Lee datos de una Google spreadsheet especifica y lo devuelve como matriz.
        Si el rango no tiene contenido devuelve una lista vacía"""
        try:
            service = build(
                'sheets', 'v4', credentials=cls.__get_google_credentials__())
            if hasattr(service, 'spreadsheets'):
                sheet: Resource = service.spreadsheets()
                result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                            range=range_name).execute()
                return result.get('values', [])
        except Exception as err:
            raise ConnectionError(
                'Error al leer datos de Google Sheets: ', err) from err
        return []

    @classmethod
    def update_spreadsheet_values(cls, spreadsheet_id: str, range_name: str, values: List[List[Any]], value_input_option: ValueInputOption = ValueInputOption.USER_ENTERED) -> int:
        """Actualiza datos en un rango especifico de una Google spreadsheet.
        Devuelve la cantidad de celdas actualizadas."""
        try:
            service = build(
                'sheets', 'v4', credentials=cls.__get_google_credentials__())
            if hasattr(service, 'spreadsheets'):
                sheet: Resource = service.spreadsheets()
                result: dict = sheet.values().update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    body={
                        "values": values
                    },
                    valueInputOption=value_input_option.value
                ).execute()
                return result.get('updatedCells', 0)
        except Exception as err:
            raise ConnectionError(
                "Error al actualizar el contenido de la hoja de Google Sheets: ", err) from err
        return 0

    @classmethod
    def read_gsheet_data(cls, spreadsheet_id: str, range_name: str, result_type: ResultType = ResultType.JSON_LIST) -> pd.DataFrame | List[Dict[str, Any]]:
        """Lee datos de una Google spreadsheet especifica y lo devuelve como pandas DataFrame o JSON List"""
        df = pd.DataFrame()
        values = cls.get_spreadsheet_values(spreadsheet_id, range_name)
        if values:
            headers = values[0]
            data = values[1:]
            df = cls.__standarized_dataframe__(
                pd.DataFrame(data, columns=headers))
        if result_type == ResultType.JSON_LIST:
            return df.to_dict(orient='records')
        return df

    @classmethod
    def write_gsheet_data(cls, spreadsheet_id: str, range_name: str, values_as_df: pd.DataFrame = pd.DataFrame()) -> int:
        """Escribe datos en una Google spreadsheet especifica.
        Devuelve la cantidad de celdas escritas."""
        values = [values_as_df.columns.tolist()] + values_as_df.values.tolist()
        return cls.update_spreadsheet_values(spreadsheet_id, range_name, values)

    @classmethod
    def clear_gsheet_and_keep_format(cls, spreadsheet_id: str, range_name: str) -> bool:
        """Borra el contenido de las celdas pero mantiene el formato previo"""
        try:
            actual_values = cls.get_spreadsheet_values(
                spreadsheet_id, range_name)
            if actual_values:
                new_empty_values = [
                    ["" for _ in range(len(value))] for value in actual_values]
                updated_cells = cls.update_spreadsheet_values(
                    spreadsheet_id, range_name, new_empty_values)
                return sum(len(sublista) for sublista in actual_values) == updated_cells
        except Exception as err:
            raise ConnectionError(
                "Error al borrar el contenido de la hoja de Google Sheets manteniendo el formato: ", err) from err
        return False

    @classmethod
    def read_excel_data_from_google_drive(cls, file_id: str, sheet_name: str, output_data_type=None, result_type: ResultType = ResultType.JSON_LIST) -> pd.DataFrame | List[Dict[str, Any]]:
        """Lee datos de un XLS o XSLX de Google Drive y lo devuelve como pandas DataFrame o JSON List"""
        df = pd.DataFrame()
        try:
            service: Resource = build(
                'drive', 'v3', credentials=cls.__get_google_credentials__())
            if hasattr(service, 'files'):
                request: HttpRequest = service.files().get_media(fileId=file_id)
                downloader = request.execute()
                with BytesIO(downloader) as f:
                    xls = pd.ExcelFile(f)
                    for sheet in xls.sheet_names:
                        if sheet.strip() == sheet_name:
                            df = cls.__standarized_dataframe__(
                                xls.parse(sheet_name, dtype=output_data_type))
            if result_type == ResultType.JSON_LIST:
                return df.to_dict(orient='records')
            return df
        except Exception as err:
            raise ConnectionError(
                f'Error al leer datos en formato Excel desde Google Drive file id "{file_id}"') from err

    @classmethod
    def read_directory_content_from_google_drive(cls, dir_id: str, mime_type_filter: str) -> pd.DataFrame | List[Dict[str, Any]]:
        """Lee el contenido de un directorio de Google drive y lo devuelve en JSON"""
        data_as_json: list = []
        try:
            service: Resource = build(
                'drive', 'v3', credentials=cls.__get_google_credentials__())
            if hasattr(service, 'files'):
                results = service.files().list(
                    q=f"'{dir_id}' in parents and trashed=false", fields="files(id, name, mimeType)").execute()
                items = results.get('files', [])
                if items:
                    for item in items:
                        if item.get('mimeType') == mime_type_filter:
                            data_as_json.append(item)
            return data_as_json
        except Exception as err:
            raise ConnectionError(
                f'Error al leer el directorio "{dir_id}" de Google Drive') from err
