from os.path import abspath, dirname, join
from roche_datachapter_lib.query_manager import QueryManager
from roche_datachapter_lib.db_config import DB_CONFIG

QUERIES_DIR = join(dirname(abspath(__file__)), 'queries')
print("QUERIES DIR: ", QUERIES_DIR)
QUERY_MANAGER = QueryManager(QUERIES_DIR)
query = QUERY_MANAGER.get_query('stock_sap.sql')


print(DB_CONFIG.execute_custom_select_query(query,'sapdwp06'))
