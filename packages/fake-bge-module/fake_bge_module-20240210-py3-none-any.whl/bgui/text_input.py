import sys
import typing
import bgui.widget

GenericType = typing.TypeVar("GenericType")


class TextInput(bgui.widget.Widget):
    children = None
    ''' '''

    on_active = None
    ''' '''

    on_click = None
    ''' '''

    on_enter_key = None
    ''' '''

    on_hover = None
    ''' '''

    on_mouse_enter = None
    ''' '''

    on_mouse_exit = None
    ''' '''

    on_release = None
    ''' '''

    parent = None
    ''' '''

    position = None
    ''' '''

    prefix = None
    ''' '''

    size = None
    ''' '''

    system = None
    ''' '''

    text = None
    ''' '''

    theme_options = None
    ''' '''

    theme_section = None
    ''' '''

    def activate(self):
        ''' 

        '''
        pass

    def add_animation(self, animation):
        ''' 

        '''
        pass

    def calc_mouse_cursor(self, pos):
        ''' 

        '''
        pass

    def deactivate(self):
        ''' 

        '''
        pass

    def find_mouse_slice(self, pos):
        ''' 

        '''
        pass

    def move(self, position, time, callback):
        ''' 

        '''
        pass

    def select_all(self):
        ''' 

        '''
        pass

    def select_none(self):
        ''' 

        '''
        pass

    def swapcolors(self, state):
        ''' 

        '''
        pass

    def update_selection(self):
        ''' 

        '''
        pass
