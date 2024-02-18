"""ValueInputOption Class"""
from enum import Enum


class ValueInputOption(Enum):
    """Google Spreadahseet update ValueInputOption Class"""
    RAW = 'RAW'
    USER_ENTERED = 'USER_ENTERED'
    UNSPECIFIED = 'INPUT_VALUE_OPTION_UNSPECIFIED'
    
class ValueRenderOption(Enum):
    """Google Spreadahseet update ValueInputOption Class"""
    FORMATTED_VALUE = 'FORMATTED_VALUE'
    UNFORMATTED_VALUE = 'UNFORMATTED_VALUE'
    FORMULA = 'FORMULA'
