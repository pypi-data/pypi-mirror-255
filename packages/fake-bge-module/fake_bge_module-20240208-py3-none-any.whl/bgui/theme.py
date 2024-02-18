import sys
import typing

GenericType = typing.TypeVar("GenericType")


class NewSectionProxy:
    name = None
    ''' '''

    parser = None
    ''' '''

    def clear(self):
        ''' 

        '''
        pass

    def get(self, option, fallback, raw, vars, _impl, kwargs):
        ''' 

        '''
        pass

    def items(self):
        ''' 

        '''
        pass

    def keys(self):
        ''' 

        '''
        pass

    def pop(self, key, default):
        ''' 

        '''
        pass

    def popitem(self):
        ''' 

        '''
        pass

    def setdefault(self, key, default):
        ''' 

        '''
        pass

    def update(self, other, kwds):
        ''' 

        '''
        pass

    def values(self):
        ''' 

        '''
        pass


class Theme:
    BOOLEAN_STATES = None
    ''' '''

    NONSPACECRE = None
    ''' '''

    OPTCRE = None
    ''' '''

    OPTCRE_NV = None
    ''' '''

    SECTCRE = None
    ''' '''

    converters = None
    ''' '''

    path = None
    ''' '''

    def add_section(self, section):
        ''' 

        '''
        pass

    def clear(self):
        ''' 

        '''
        pass

    def defaults(self):
        ''' 

        '''
        pass

    def get(self, section, option, raw, vars, fallback):
        ''' 

        '''
        pass

    def getboolean(self, section, option, raw, vars, fallback, kwargs):
        ''' 

        '''
        pass

    def getfloat(self, section, option, raw, vars, fallback, kwargs):
        ''' 

        '''
        pass

    def getint(self, section, option, raw, vars, fallback, kwargs):
        ''' 

        '''
        pass

    def has_option(self, section, option):
        ''' 

        '''
        pass

    def has_section(self, section):
        ''' 

        '''
        pass

    def items(self, section, raw, vars):
        ''' 

        '''
        pass

    def keys(self):
        ''' 

        '''
        pass

    def options(self, section):
        ''' 

        '''
        pass

    def optionxform(self, optionstr):
        ''' 

        '''
        pass

    def pop(self, key, default):
        ''' 

        '''
        pass

    def popitem(self):
        ''' 

        '''
        pass

    def read(self, filenames, encoding):
        ''' 

        '''
        pass

    def read_dict(self, dictionary, source):
        ''' 

        '''
        pass

    def read_file(self, f, source):
        ''' 

        '''
        pass

    def read_string(self, string, source):
        ''' 

        '''
        pass

    def readfp(self, fp, filename):
        ''' 

        '''
        pass

    def remove_option(self, section, option):
        ''' 

        '''
        pass

    def remove_section(self, section):
        ''' 

        '''
        pass

    def sections(self):
        ''' 

        '''
        pass

    def set(self, section, option, value):
        ''' 

        '''
        pass

    def setdefault(self, key, default):
        ''' 

        '''
        pass

    def supports(self, widget):
        ''' 

        '''
        pass

    def update(self, other, kwds):
        ''' 

        '''
        pass

    def values(self):
        ''' 

        '''
        pass

    def warn_legacy(self, section):
        ''' 

        '''
        pass

    def warn_support(self, section):
        ''' 

        '''
        pass

    def write(self, fp, space_around_delimiters):
        ''' 

        '''
        pass
