"""Query Manager Module"""
import os
import chardet


class QueryManager():
    """Clase para manejar la lectura de archivos SQL en el QUERIES_DIR"""

    def __init__(self, queries_dir):
        self.queries_dir = queries_dir
        self.default_encoding = 'utf-8'

    def __detect__enconding__(self, file) -> str:
        if os.path.exists(file) and os.path.isfile(file):
            with open(file, 'rb') as f:
                return chardet.detect(f.read())['encoding']
        return self.default_encoding

    def get_query(self, query_name: str = "") -> str:
        """Devuelve en string el código SQL de un archivo específico o None si no encuentra el archivo"""
        if isinstance(query_name, str) and not query_name.endswith(".sql"):
            query_name += ".sql"
        query_path = os.path.join(self.queries_dir, query_name)
        if os.path.exists(query_path) and os.path.isfile(query_path):
            with open(query_path, 'r', encoding=self.__detect__enconding__(query_path)) as file:
                return file.read()
        else:
            return None
