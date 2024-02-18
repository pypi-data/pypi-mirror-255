"""Data transform module"""
from datetime import datetime
from math import isnan


class DataTransformer:
    """Data transform static class"""

    @classmethod
    def datestr_to_date(cls, datestr: str = '', date_format="%d/%m/%Y"):
        """Convierte string con formato específico o por defecto 'dd/mm/YYYY' a una fecha.
        Formatos aceptados en: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        Return None if not possible"""
        try:
            return datetime.strptime(datestr, date_format)
        except ValueError:
            return None

    @classmethod
    def date_to_str(cls, date: datetime, output_format='%d/%m/%Y'):
        """Formatea fecha a string en el formato especificado o por defecto 'dd/mm/YYYY'.
        Formatos aceptados en: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes 
        Return None if not possible"""
        if isinstance(date, datetime):
            try:
                return date.strftime(output_format)
            except ValueError:
                return None
        return None

    @classmethod
    def date_to_datesk(cls, date: datetime):
        """Formatea fecha a string YYYYMMDD.
        Return None if not possible"""
        return cls.date_to_str(date, '%Y%m%d')

    @classmethod
    def str_to_float(cls, p_input: str):
        """Convierte string a float.
        Return None if not possible"""
        try:
            valor_float = float(p_input)
            return valor_float
        except ValueError:
            return None

    @classmethod
    def str_to_bool(cls, p_input: str = ''):
        """Convierte string a Boolean.
        Return None if not possible"""
        if isinstance(p_input, bool):
            return p_input
        try:
            bool_value = p_input.strip().lower() in (
                'true', 'verdadero', 'yes', 'sí', 'si')
            return bool_value
        except ValueError:
            return None

    @classmethod
    def str_to_int(cls, p_input: str = ''):
        """Convierte string a int.
        Return None if not possible"""
        try:
            valor_int = int(p_input)
            return valor_int
        except ValueError:
            return None

    @classmethod
    def nan_to_none(cls, p_input: float):
        """Convierte nan a None.
        Return p_input if not possible"""
        if isinstance(p_input, float) and isnan(p_input):
            return None
        if isinstance(p_input, str) and p_input == '':
            return None
        return p_input

    @classmethod
    def none_to_no_especificado(cls, p_input: None = None):
        """Convierte None a el string 'No especificado'.
        Return p_input if not possible"""
        return "No especificado" if p_input is None else p_input
