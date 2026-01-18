
from re import X
from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import NumericProperty, ListProperty
from kivy.utils import get_color_from_hex
from kivy.graphics import RoundedRectangle, Triangle
from kivy.graphics import Color
import kivymd.material_resources as m_res
from kivymd.uix.list import BaseListItem
from kivymd.uix.behaviors import HoverBehavior
from kivymd.theming import ThemableBehavior
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDIconButton




class RightMouseButtonListItem(BaseListItem, ThemableBehavior, HoverBehavior):
    """A one line list item."""

    _txt_left_pad = NumericProperty("10dp")
    _txt_top_pad = NumericProperty("13dp")
    _txt_bot_pad = NumericProperty("13dp")  # dp(20) - dp(5)
    _txt_right_pad = NumericProperty("10dp")
    _height = NumericProperty()
    _num_lines = 1
    rect = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.font_style = 'Arialbd'
        self.detect_visible = False
        self.height = dp(48)
        self.on_leave()

    def on_touch_down(self, touch):
        self.on_leave()
        return super().on_touch_down(touch)

    def on_enter(self):
        if hasattr(self.app, 'rmb_nested_menu'):
            self.app.rmb_nested_menu.dismiss()
        self.canvas.before.add(
            Color(*get_color_from_hex('#3e3e3e'))
        )

        self.rect = RoundedRectangle(
            pos=[self.pos[0]+4, self.pos[1]],
            size=[self.size[0]-8, self.size[1]],
            radius=[3, 3, 3, 3])
        self.canvas.before.add(self.rect)

    def on_leave(self):
        if self.rect:
            self.canvas.before.remove(self.rect)
            self.rect=None


class RightMouseButtonNestedListItem(RightMouseButtonListItem):
    def on_enter(self):
        self.canvas.before.add(
            Color(*get_color_from_hex('#3e3e3e'))
        )

        self.rect = RoundedRectangle(
            pos=[self.pos[0]+4, self.pos[1]],
            size=[self.size[0]-24, self.size[1]],
            radius=[3, 3, 3, 3])
        self.canvas.before.add(self.rect)

class SearchFieldTextInput(TextInput):
    def __init__(self, **kwargs):
        self.multiline=False
        self.items_list_is_set = False
        self.hint_text="Find a playlist"
        self.pos_hint={'top': 0.82}
        self.foreground_color = (1,1,1,1)
        self.cursor_color = (1,1,1,1)
        self.background_color = (0,0,0,0)
        self.size_hint=(None, None)
        self.close_icon=kwargs.pop('close_icon')
        super().__init__(**kwargs)

    def on_text(self, *args, **kwargs):
        if self.text:
            self.close_icon.opacity=1
        else:
            self.close_icon.opacity=0
        subtext = args[1]
        if not self.items_list_is_set:
            self.items_list_is_set = True
            self.menu = self.parent.parent.parent.parent.parent
        self.menu.filter_children_with_subtext(subtext)


            

class RightMouseButtonSearchField(BoxLayout):
    ICON_SIZE = 22
    ICON_COLOR = '#C5C5C5'
    THEME_COLOR = 'Custom'
    ICON_POS_HINT = {'top': 1.05}
    MARGIN = 32
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_widgets()
        self.add_widget(self.icon)
        self.add_widget(self.text_input)
        self.add_widget(self.close_icon)

    def setup_widgets(self):
        self.icon = MDIconButton(icon='magnify',
                                theme_text_color=self.THEME_COLOR,
                                text_color=self.ICON_COLOR,
                                user_font_size=self.ICON_SIZE, 
                                pos_hint=self.ICON_POS_HINT)
        self.icon.on_touch_down = lambda obj: None
        self.canvas.before.add(Color(rgba=[*get_color_from_hex('#3e3e3e')]))
        self.background = RoundedRectangle(radius=[4, 4, 4, 4])
        self.canvas.before.add(self.background)
        self.bind(pos=lambda obj, pos: setattr(
                                self.background, "pos", [pos[0]+6, pos[1]+2]))
        self.bind(size=lambda obj, size: setattr(
                                self.background, "size", [size[0]-self.MARGIN, self.MARGIN]))

        self.close_icon = MDIconButton(icon='close', 
                                theme_text_color=self.THEME_COLOR,
                                text_color=self.ICON_COLOR,
                                user_font_size=self.ICON_SIZE, 
                                pos_hint=self.ICON_POS_HINT,
                                opacity=0)
        def on_release():
            self.text_input.text=''
        self.close_icon.on_release=on_release

        self.text_input = SearchFieldTextInput(size=(self.size[0]-self.MARGIN, self.MARGIN), 
                                close_icon=self.close_icon)
        self.bind(size=lambda obj, size: setattr(
                                self.text_input, "size", [size[0]-105, size[1]]))

    def on_touch_down(self, touch):
        super().on_touch_down(touch)

class RightMouseButtonNestedMenu(RightMouseButtonListItem):
    row_size = []
    points = ListProperty()
    can = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.add_triangle_on_canvas()

    def on_enter(self):
        super().on_enter()
        self.triangle = Triangle(
            points=[self.pos[0]+self.size[0]-18, self.pos[1]+17,
                    self.pos[0]+self.size[0]-18, self.pos[1]+self.size[1]-12,
                    self.pos[0]+self.size[0]-12, self.pos[1]+self.size[1]/2+3])
        self.canvas.add(self.triangle)
        hor_growth='right'
        if self.parent.parent.parent.parent.hor_growth=='left':
            hor_growth='left'
        
        pos = [*self.parent.parent.parent.parent.touch.pos]
        pos[1]+=self.pos[1]
        if self.text=='Add to playlist':
            self.app.open_nested_rmb_menu(self, pos, self.parent.parent.parent.parent.row_width, hor_growth)

    def add_triangle_on_canvas(self):
        with self.canvas.after:
            Color(rgba=[1, 1, 1, 1]),
            self.triangle = Triangle(
                points=[0, 0, 0, 0, 0, 0],
            )
        self.bind(size=lambda obj, size: setattr(
            self.triangle, "points", [self.pos[0]+size[0]-18, self.pos[1]+17,
                                      self.pos[0]+size[0] -
                                      18, self.pos[1]+size[1]-12,
                                      self.pos[0]+size[0]-12, self.pos[1]+size[1]/2+3]))


class RightMouseButtonListDivider(BaseListItem, ThemableBehavior, HoverBehavior):
    """A one line list item."""
    _height = NumericProperty()
    _num_lines = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.height = dp(48) if not self._height else self._height
        self.canvas.before.add(
            Color(*get_color_from_hex('#3e3e3e'))
        )
        self.background = RoundedRectangle(
            pos=[self.pos[0]+4, self.pos[1]],
            size=[self.size[0]-8, self.size[1]],
            radius=[4, 4, 4, 4])
        self.canvas.before.add(self.background)
        self.bind(pos=lambda obj, pos: setattr(
            self.background, "pos", [pos[0]+7, pos[1]]))
        self.bind(size=lambda obj, size: setattr(
            self.background, "size", [size[0]-13, size[1]]))


class DropDownMenuTrackWithMousePos(MDDropdownMenu):
    row_width = NumericProperty(100)

    def __init__(self, touch=None, row_width=183, **kwargs):
        super().__init__(**kwargs)
        self.unfiltered_items = self.items
        self.touch = touch
        self.row_width = row_width

    def filter_children_with_subtext(self, subtext):
        longest_playlist_name = 25
        items_copy = self.unfiltered_items[:3]
        for item in self.unfiltered_items[3:]:
            if subtext.upper() in item['text'].upper():
                items_copy.append(item)
        
        for item in items_copy:
                longest_playlist_name = max(
                    longest_playlist_name, len(item['text']))
        self.row_width=longest_playlist_name*7.5
        self.items=items_copy

        self.menu.width = self.row_width
        self.set_menu_properties(0)
        

    def set_menu_properties(self, interval=0):
        """Sets the size and position for the menu window."""
        if self.caller:
            print(self.caller)
            self.ids.md_menu.data = self.items
            # We need to pick a starting point, see how big we need to be,
            # and where to grow to.
            try:
                pos = self.touch.pos
            except AttributeError:
                pos = self.touch
            self._start_coords = self.caller.to_window(
                *pos
            )
            print('test')

            window_touch = [*self._start_coords]
            start_cords = window_touch
            # Set width
            self.target_width = self.row_width
            print(self.target_width)
            # If we're wider than the Window...
            if self.target_width > Window.width:
                # ...reduce our multiplier to max allowed.
                self.target_width = (
                    int(Window.width / m_res.STANDARD_INCREMENT)
                    * m_res.STANDARD_INCREMENT
                )

            # Set the target_height of the menu depending on the size of
            # each MDMenuItem or MDMenuItemIcon.
            self.target_height = 8
            for item in self.ids.md_menu.data:
                self.target_height += item.get("height", dp(72))
            # If we're over max_height...
            if 0 < self.max_height < self.target_height:
                self.target_height = self.max_height

            # Establish vertical growth direction.
            if self.ver_growth is not None:
                ver_growth = self.ver_growth
            else:
                if (
                    Window.height - window_touch[1] < window_touch[1]
                ):

                    ver_growth = "down"
                    if window_touch[1] <= self.target_height:
                        start_cords[1] = 8 + self.target_height
                # If there's more space above us:
                else:
                    ver_growth = "up"
                    if Window.height - window_touch[1] < self.target_height:
                        start_cords[1] = Window.height-8 - self.target_height
            self._start_coords = self.caller.to_window(
                *start_cords
            )
            if self.hor_growth is not None:
                hor_growth = self.hor_growth
            else:
                # If there's enough space to the right:
                if (
                    self.target_width
                    <= Window.width - self._start_coords[0] - self.border_margin
                ):
                    hor_growth = "right"
                # if there's enough space to the left:
                elif (
                    self.target_width
                    < self._start_coords[0] - self.border_margin
                ):
                    hor_growth = "left"
                # Otherwise, let's pick the one with more space and adjust ourselves.
                else:
                    # if there"s more space to the right:
                    if (
                        Window.width - self._start_coords[0]
                        >= self._start_coords[0]
                    ):
                        hor_growth = "right"
                        self.target_width = (
                            Window.width
                            - self._start_coords[0]
                            - self.border_margin
                        )
                    # if there"s more space to the left:
                    else:
                        hor_growth = "left"
                        self.target_width = (
                            self._start_coords[0] - self.border_margin
                        )

            if ver_growth == "down":
                self.tar_y = start_cords[1] - self.target_height
            else:  # should always be "up"
                self.tar_y = start_cords[1]

            if hor_growth == "right":
                self.tar_x = start_cords[0]
            else:  # should always be "left"
                self.tar_x = start_cords[0] - \
                    self.target_width - self.border_margin
                self.hor_growth='left'
            self._calculate_complete = True
