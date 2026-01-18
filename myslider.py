"""
Components/Slider
=================

.. seealso::

    `Material Design spec, Sliders <https://material.io/components/sliders>`_

.. rubric:: Sliders allow users to make selections from a range of values.

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/slider.png
    :align: center

With value hint
---------------

.. code-block:: python

    from kivy.lang import Builder

    from kivymd.app import MDApp

    KV = '''
    Screen

        MyMDSlider:
            min: 0
            max: 100
            value: 40
    '''


    class Test(MDApp):
        def build(self):
            return Builder.load_string(KV)


    Test().run()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/slider-1.gif
    :align: center

Without value hint
------------------

.. code-block:: kv

    MyMDSlider:
        min: 0
        max: 100
        value: 40
        hint: False

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/slider-2.gif
    :align: center

Without custom color
--------------------

.. code-block:: kv

    MyMDSlider:
        min: 0
        max: 100
        value: 40
        hint: False
        color: app.theme_cls.accent_color

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/slider-3.png
    :align: center
"""

__all__ = ("MyMDSlider",)

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    NumericProperty,
)
from kivy.graphics import Color, Rectangle, Ellipse

from kivy.uix.slider import Slider
from kivy.utils import get_color_from_hex

from kivymd.color_definitions import colors
from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import HoverBehavior

from kivy.app import App

Builder.load_string(
    """
#:import images_path kivymd.images_path
#:import Thumb kivymd.uix.selectioncontrol.Thumb


<MyMDSlider>
    id: slider
    canvas:
        Clear
    Widget:
        id: bar
        bar_color: [1, 1, 1, 1]
        canvas:
            Clear
            Color:
                rgba:
                    [0.3686274509803922, 0.3686274509803922, 0.3686274509803922, 1.0]
            Rectangle:
                size:
                    (self.parent.width - self.parent.padding * 2 , dp(4))
                pos:
                    (self.parent.x + self.parent.padding , self.parent.center_y - dp(4))
            Color:
                rgba:
                    [0.3686274509803922, 0.3686274509803922, 0.3686274509803922, 1.0]
            Rectangle:
                size:
                    ( dp(1), dp(2))
                pos:
                    (self.parent.x+self.parent.width - self.parent.padding + self.parent._offset[0], self.parent.center_y - dp(3))
            Color:
                rgba:
                    self.bar_color
            Rectangle:
                size:
                    ((self.parent.width - self.parent.padding * 2) * self.parent.value_normalized, sp(4)) 
                pos:
                    (self.parent.x + self.parent.padding, self.parent.center_y - dp(4))
            Color:
                rgba:
                    self.bar_color
            Rectangle:
                size:
                    (dp(1)*((self.parent.width - self.parent.padding * 2) * self.parent.value_normalized)+2, dp(2)) 
                pos:
                    (self.parent.x-1 + self.parent.padding, self.parent.center_y - dp(3))
    Thumb:
        id: thumb
        size_hint: None, None
        size:
            (dp(0), dp(0))
        pos:
            (slider.value_pos[0] - dp(8), slider.center_y - thumb.height / 2 - dp(2)) 
        color:
            (1, 1, 1, 1)
"""
)


class MyMDSlider(ThemableBehavior, HoverBehavior, Slider):
    active = BooleanProperty(False)
    """
    If the slider is clicked.

    :attr:`active` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.
    """

    is_hovered = BooleanProperty(False)

    hint = BooleanProperty(True)
    """
    If True, then the current value is displayed above the slider.

    :attr:`hint` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `True`.
    """

    hint_bg_color = ColorProperty(None)
    """
    Hint rectangle color in ``rgba`` format.

    :attr:`hint_bg_color` is an :class:`~kivy.properties.ColorProperty`
    and defaults to `None`.
    """

    hint_text_color = ColorProperty(None)
    """
    Hint text color in ``rgba`` format.

    :attr:`hint_text_color` is an :class:`~kivy.properties.ColorProperty`
    and defaults to `None`.
    """

    hint_radius = NumericProperty(4)
    """
    Hint radius.

    :attr:`hint_radius` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `4`.
    """

    show_off = BooleanProperty(True)
    """
    Show the `'off'` ring when set to minimum value.

    :attr:`show_off` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `True`.
    """

    color = ColorProperty([0, 0, 0, 0])
    """
    Color slider in ``rgba`` format.

    :attr:`color` is an :class:`~kivy.properties.ColorProperty`
    and defaults to `None`.
    """

    _track_color_active = ColorProperty([0, 0, 0, 0])
    _track_color_normal = ColorProperty([0, 0, 0, 0])
    _track_color_disabled = ColorProperty([0, 0, 0, 0])
    _thumb_pos = ListProperty([0, 0])
    _thumb_color_disabled = ColorProperty(
        get_color_from_hex(colors["Gray"]["400"])
    )
    # Internal state of ring
    _is_off = BooleanProperty(False)
    # Internal adjustment to reposition sliders for ring
    _offset = ListProperty((0, 0))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.bind(
            theme_style=self._set_colors,
            primary_color=self._set_colors,
            primary_palette=self._set_colors,
        )
        self.detect_visible = False
        self._set_colors()
        self.app = App.get_running_app()

    def on_enter(self):
        """
        Shows thumb, changes slider color, if there is stored thumb_proxy,
        adds thumb_proxy to canvas, because it was removed in on_leave callback. 
        """
        self.ids.thumb.size = (dp(12), dp(12))
        self.ids.bar.bar_color = [0.11764705882352941,
                                  0.8431372549019608, 0.3764705882352941, 1.0]

        if hasattr(self, 'thumb_proxy'):
            self.canvas.children[0].add(Color(rgba=[1, 1, 1, 1]))
            self.canvas.children[0].add(self.thumb_proxy)
            self.thumb_proxy.size=(dp(12), dp(12))

    def on_leave(self):
        """
        If slider is not clicked, changes slider color and
        removes thumb while storing it as self.thumb_proxy,
        to add it back on next on_enter callback. 
        """
        if not self.app.progressbar_is_active:
            self.ids.bar.bar_color = [1, 1, 1, 1]
            for child in self.canvas.children:
                for child2 in child.children:
                    if isinstance(child2, Ellipse):
                        self.thumb_proxy = child2
                        self.thumb_proxy.size=(dp(0), dp(0))
                        child.remove(child2)

    def on_hint(self, instance, value):
        if not value:
            self.remove_widget(self.ids.hint_box)

    def on_value_normalized(self, *args):
        """When the ``value == min`` set it to `'off'` state and make slider
        a ring.
        """

        self._update_is_off()

    def on_show_off(self, *args):
        self._update_is_off()

    def on__is_off(self, *args):
        self._update_offset()

    def on_active(self, *args):
        self._update_offset()

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            self.active = True
            self.app.progressbar_is_active = True

    def on_touch_move(self, touch):
        super().on_touch_move(touch)
        try:
            self.app.current_track['progress_ms'] = int(self.value)
            self.app.get_remaining_timer()
            self.app.get_progress_timer()
            self.app.get_progress_slider()
        except TypeError:
            return

    def on_touch_up(self, touch):
        if super().on_touch_up(touch):
            self.active = False
            self.app.spotify.seek_track(int(self.value), self.app.device['id'])
            self.app.current_track['progress_ms'] = int(self.value)
            self.app.progressbar_is_active = False
            self.app.get_remaining_timer()
            self.app.get_progress_timer()
            self.app.get_progress_slider()

            if not self.collide_point(*touch.pos):
                self.on_leave()

    def _update_offset(self):
        """Offset is used to shift the sliders so the background color
        shows through the off circle.
        """

        d = 2 if self.active else 0
        self._offset = (dp(11 + d), dp(11 + d)) if self._is_off else (0, 0)

    def _update_is_off(self):
        self._is_off = self.show_off and (self.value_normalized == 0)

    def _set_colors(self, *args):
        if self.theme_cls.theme_style == "Dark":
            self._track_color_normal = get_color_from_hex("FFFFFF")
            self._track_color_normal[3] = 0.3
            self._track_color_active = self._track_color_normal
            self._track_color_disabled = self._track_color_normal
            if self.color == [0, 0, 0, 0]:
                self.color = get_color_from_hex(
                    colors[self.theme_cls.primary_palette]["200"]
                )
            self.thumb_color_disabled = get_color_from_hex(
                colors["Gray"]["800"]
            )
        else:
            self._track_color_normal = get_color_from_hex("000000")
            self._track_color_normal[3] = 0.26
            self._track_color_active = get_color_from_hex("000000")
            self._track_color_active[3] = 0.38
            self._track_color_disabled = get_color_from_hex("000000")
            self._track_color_disabled[3] = 0.26
            if self.color == [0, 0, 0, 0]:
                self.color = self.theme_cls.primary_color
