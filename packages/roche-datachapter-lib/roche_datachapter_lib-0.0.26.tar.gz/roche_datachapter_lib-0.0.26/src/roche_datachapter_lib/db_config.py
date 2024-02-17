"""All Database configurations and methods"""
from typing import List, Dict, Any
from os import environ
import pandas
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.exc import OperationalError
from .result_type import ResultType

ENV_VAR_NAMES = ["SQLSERVER_SERVER", "SQLSERVER_USER", "SQLSERVER_PWD",
                 "SQLSERVER_LATAM_AR_DB", "SQLSERVER_LATAM_AR_DEV_DB",
                 "SQLSERVER_LATAM_AR_FARMADB_DB", "SQLSERVER_LATAM_AR_SAND_DB",
                 "SQLSERVER_LATAM_AR_STAGING_DB", "SQLSERVER_LATAM_UY_DB",
                 "SQLSERVER_LATAM_UY_STAGING_DB", "GODW_SERVER", "GODW_PORT",
                 "GODW_USER", "GODW_PASSWORD", "GODW_SERVICENAME", "GODW_ORACLE_INSTANT_CLIENT_PATH",
                 "SAPDWP06_SERVER", "SAPDWP06_PORT", "SAPDWP06_USER", "SAPDWP06_PASSWORD", "SAPDWP06_DB",
                 "REXIS_SALES_SERVER", "REXIS_SALES_DB", "REXIS_SERVICES_SERVER", "REXIS_SERVICES_DB"]

for env_var_name in ENV_VAR_NAMES:
    value = environ.get(env_var_name)
    if value is not None:
        globals()[env_var_name] = value
    else:
        raise EnvironmentError(
            f'Environment variable "{env_var_name}" is NOT set')

SQLSERVER_BASE = None
if all(item in globals() for item in ENV_VAR_NAMES):
    # pylint:disable=undefined-variable
    SQLSERVER_BASE = "mssql+pymssql://" + \
        f"{SQLSERVER_USER}:{SQLSERVER_PWD}@{SQLSERVER_SERVER}"


class DbConfig():
    """All DB config params"""
    SQLALCHEMY_BINDS = {
        'sqlserver_master': f"{SQLSERVER_BASE}/master",  # pylint:disable=undefined-variable
        'sqlserver_msdb': f"{SQLSERVER_BASE}/msdb",  # pylint:disable=undefined-variable
        'sqlserver_tempdb': f"{SQLSERVER_BASE}/tempdb",  # pylint:disable=undefined-variable
        'sqlserver_model': f"{SQLSERVER_BASE}/model",  # pylint:disable=undefined-variable
        'sqlserver_latam_ar': f"{SQLSERVER_BASE}/{SQLSERVER_LATAM_AR_DB}",  # pylint:disable=undefined-variable
        'sqlserver_latam_ar_dev': f"{SQLSERVER_BASE}/{SQLSERVER_LATAM_AR_DEV_DB}",  # pylint:disable=undefined-variable
        'sqlserver_latam_ar_farmadb': f"{SQLSERVER_BASE}/{SQLSERVER_LATAM_AR_FARMADB_DB}",  # pylint:disable=undefined-variable
        'sqlserver_latam_ar_sand': f"{SQLSERVER_BASE}/{SQLSERVER_LATAM_AR_SAND_DB}",  # pylint:disable=undefined-variable
        'sqlserver_latam_ar_staging': f"{SQLSERVER_BASE}/{SQLSERVER_LATAM_AR_STAGING_DB}",  # pylint:disable=undefined-variable
        'sqlserver_latam_uy': f"{SQLSERVER_BASE}/{SQLSERVER_LATAM_UY_DB}",  # pylint:disable=undefined-variable
        'sqlserver_latam_uy_staging': f"{SQLSERVER_BASE}/{SQLSERVER_LATAM_UY_STAGING_DB}",  # pylint:disable=undefined-variable
        'godw': f"oracle+oracledb://{GODW_USER}:{GODW_PASSWORD}@{GODW_SERVER}:{GODW_PORT}/?service_name={GODW_SERVICENAME}",  # pylint:disable=undefined-variable
        'sapdwp06': f"hana+hdbcli://{SAPDWP06_USER}:{SAPDWP06_PASSWORD}@{SAPDWP06_SERVER}:{SAPDWP06_PORT}/{SAPDWP06_DB}?encrypt=true",  # pylint:disable=undefined-variable
        'rexis_sales': f"mssql+pymssql://@{REXIS_SALES_SERVER}/{REXIS_SALES_DB}",  # pylint:disable=undefined-variable
        'rexis_services': f"mssql+pymssql://@{REXIS_SERVICES_SERVER}/{REXIS_SERVICES_DB}"  # pylint:disable=undefined-variable
    }

    @classmethod
    def __get_bind__(cls, bind: str = ''):
        return cls.SQLALCHEMY_BINDS[cls.validate_bind(bind)]

    @classmethod
    def __check_select_query__(cls, query: str = ''):
        if not query.lower().strip().startswith("select"):
            raise ValueError(f'NOT SELECT query: "{query[:100].strip().replace(
                '\n', ' ').replace('\t', ' ').replace('  ', ' ')}..."')

    @classmethod
    def validate_bind(cls, bind: str = ''):
        """Bind validation"""
        if bind in cls.SQLALCHEMY_BINDS:
            return bind
        available_binds = ', '.join(
            f"{key}" for key in cls.SQLALCHEMY_BINDS)
        raise ValueError(
            f'Bind Key "{bind}" NOT valid. Available binds are: {available_binds}')

    @classmethod
    def test_bind_connection(cls, bind: str = ''):
        """Bind testing. Return True if connection success, otherwise return False"""
        try:
            engine = create_engine(cls.__get_bind__(bind), echo=True)
            with engine.connect():
                return True
        except OperationalError:
            return False
        return False

    @classmethod
    def execute_custom_select_query(cls, query: str, p_bind: str, result_set_as: ResultType = ResultType.PANDAS_DATA_FRAME) -> pandas.DataFrame | List[Dict[str, Any]]:
        """Execute SQL SELECT query on specific bind and return result set as a pandas DataFrame"""
        cls.__check_select_query__(query)
        df = pandas.DataFrame()
        engine = create_engine(cls.__get_bind__(p_bind))
        with engine.connect() as connection:
            result = connection.execute(text(query))
            all_rows = result.fetchall()
            if len(all_rows) > 0:
                df = pandas.DataFrame.from_records(
                    all_rows, columns=result.keys())
        if result_set_as == ResultType.JSON_LIST:
            df = df.to_dict(orient='records')
        return df

    @classmethod
    def execute_stored_procedure(cls, sp_name: str, sp_params: dict = None, p_bind: str = 'sqlserver_master'):
        """Execute SQL query on specific bind and return result set as a dictionary"""
        engine = create_engine(cls.__get_bind__(p_bind))
        with engine.connect() as connection:
            sql_string = f"EXEC {sp_name} "
            params = []
            if isinstance(sp_params, dict):
                for clave, valor in sp_params.items():
                    if not clave.startswith('@'):
                        clave = f'@{clave}'
                    if isinstance(valor, str):
                        params.append(f"{clave}=N'{valor}'")
                    elif isinstance(valor, bool):
                        params.append(f"{clave}={1 if valor else 0}")
                    elif isinstance(valor, (int, float)):
                        params.append(f"{clave}={repr(valor)}")
                    else:
                        print(type(valor))
                        input(valor)
                        raise ValueError(
                            "sp_params only accept dict of int, float, bool or str")
                sql_string += ', '.join(params)
            connection.execute(text(sql_string))
            connection.commit()


DB_CONFIG = DbConfig()
