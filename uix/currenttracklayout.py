
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivymd.uix.floatlayout import FloatLayout
from kivy.graphics import Line
from buttons import PlaybackButton

class CurrentTrackLayout(FloatLayout):
    app = None
    max_x_pos = None

    def __init__(self, max_x_pos, **kwargs):
        super().__init__(**kwargs)

        Window.bind(on_resize=self.on_window_resize)
        Window.bind(on_maximize=self.on_window_resize)
        Window.bind(on_restore=self.on_window_resize)
        self.app = App.get_running_app()
        self.max_x_pos = max_x_pos
        self.on_window_resize(Window, Window.width, Window.height)

    def on_window_resize(self, *args):
        self.canvas.before.clear()
        self.add_gradient_background(
            self.app.screen.ids.playback_progress.pos[0]-40)

    def add_gradient_background(self, position):
        """Adds gradient background under heart icon."""
        if position < 140:
            position = 171
        label_width = self.max_x_pos - 16
        if position > label_width:
            position = label_width
        alpha_channel_rate = 0
        increase_rate = 1 / 10
        self.paint_icon(position)
        r, g, b, _ = get_color_from_hex('#181818')
        for sep in range(24):

            self.canvas.before.add(Color(rgba=(r, g, b, alpha_channel_rate)))
            self.canvas.before.add(
                Line(points=[position-8+sep, 0, position-8+sep, 90], width=1))
            alpha_channel_rate += increase_rate
        self.canvas.before.add(Color(rgba=(r, g, b, alpha_channel_rate)))
        self.canvas.before.add(
            Rectangle(size=(Window.width/2, 50), pos=[position+10, 23]))

    def paint_icon(self, position):
        """Adds heart icon to save/remove song."""
        app = App.get_running_app()
        self.track = app.current_track['item']['id']
        is_saved = app.spotify.current_user_saved_tracks_contains([self.track, ])[
            0]
        if is_saved:
            heart_icon = PlaybackButton(app=app,
                                        icon='heart',
                                        tooltip_text='Remove from Your Library',
                                        size_hint=(None, None),
                                        pos=[position, self.pos[1]-13],
                                        user_font_size=20,
                                        size=(16, 16),
                                        shift_y=73,
                                        tooltip_radius=[3, ],
                                        theme_text_color='Custom',
                                        text_color='#1ed760')
        else:
            heart_icon = PlaybackButton(app=app,
                                        icon='heart-outline',
                                        user_font_size=20,
                                        size=(16, 16),
                                        shift_y=73,
                                        tooltip_radius=[3, ],
                                        tooltip_text='Save to Your Library',
                                        theme_text_color='Secondary',
                                        size_hint=(None, None),
                                        pos=[position, self.pos[1]-13])
        self.clear_widgets()
        self.add_widget(
            heart_icon
        )
