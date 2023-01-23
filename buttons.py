
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.uix.button import MDIconButton, MDTooltip
from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import HoverBehavior, MagicBehavior
from uix.tracktablerow import TrackTableRow
from kivy.animation import Animation
from kivy.properties import (
    OptionProperty,
)


class PlaybackButton(MDTooltip, MDIconButton,  ThemableBehavior, HoverBehavior):
    selected = False
    id = None
    clicked = False
    events = {}
    detect_visible = True
    tooltip_display_delay = 1
    tooltip_text_color = '#FFFFFF'
    tooltip_bg_color = '#242424'
    target = OptionProperty(None,
                            options=['context', None])
    upscale_anim = Animation(user_font_size=69, d=.1)
    downscale_anim = Animation(user_font_size=68, d=.1)

    def __init__(self, app=None, selected=None, *args, **kwargs):
        super(PlaybackButton, self).__init__(**kwargs)
        self.app = app
        self.events = {'Enable shuffle': self.enable_shuffle_event,
                       'Disable shuffle': self.disable_shuffle_event,
                       'Previous': self.previous_track_event,
                       'Play': self.play_track_event,
                       'Pause': self.pause_track_event,
                       'Next': self.next_track_event,
                       'Enable repeat': self.enable_repeat_event,
                       'Enable repeat one': self.enable_repeat_one_event,
                       'Disable repeat': self.disable_repeat_event,
                       'Save to Your Library': self.save_to_your_library_event,
                       'Remove from Your Library': self.remove_from_your_library_event,
                       }
        Clock.schedule_once(self.init_after_interval, .1)
        
    def init_after_interval(self, interval):
        if self.tooltip_text in ('Play',
                                 'Pause',
                                 'Remove from Your Library',):
            self.selected = True
            if self.tooltip_text in ('Play',
                                 'Pause'):
                if not self.target:
                    self.app.playback_button = self
    def on_enter(self, *args):
        if not self.selected and not self.target:
            self.theme_text_color = "Primary"
        if self.target == 'context' and self.tooltip_text in ('Play', 'Pause'):
            self.upscale_anim.start(self)
        super().on_enter()

    def on_leave(self, *args):
        self.remove_tooltip()
        super().on_leave(*args)
        if not self.selected and not self.target:
            self.theme_text_color = "Secondary"
        if self.target == 'context' and self.tooltip_text in ('Play', 'Pause'):
            
            self.downscale_anim.start(self)

    def on_release(self):
        if self.tooltip_text and not self.target and not self.selected:
            self.theme_text_color = "Secondary"
        self.events[self.tooltip_text]()
        if self.target == 'context' and self.tooltip_text in ('Play', 'Pause'):
            self.downscale_anim.start(self)
        super().on_release()

    def change_state(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.remove_tooltip()

    def enable_shuffle_event(self):
        self.change_state(tooltip_text='Disable shuffle',
                          theme_text_color="Custom",
                          text_color='#1ed760',
                          selected=True)
        self.app.spotify.shuffle(True, device_id=self.app.device['id'])

    def disable_shuffle_event(self):
        self.change_state(tooltip_text='Enable shuffle',
                          theme_text_color="Secondary",
                          selected=False)
        self.app.spotify.shuffle(
            False, device_id=self.app.device['id'])

    def previous_track_event(self):
        self.app.spotify.previous_track(
            device_id=self.app.device['id'])
        Clock.schedule_once(self.app.schedule_clock_update_interface, .05)
        Clock.schedule_once(self.show_playing_track_in_context_table, .15)
        Clock.schedule_once(self.show_playing_track_in_context_table, .35)
        self.remove_tooltip()

    def play_track_event(self):
        self.app.is_playing = True
        self.app.resume_playback()
        Clock.unschedule(self.app.clock)
        if not self.target:
            self.app.spotify.start_playback(
                device_id=self.app.device['id'])
        elif self.target == 'context':
            if self.app.playing_context == self.app.selected_playlist['uri']:
                self.app.spotify.start_playback(
                    device_id=self.app.device['id'])
                return
            self.app.spotify.start_playback(
                context_uri=self.app.selected_playlist['uri'])

            self.app.current_playback()
            Clock.schedule_once(self.show_playing_track_in_context_table, .25)
            self.app.playing_context = self.app.selected_playlist['uri']

        Clock.schedule_once(self.app.schedule_clock_update_interface, .05)

    def show_playing_track_in_context_table(self, interval):
        
        playback = self.app.spotify.current_playback()
        for track in self.app.tracks_table:
            if track.spotify_id==playback['item']['id']:
                track.remove_previous_playing_track()
                Clock.schedule_once(track.load_playing_track, 0)
                track.anim_layout.opacity=1
                self.app.playing_track_row=track

    def start_updating_interface(self, interval):

        self.app.clock = Clock.schedule_interval(self.app.update_interface, 1)

    def update_playing_context(self, interval):
        self.app.playing_track = self.app.current_track['item']['id']
        self.app.playing_context = self.app.current_track['context']['uri']
        self.app.playing_track_row_number = None

    def pause_track_event(self):
        self.app.is_playing = False
        self.app.pause_playback()
        Clock.unschedule(self.app.clock)
        self.app.spotify.pause_playback(
            device_id=self.app.device['id'])

    def enable_repeat_event(self):
        self.change_state(tooltip_text='Enable repeat one',
                          theme_text_color="Custom",
                          text_color='#1ed760',
                          selected=True)
        self.app.spotify.repeat(
            'context', device_id=self.app.device['id'])

    def enable_repeat_one_event(self):
        self.change_state(tooltip_text='Disable repeat',
                          icon='repeat-once',
                          theme_text_color="Custom",
                          text_color='#1ed760',
                          selected=True)
        self.app.spotify.repeat(
            'track', device_id=self.app.device['id'])

    def disable_repeat_event(self):
        self.change_state(tooltip_text='Enable repeat',
                          icon='repeat',
                          theme_text_color="Secondary",
                          selected=False)
        self.app.spotify.repeat('off', device_id=self.app.device['id'])

    def save_to_your_library_event(self):
        self.change_state(tooltip_text='Remove from Your Library',
                          icon='heart',
                          theme_text_color='Custom',
                          text_color='#1ed760',
                          selected=True)
        self.app.spotify.current_user_saved_tracks_add(
            [self.app.current_track['item']['id'], ])

    def remove_from_your_library_event(self):
        self.change_state(tooltip_text='Save to Your Library',
                          icon='heart-outline',
                          theme_text_color="Secondary",
                          selected=False)
        self.app.spotify.current_user_saved_tracks_delete(
            [self.app.current_track['item']['id'], ])

    def next_track_event(self):
        self.app.spotify.next_track(device_id=self.app.device['id'])
        Clock.schedule_once(self.app.schedule_clock_update_interface, .05)
        Clock.schedule_once(self.show_playing_track_in_context_table, .15)
        Clock.schedule_once(self.show_playing_track_in_context_table, .35)
        self.remove_tooltip()
