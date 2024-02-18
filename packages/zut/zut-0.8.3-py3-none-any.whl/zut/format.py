import logging
from locale import localeconv, setlocale, LC_ALL

logger = logging.getLogger(__name__)


def configure_format(*, locale: str = '', delimiter: str = None, quotechar: str = None, nullval: str = None):
    Format.configure(locale=locale, delimiter=delimiter, quotechar=quotechar, nullval=nullval)


class Format:    
    _default_csv_delimiter: str
    _default_csv_quotechar = '"'
    _default_csv_nullval = ''

    @classmethod
    def configure(cls, *, locale: str = '', delimiter: str = None, quotechar: str = None, nullval: str = None):
        # If locale is empty: let Python find out the locale from the environment.
        locale_result = setlocale(LC_ALL, locale) #TODO

        if delimiter is not None:
            cls._default_csv_delimiter = delimiter
        else:
            cls._get_default_csv_delimiter()
        
        if quotechar is not None:
            cls._default_csv_quotechar = quotechar

        if nullval is not None:
            cls._default_csv_nullval = nullval

        logger.debug("configure format (locale=%s, default delimiter=%s, default quotechar=%s, default nullval=%s)", locale_result, cls._default_csv_delimiter, cls._default_csv_quotechar, cls._default_csv_nullval)

    @classmethod
    def _get_default_csv_delimiter(cls):
        try:
            return cls._default_csv_delimiter
        except AttributeError:
            cls._default_csv_delimiter = ';' if localeconv()['decimal_point'] == ',' else ','
            return cls._default_csv_delimiter
    
    @classmethod
    def apply_csv_defaults(cls, delimiter: str, quotechar: str, nullval: str):
        default_delimiter = cls._get_default_csv_delimiter()
        logger.debug("apply csv defaults (default delimiter=%s, default quotechar=%s, default nullval=%s)", default_delimiter, cls._default_csv_quotechar, cls._default_csv_nullval)
        delimiter = default_delimiter if delimiter is None else delimiter
        quotechar = cls._default_csv_quotechar if quotechar is None else quotechar
        nullval = cls._default_csv_nullval if nullval is None else nullval
        return delimiter, quotechar, nullval
