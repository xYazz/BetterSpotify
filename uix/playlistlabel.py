import sys
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivymd.uix.behaviors import HoverBehavior
from kivymd.theming import ThemableBehavior

class PlaylistLabel(Label, ThemableBehavior, HoverBehavior):
    id = None
    selected = False

    def __init__(self, id, snapshot_id, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.snapshot_id = snapshot_id
        self.app = App.get_running_app()

    def on_parent_resize(self):
        self.size = self.parent.size
        self.texture_update()
        self.text_size = (self.size[0], None)

    def on_touch_down(self, touch):
        """Fired when PlaylistLabel is clicked."""
        # Apply to all PlaylistLabel instances.
        self.color = "#b3b3b3"
        self.selected = False
        if self.collide_point(*touch.pos):
            # Apply to clicked PlaylistLabel instance.
            if touch.is_double_tap:
                self.is_double_tapped()
            # Mark playlist as currently selected.
            self.color = "#ffffff"
            self.selected = True
            try:
                if self.app.selected_playlist['id'] != self.id:
                    self.get_playlist()
            except TypeError:
                    self.get_playlist()

            self.app.resize_main_panel()

    def get_playlist(self):
        if self.id not in self.app.selected_playlists_widgets:
            self.app.changed_context_to_playlist(self.id)
            self.app.selected_playlists_tables[self.id]=self.app.selected_playlist
            self.app.selected_playlists_widgets[self.id]=self.app.screen.ids.main_screen.children[::-1]
        else:
            self.app.screen.ids.main_screen.clear_widgets()
            self.app.tracks_table = self.app.selected_playlists_tables[self.id]
            for widget in self.app.selected_playlists_widgets[self.id]:
                self.app.screen.ids.main_screen.add_widget(widget)
            self.app.selected_playlist = self.app.selected_playlists[self.snapshot_id]

    def is_double_tapped(self):
        if self.app.playing_context[-len(self.id):] == self.id:
            # Apply if clicked playlist was already selected as playing context.
            # Different results if player has to be resumed or paused.
            self.play_playlist()
            return
        # Play selected playlist.
        self.app.spotify.start_playback(
            context_uri=self.app.selected_playlist['uri'])
        self.app.current_playback()
        self.app.resume_playback()
        self.app.playing_context = self.app.selected_playlist['uri']
        Clock.schedule_once(
            self.app.schedule_clock_update_interface, .2)
        Clock.schedule_once(
            self.show_playing_track_in_context_table, .1)

    def play_playlist(self):
        if not self.app.is_playing:
            # Resume player.
            self.app.spotify.start_playback(
            device_id=self.app.device['id'])
            self.app.current_playback()
            self.app.resume_playback()
            return
        # Pause player.
        self.app.spotify.pause_playback(
        device_id=self.app.device['id']
        )
        self.app.current_playback()
        self.app.pause_playback()
        Clock.unschedule(self.app.clock)

    def show_playing_track_in_context_table(self, interval):
        """ 
        Mark currently playing track as playing in the context table.
        Currently playing track row has playing animation and it's title color is green.
        """
        playback = self.app.spotify.current_playback()
        for track in self.app.tracks_table:
            if track.spotify_id == playback['item']['id']:
                Clock.schedule_once(track.load_playing_track, .1)
                try:
                    track.anim_layout.opacity = 1
                except AttributeError:
                    track.add_playing_anim(1)
                try:
                    track.button.opacity = 0
                except AttributeError:
                    pass
                track.remove_previous_playing_track()
                track.is_playing = True
                self.app.playing_track_row = track

    def on_enter(self, *args):
        if not self.app.playlist_panel_resizing:
            self.color = "#ffffff"

    def on_leave(self, *args):
        if not self.selected:
            self.color = "#b3b3b3"