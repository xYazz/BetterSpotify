
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.uix.label import Label

from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import HoverBehavior

class TrackTableLabel(Label, ThemableBehavior, HoverBehavior):
    '''Custom item implementing hover behavior.'''
    id = None
    __events__ = ['on_ref_press', 'on_ref_enter', 'on_ref_leave']
    underlines = {}

    def __init__(self, has_link=False, on_enter_color='#b3b3b3', link=None, on_leave_color=None, **kwargs):
        self.app = App.get_running_app()
        self.has_link = has_link
        self.link = link
        self.color = on_enter_color
        if on_leave_color:
            self.color = on_leave_color
        self.on_enter_color = on_enter_color
        self.on_leave_color = on_leave_color
        self.detect_visible = True
        super().__init__(**kwargs)

    def on_parent_resize(self):
        self.size = self.parent.size
        self.texture_update()
        self.text_size = (self.size[0], None)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button == 'left' and len(self.app.pressed_buttons) == 0:
                if self.has_link:
                    self.app.rmb_track_menu.go_to_album_page(self.link)
                if not len(self.refs):
                    return False
                tx, ty = touch.pos
                tx -= self.center_x - self.texture_size[0]/2
                for uid, zones in self.refs.items():
                    for zone in zones:
                        x, y, w, h = zone
                        # Adjust zone detection to match underlining.
                        if x - 1 <= tx <= w:
                            self.dispatch('on_ref_press', uid)
                            return True
                return False

    def on_enter(self, *args):
        '''The method will be called when the mouse cursor
        is within the borders of the current widget.'''
        # if not self.app.playlist_panel_resizing:
        Window.bind(mouse_pos=self.on_mouse_update_hovering_over_refs)
        if self.has_link:
            self.underline = True
        if self.on_leave_color:
            self.color = self.on_enter_color

    def on_ref_press(self, *args):
        App.get_running_app().rmb_track_menu.go_to_artist_page(args[0])

    def on_mouse_update_hovering_over_refs(self, *args):
        '''The method checking if mouse is over any of 
        the refs zones, if so, dispatches according event'''
        if not len(self.refs):
            return False
        tx, ty = args[1]

        # Adjust mouse position, to match recieved mouse_pos
        # by substracting left panel's width from mouse_pos x.
        tx -= self.app.screen.ids.splitter.size[0]
        for uid, zones in self.refs.items():
            for zone in zones:
                x, y, w, h = zone

                if self.pos[0]+x <= tx <= self.pos[0]+w:
                    self.dispatch('on_ref_enter', uid, x, w)
                else:
                    self.dispatch('on_ref_leave', uid)
        return False

    def on_ref_enter(self, *args):
        with self.canvas.before:
            Color(*get_color_from_hex('#ffffff'))
            self.underlines[args[0]] = Rectangle(
                pos=[self.pos[0]+args[1], self.pos[1]+5],
                size=[args[2]-args[1], 1],
            )

    def on_ref_leave(self, *args):
        try:
            self.canvas.before.remove(self.underlines[args[0]])
            del self.underlines[args[0]]
            self.canvas.before.clear()
        except KeyError:
            pass
        except ValueError:
            pass

    def on_leave(self, *args):
        '''The method will be called when the mouse cursor goes beyond
        the borders of the current widget.'''
        if self.has_link:
            self.underline = False
        self.canvas.before.clear()
        Window.unbind(mouse_pos=self.on_mouse_update_hovering_over_refs)
