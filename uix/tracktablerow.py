
import pprint
from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import BooleanProperty

from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import HoverBehavior
from kivymd.uix.button import MDIconButton
from kivymd.uix.floatlayout import FloatLayout


class TrackTableRow(BoxLayout, ThemableBehavior, HoverBehavior):
    '''Custom item implementing hover behavior.'''
    spotify_id = None
    album_id = None
    song_link = None
    artists_ids = None
    __is_playing = False
    __is_selected = False

    selected = BooleanProperty(False)
    
    def __init__(self, row_number,  spotify_id, album_id, song_link, artists_ids, context_type='playlist', **kwargs):
        super().__init__(**kwargs)
        self.spotify_id = spotify_id
        self.album_id = album_id
        self.song_link = song_link
        self.row_number = row_number
        self.artists_ids = artists_ids
        self.context_type = context_type
        self.opacity = 1
        self.height = 55
        if self.context_type == 'playlist':
            self.title_label_idx = -3
        else:
            self.title_label_idx = -2
        self.app = App.get_running_app()
        self.check_if_track_is_currently_playing()
        #     Clock.schedule_once(self.load_playing_track, .01)
        # Clock.schedule_once(self.add_playing_anim, .1)
        self.bind(selected=self.on_selected)
        
    @property
    def is_playing(self):
        return self.__is_playing

    @is_playing.setter
    def is_playing(self, value):
        if value:
            self.anim_layout.opacity=1
            self.button.opacity=0
            self.row_num_label.opacity=0
            self.button.on_touch_up = self.pause_button_callback
        
        else:
            self.anim_layout.opacity=0
            self.button.opacity=1
            self.row_num_label.opacity=0
            self.button.on_touch_up = self.resume_button_callback
        self.__is_playing = value

    @property
    def is_selected(self):
        return self.__is_selected

    @is_selected.setter
    def is_selected(self, value):
        self.__is_selected = value

    def on_selected(self, *args):
        if args[1]==True:
            self.row_active()
        else:
            self.row_inactive()

    @staticmethod
    def display_playing_from_context_play_button(interval):
        app = App.get_running_app()
        for row in app.tracks_table:
            if isinstance(row, TrackTableRow):
                if row.spotify_id == app.playing_track:
                    row.remove_previous_playing_track()
                    row_button = row.get_row_playback_button()
                    row_num_label = row.get_row_numb_label()

                    def touched(touch):
                        if row_button.collide_point(*touch.pos) and touch.button == 'left':
                            if app.is_playing:
                                Clock.unschedule(app.clock)

                                row_num_label.color = '#1ed760'
                                row_num_label.opacity = 0
                                app.is_playing = False
                                row.anim_layout.opacity = 0
                                app.playing_track_row = row
                                app.spotify.pause_playback(
                                    device_id=row.app.device['id'])
                                row.add_playback_button(False)
                    row_button.on_touch_up = touched
                    row.anim_layout.opacity = 1
                    row_button.opacity = 0
                    app.playing_track_row = row

    def add_playing_anim(self, interval):
        self.add_currently_playing_animated_icon()
        if not self.check_if_track_is_currently_playing() or not self.app.is_playing:
            self.anim_layout.opacity = 0
        else:
            self.row_num_label = self.get_row_numb_label()
            self.row_num_label.opacity = 0


    def load_playing_track(self, interval):
        self.add_playback_button()
        self.button.icon = 'pause'
        self.button.opacity = 0
        self.row_num_label = self.get_row_numb_label()
        if self.app.is_playing:
            self.row_num_label.color = '#1ed760'
            self.row_num_label.opacity=0
        else:
            self.button.icon = 'play'
            self.row_num_label.color = '#1ed760'
            self.row_num_label.opacity = 1
            self.button.on_touch_up = self.resume_button_callback
        try:
            self.children[self.title_label_idx].children[-1].children[0].color = '#1ed760'
        except IndexError:
            self.children[self.title_label_idx].children[0].color = '#1ed760'


    def on_touch_down(self, touch):
        #304 is shift, 305 is ctrl
        touched_with_right = False
        if touch.button == 'right':
            touched_with_right = True

        if 305 not in self.app.pressed_buttons and 304 not in self.app.pressed_buttons and not touched_with_right:
            self.clear_background(self.canvas.before)
            self.selected = False
            if self.row_number in self.app.displayed_tracks_selected:
                self.app.displayed_tracks_selected.pop(self.row_number)
        if self.collide_point(*touch.pos):
            if touch.is_double_tap and 304 not in self.app.pressed_buttons:
                self.double_tapped()
            if self.app.pressed_buttons == {305}:
                self.selected_with_ctrl_pressed()
            elif self.app.pressed_buttons == {304}:
                self.selected_with_shift_pressed()
            else:
                self.selected_with_no_special_keys_pressed(touched_with_right)
            if touched_with_right:
                self.app.open_right_clicked_track_menu(self, touch)

    def set_apps_last_selected_track(self):
        self.app.last_selected_track = self.row_number

    def double_tapped(self):
        try:
            self.app.spotify.start_playback(context_uri=self.app.selected_playlist['uri'], offset={
                                            'uri': f'spotify:track:{self.spotify_id}'})
            self.app.playing_context = self.app.selected_playlist['uri']
        except KeyError:
            self.app.spotify.start_playback(uris=self.app.rmb_track_menu.uris, offset={
                                            'uri': f'spotify:track:{self.spotify_id}'})
            self.app.playing_context = 'artists_top_tracks'

        self.app.playing_track = self.spotify_id

        try:
            self.children[self.title_label_idx].children[-1].children[0].color = '#1ed760'
        except IndexError:
            self.children[self.title_label_idx].children[0].color = '#1ed760'

        self.app.is_playing = True
        self.app.playing_track_row = self
        Clock.schedule_once(self.app.schedule_clock_update_interface, .1)


    def remove_previous_playing_track(self):
        if self.app.playing_track_row and self.app.playing_track_row is not self:
            self.app.playing_track_row.is_playing = False
            self.app.playing_track_row.row_num_label.opacity = 1
            self.app.playing_track_row.row_num_label.color = '#ffffff'
            self.app.playing_track_row.anim_layout.opacity = 0
            self.app.playing_track_row.add_playback_button(reset_button=True)
            self.app.playing_track_row.button.opacity = 0
            try:
                self.app.playing_track_row.children[self.title_label_idx].children[-1].children[0].color = '#ffffff'
            except IndexError:
                self.app.playing_track_row.children[self.title_label_idx].children[0].color = '#ffffff'

    def get_row_neighbors(self, id):
        neighbors = {}
        if id-1 in self.app.displayed_tracks_selected:
            neighbors['neighbors_from_top'] = self.app.displayed_tracks_selected[id-1]
        if id+1 in self.app.displayed_tracks_selected:
            neighbors['neighbors_from_bot'] = self.app.displayed_tracks_selected[id+1]
        return neighbors

    def row_active(self):
        for layout in self.children:
            for child in layout.children:
                if isinstance(child, AnchorLayout):
                    for label in child.children:
                        if hasattr(label, 'on_leave_color'):
                            if label.on_leave_color:
                                label.color = label.on_enter_color
                else:
                    if hasattr(child, 'on_leave_color'):
                        if child.on_leave_color:
                            child.color = child.on_enter_color

    def clear_background(self, caller):
        caller.clear()
        self.row_inactive()

    def row_inactive(self):
        for layout in self.children:
            for child in layout.children:
                if isinstance(child, AnchorLayout):
                    for label in child.children:
                        if hasattr(label, 'on_leave_color'):
                            if label.on_leave_color:
                                label.color = label.on_leave_color
                else:
                    if hasattr(child, 'on_leave_color'):
                        if child.on_leave_color:
                            child.color = child.on_leave_color


    def check_if_track_is_currently_playing(self):
        try:
            if self.app.playing_track == self.spotify_id and self.app.playing_context == self.app.selected_playlist['uri']:
                if not self.app.playing_track_row:
                    self.app.playing_track_row = self
                    return True
                if self == self.app.playing_track_row:
                    return True
                return False
            return False
        except KeyError:
            if self.app.playing_track == self.spotify_id:
                if not self.app.playing_track_row:
                    self.app.playing_track_row = self
                    return True
                if self == self.app.playing_track_row:
                    return True
                return False
            return False


    def add_playback_button(self, reset_button=False):
        if not hasattr(self, 'button'):
            layout = FloatLayout()
            self.button = MDIconButton(icon='play',
                                       user_font_size='20sp', theme_text_color='Custom', text_color='#ffffff')

        def touched():
            pass
        if self.is_playing:
            if self.app.is_playing:
                self.button.icon = 'pause'
                touched = self.pause_button_callback
            else:
                self.button.icon = 'play'
                touched = self.resume_button_callback
        else:
            self.button.icon = 'play'
            touched = self.play_new_button_callback
        if reset_button:
            self.button.icon = 'play'
            touched = self.play_new_button_callback

        self.button.on_touch_up = touched
        self.button.opacity = 1
        if not self.get_row_playback_button():
            layout.bind(pos=lambda obj, pos: setattr(
                self.button, 'pos', [pos[0]-18, pos[1]+8]))
            layout.add_widget(self.button)
            self.button.opacity = 0
            self.children[-1].add_widget(layout)
        self.opacity = 1
        self.height = 55

    def pause_track_playback(self):
        self.button.icon = 'play'
        self.row_num_label.color = '#1ed760'
        self.is_playing = True
        self.button.on_touch_up = self.resume_button_callback
        self.button.color = '#1ed760'
        self.row_num_label.color='#1ed760'

    def resume_track_playback(self):
        self.button.icon = 'pause'
        self.is_playing = True
        self.button.on_touch_up = self.pause_button_callback
        self.buton = '#1ed760'
        self.row_num_label.color='#1ed760'

    def pause_button_callback(self, touch):
        if self.button.collide_point(*touch.pos) and touch.button == 'left':
            self.app.pause_playback()
            self.app.is_playing = False
            self.is_playing = False
            Clock.unschedule(self.app.clock)
            self.app.playing_track_row = self
            self.app.spotify.pause_playback(
                device_id=self.app.device['id'])

    def resume_button_callback(self, touch):
        if self.button.collide_point(*touch.pos) and touch.button == 'left':
            self.app.resume_playback()
            self.remove_previous_playing_track()
            self.is_playing = True
            self.app.playing_track_row = self
            self.app.spotify.start_playback(
                device_id=self.app.device['id'])
            self.button.opacity = 1
            Clock.schedule_once(
                self.app.schedule_clock_update_interface, 0)

    def play_new_button_callback(self, touch):
        if self.button.collide_point(*touch.pos) and touch.button == 'left':
            self.remove_previous_playing_track()
            self.app.playing_track_row = self
            self.app.resume_playback()
            self.is_playing = True
            self.app.is_playing = True
            self.double_tapped()

    def add_currently_playing_animated_icon(self):
        self.anim_layout = FloatLayout()
        self.anim_layout.canvas.clear()
        self.bars = [
            Rectangle(
                size=[2, 2]),
            Rectangle(
                size=[2, 15]),
            Rectangle(
                size=[2, 7]),
            Rectangle(
                size=[2, 11]),
            Rectangle(
                size=[2, 6]),
        ]

        self.anim_layout.canvas.add(Color(*get_color_from_hex('#1ed760')))
        for idx, rectangle in enumerate(self.bars):
            self.anim_layout.canvas.add(rectangle)
            anim = Animation(size=[2, 16], d=0.3+idx/10) + \
                Animation(size=[2, 0], d=0.31+idx/12)
            anim.repeat = True
            anim.start(rectangle)

        def bind_bars_pos(obj, pos):
            for idx, rectangle in enumerate(self.bars):
                rectangle.pos = [pos[0]-4+3*idx, pos[1]+22]
        self.anim_layout.bind(pos=bind_bars_pos)
        self.children[-1].add_widget(self.anim_layout)

    def display_row_num(self):
        self.row_num_label = self.get_row_numb_label()

    def set_displayed_row_num(self, num):
        self.displayed_row_num = num


    def selected_with_shift_pressed(self):
        row_nums = set()
        if self.app.last_selected_track < self.row_number:
            row_nums = {row_num for row_num in range(
                self.app.last_selected_track, self.row_number+1)}
        else:
            row_nums = {row_num for row_num in range(
                self.row_number, self.app.last_selected_track+1)}

        tracks = [children for children in self.app.tracks_table if children.row_number in row_nums]
        for track in tracks:
            track.selected = True
            self.app.displayed_tracks_selected[track.row_number] = track

        for track in tracks:
            track.paint_background(
                color='#5a5a5a')

    def selected_with_ctrl_pressed(self):
        neighbors = self.get_row_neighbors(self.row_number)
        if not self.selected:
            self.selected = True
            self.app.displayed_tracks_selected[self.row_number] = self
            self.set_apps_last_selected_track()
            self.paint_background(
                color='#5a5a5a')
        else:
            self.selected = False
            self.clear_background(self.canvas.before)
            self.app.displayed_tracks_selected.pop(self.row_number)
        if 'neighbors_from_top' in neighbors:
            neighbors['neighbors_from_top'].paint_background(
                color='#5a5a5a')
        if 'neighbors_from_bot' in neighbors:
            neighbors['neighbors_from_bot'].paint_background(
                color='#5a5a5a')

    def selected_with_no_special_keys_pressed(self, touched_with_rmb):
        if not touched_with_rmb:
            self.app.displayed_tracks_selected = {}
            self.selected = True
            self.app.displayed_tracks_selected[self.row_number] = self
            self.set_apps_last_selected_track()
        else:
            if self.selected:
                return
            tracks = [children for children in self.app.tracks_table if children.row_number in self.app.displayed_tracks_selected]
            for track in tracks:
                track.selected = False
                self.clear_background(track.canvas.before)
                track.rect = None
            self.app.displayed_tracks_selected = {}
            self.selected = True
            self.app.displayed_tracks_selected[self.row_number] = self
            self.set_apps_last_selected_track()
        self.paint_background(
            color='#5a5a5a')

    def paint_background(self, color='#2a2a2a', top_radius=5, bot_radius=5):
        self.row_active()
        self.canvas.before.clear()
        neighbors = self.get_row_neighbors(self.row_number)

        if 'neighbors_from_top' in neighbors:
            top_radius = 0
        if 'neighbors_from_bot' in neighbors:
            bot_radius = 0
        with self.canvas.before:
            Color(*get_color_from_hex(color))
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=[self.size[0], self.size[1]+1],
                # Adding one to height to compensate for layout's spacing,
                # which is required to prevent selecting both songs while pressing on pixel between.
                radius=[(top_radius, top_radius), (top_radius, top_radius),
                        (bot_radius, bot_radius), (bot_radius, bot_radius)],
            )
            self.bind(pos=lambda obj, pos: setattr(
                self.rect, "pos", pos))
            self.bind(size=lambda obj, size: setattr(
                self.rect, "size", [size[0], size[1]+1]))

    def on_enter(self, *args):
        '''The method will be called when the mouse cursor
        is within the borders of the current widget.'''
        self.button.opacity = 1
        self.row_num_label = self.get_row_numb_label()
        self.row_num_label.opacity = 0
        self.anim_layout.opacity = 0
        self.row_active()
        if not self.selected:
            self.paint_background()

    def get_row_numb_label(self):
        for child in self.children[-1].children:
            if isinstance(child, Label):
                return child

    def get_row_playback_button(self):
        for child in self.children[-1].children:
            if len(child.children) > 0:
                if isinstance(child.children[0], MDIconButton):
                    return child.children[0]

    def on_leave(self, *args):
        '''The method will be called when the mouse cursor goes beyond
        the borders of the current widget.'''
        self.button.opacity = 0
        if not self.is_playing:
            self.row_num_label.opacity = 1
        else:
            if self.app.is_playing:
                self.anim_layout.opacity = 1
            else:
                self.row_num_label.opacity = 1
                self.row_num_label.color = '#1ed760'
                self.anim_layout.opacity = 0

        if not self.selected:
            self.clear_background(self.canvas.before)
