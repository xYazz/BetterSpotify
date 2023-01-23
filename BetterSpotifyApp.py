from email.policy import default
import itertools
import pyperclip
import pprint
from exceptions import NoTrackAvailable, NoTrackAvailableHandler
from kivy.base import ExceptionManager
from spotipy.oauth2 import SpotifyOAuth
from kivy.loader import Loader
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.theming import ThemableBehavior
from kivymd.uix.floatlayout import FloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDTooltip
from kivymd.uix.progressbar import MDProgressBar
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.behaviors.elevation import RectangularElevationBehavior
from kivy.graphics import Line, Color, Rectangle
from kivymd.uix.slider import MDSlider
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivymd.font_definitions import theme_font_styles
from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivymd.uix.label import MDLabel
from kivymd.uix.behaviors import HoverBehavior, MagicBehavior
from uix.dropdownmenu import (
    DropDownMenuTrackWithMousePos,
    RightMouseButtonListItem,
    RightMouseButtonListDivider
)
from kivy.uix.scrollview import ScrollView
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stacklayout import StackLayout
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivy.uix.image import AsyncImage
from kivy.app import App
from kivy.metrics import dp
from kivy.lang.builder import Builder
from kivy.uix.slider import Slider
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import mainthread, Clock
from kivy.event import EventDispatcher
from kivy.utils import get_color_from_hex
from myslider import MyMDSlider
from buttons import PlaybackButton
from kivy.effects.scroll import ScrollEffect
from functools import partial
from decorators.onhover import on_hover
import spotipy
import discor
from kivy.uix.splitter import SplitterStrip
import multiprocessing
from textwrap import shorten
from time import sleep
from tkinter import Canvas
import datetime
import asyncio
import threading
import sys
from turtle import title, width

from kivy.config import Config
from kivymd.uix.list import BaseListItem

from layout_factories.app_utils.app_utils import to_timer
from layout_factories.context_table_layouts import get_album_tracks_table, get_artist_top_tracks_table, get_song_radio_table_track, get_playlist_tracks_table
from layout_factories.rmb_menu_layouts import set_rmb_menu_items

from uix.currenttracklayout import CurrentTrackLayout
from uix.fadingsnackbar import FadingSnackbar
from uix.playlistlabel import PlaylistLabel
from uix.tracktablelabel import TrackTableLabel
from uix.tracktablerow import TrackTableRow

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


class BetterSpotifyApp(MDApp):
    
    selected_playlists = {}
    selected_playlists_widgets = {}
    selected_playlists_tables = {}
    discord = None
    is_playing = False
    device = None
    progress = None
    progress_bar = None
    left_timer = None
    right_timer = None
    current_track = None
    playing_track_row = None
    playback_button = None
    progress_in_mins = None
    uris = []
    tracks_table = []
    tracks_table_widget = None
    current_track_flag = ''
    playlist_panel_resizing = False
    remaining_in_mins = None
    slider_is_hovered = None
    screen = None
    current_user = None
    progressbar_is_active = False
    clock = None
    playing_context = None
    playing_track = None
    last_selected_track = None
    pressed_buttons = set()
    displayed_tracks_selected = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__selected_playlist = None
        self.event_loop_worker = None
        ExceptionManager.add_handler(NoTrackAvailableHandler())
        self.init_font_styles()
        self.set_client_scope()
        self.current_user = self.spotify.current_user()
        self.get_playback_info(0)
        self.device = self.spotify.devices()['devices'][0]
        self.current_playback()
        Window.bind(on_motion=self.scroll)
        Window.bind(on_key_up=self._keyup)
        Window.bind(on_key_down=self._keydown)



    @property
    def selected_playlist(self):
        return self.__selected_playlist

    @selected_playlist.setter
    def selected_playlist(self, playlist):
        if not playlist['snapshot_id'] in self.selected_playlists:
            self.selected_playlists[playlist['snapshot_id']]=playlist
            self.__selected_playlist = playlist
        else:
            self.__selected_playlist = self.selected_playlists[playlist['snapshot_id']]

    def _keyup(self, *args, **kwargs):
        """
        Removes saved keyboard keys that got released.
        """
        if args[1] in self.pressed_buttons:
            self.pressed_buttons.remove(args[1])

    def _keydown(self, *args):
        """
        Saves keyboards pressed, to detect shortcuts and
        if needed change certain functionalities behavior.
        """
        if args[1] not in self.pressed_buttons:
            self.pressed_buttons.add(args[1])
            if self.pressed_buttons == {305, 97}:
                children_list = self.tracks_table
                if children_list:
                    for children in children_list:
                        if isinstance(children, TrackTableRow):
                            self.displayed_tracks_selected[children.row_number] = children
                            children.selected = True
                            children.paint_background(
                                color='#5a5a5a', top_radius=0, bot_radius=0)
                    children_list[0].paint_background(
                        color='#5a5a5a', top_radius=0, bot_radius=5)
                    children_list[-1].paint_background(
                        color='#5a5a5a', top_radius=5, bot_radius=0)

    def set_client_scope(cls):
        scope = "user-library-read,user-modify-playback-state,playlist-modify-public,playlist-modify-private,playlist-read-private,user-read-recently-played,user-read-playback-state,user-library-modify,user-library-read"
        cls.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    def scroll(self, window, etype, me):
        pass

    def build(self):
        Window.minimum_width, Window.minimum_height = (800, 600)
        Loader.loading_image = 'loading.png'
        self.theme_cls.theme_style = "Dark"
        self.screen = Builder.load_file('kv_layout/kv_layout.kv')
        self.get_progress_slider()
        try:
            self.get_current_track(1)
        except NoTrackAvailable:
            pass
        self.get_user_playlists()
        self.resize_playlists_panel()
        self.playlist_panel_resizing_off()
        # Window.borderless = True
        return self.screen

    def init_font_styles(self):

        theme_font_styles.append('Arialbd')
        self.theme_cls.font_styles["Arialbd"] = [
            "arialbd",
            13,
            False,
            -5,
        ]

    def pause_playback(self):
        self.is_playing = False
        try:
            self.playing_track_row.pause_track_playback()
            self.playing_track_row.button.opacity=0
            self.playing_track_row.row_num_label.opacity=1
            self.playing_track_row.anim_layout.opacity=0
        except AttributeError:
            print('error')
        try:
            self.playback_button.change_state(tooltip_text='Play',
                                              icon='play-circle')
        except AttributeError:
            pass
        try:
            self.context_playback_button.change_state(tooltip_text='Play',
                                                      icon='play-circle')
        except AttributeError:
            pass

    def resume_playback(self):
        self.is_playing = True
        try:
            self.playing_track_row.resume_track_playback()
        except AttributeError:
            pass
        try:
            self.playback_button.change_state(tooltip_text='Pause',
                                              icon='pause-circle')
        except AttributeError:
            pass
        try:
            self.context_playback_button.change_state(tooltip_text='Pause',
                                                      icon='pause-circle')
        except AttributeError:
            pass

    def on_start(self, **kwargs):
        print(self.spotify.artist('6sFIWsNpZYqfjUpaCgueju'))

    def update_interface(self, interval):
        if self.is_playing:
            try:
                thr = threading.Thread(
                    target=self.get_playback_info, args=(0,))
                thr.start()
                self.get_current_track(0)
            except NoTrackAvailable:
                print('NoTrackAvailable error')
                pass
            if not self.progressbar_is_active:
                self.current_track['progress_ms'] += 1000
                self.get_progress_slider()
            self.get_remaining_timer()
            self.get_progress_timer()

    def get_progress_slider(self):
        if not self.left_timer:
            seconds = self.progress_in_mins[1]
            self.left_timer = MDLabel(text=f'[size=11]{self.progress_in_mins[0]}:{seconds}[/size]',
                                      size_hint=(.07, 1),
                                      pos_hint={"center_x": 0,
                                                "center_y": .12},
                                      markup=True,
                                      theme_text_color="Secondary")
            self.screen.ids.playback_progress.add_widget(self.left_timer)
        if not self.right_timer:
            seconds = self.remaining_in_mins[1]
            self.right_timer = MDLabel(text=f'[size=11]{self.remaining_in_mins[0]}:{seconds}[/size]',
                                       size_hint=(.07, 1),
                                       pos_hint={"center_x": 1,
                                                 "center_y": .12},
                                       markup=True,
                                       theme_text_color="Secondary")
            self.screen.ids.playback_progress.add_widget(self.right_timer)
        if not self.progress_bar:
            try:
                val = self.current_track['progress_ms']
                max_val = self.current_track['item']['duration_ms']
            except TypeError:
                val = 0
                max_val = 100
            self.progress_bar = MyMDSlider(value=val,
                                           size_hint=(1, .2),
                                           pos_hint={"center_x": .5,
                                                     "center_y": .12},
                                           min=0,
                                           step=1000,
                                           max=max_val,
                                           detect_visible=False
                                           )
            self.screen.ids.playback_progress.add_widget(self.progress_bar)

        seconds = self.progress_in_mins[1]
        self.left_timer.text = f'[size=11]{self.progress_in_mins[0]}:{seconds}[/size]'
        seconds = self.remaining_in_mins[1]
        self.right_timer.text = f'[size=11]{self.remaining_in_mins[0]}:{seconds}[/size]'
        try:
            val = self.current_track['progress_ms']
        except TypeError:
            val = 0
        self.progress_bar.value = val

    def get_remaining_timer(self):
        progress = self.current_track['progress_ms']
        try:
            duration = self.current_track['item']['duration_ms']
        except TypeError:
            duration = 0
        remaining = duration - progress
        self.remaining_in_mins = to_timer(remaining)

    def get_progress_timer(self):
        progress = self.current_track['progress_ms']
        self.progress_in_mins = to_timer(progress-1000)



    def get_playback_info(self, interval):
        track = self.spotify.currently_playing()
        self.current_track = track
        self.is_playing = track['is_playing']
        if self.is_playing:
            if self.clock:
                Clock.unschedule(self.clock)
            self.clock = Clock.schedule_interval(self.update_interface, 1)
        track = track['item']
        self.get_progress_timer()
        self.get_remaining_timer()
        try:
            self.current_track['artists'] = ', '.join(
                [artist['name'] for artist in track['artists']])
        except TypeError:
            self.current_track['artists'] = ''

    def open_devices_menu(self):
        items = self.spotify.devices()['devices']
        menu_items = [
            {
                "text": item['name'],
                "viewclass": "OneLineListItem",
                "on_release": lambda x=item: self.devices_menu_callback(x),
            } for item in items
        ]
        self.devices_menu = MDDropdownMenu(
            caller=self.screen.ids.button,
            items=menu_items,
            width_mult=3,
            max_height=50*len(items)

        )
        self.devices_menu.open()

    def devices_menu_callback(self, device):
        self.device = device
        self.devices_menu.dismiss()


    def share_song_link(self):
        link = self.displayed_tracks_selected[next(
            iter(self.displayed_tracks_selected))].song_link
        pyperclip.copy(link)
        self.rmb_track_menu.dismiss()
        self.prompt_snackbar(text="Link copied to clipboard", width=188)

    def remove_from_playlist(self):
        items = [item.spotify_id for row_num,
                 item in self.displayed_tracks_selected.items()]

        self.spotify.playlist_remove_all_occurrences_of_items(
            self.selected_playlist['id'], items=items)
        deleted_tracks = set(
            row for row_num, row in self.displayed_tracks_selected.items())
        for track_row in self.tracks_table[:]:
            if track_row in deleted_tracks:
                self.tracks_table.remove(track_row)
                self.tracks_table_widget.remove_widget(track_row)
        for idx, track_row in enumerate(self.tracks_table_widget.children[::-1]):
            if isinstance(track_row, TrackTableRow):
                for child in track_row.children[-1].children:
                    if isinstance(child, Label):
                        child.text = str(idx)
        self.rmb_track_menu.dismiss()

    def save_or_remove_from_saved_songs(self, ids, remove):
        if remove:
            self.spotify.current_user_saved_tracks_delete(ids)
        else:
            self.spotify.current_user_saved_tracks_add(ids)
        self.rmb_track_menu.dismiss()

    def add_tracks_to_queue(self):
        for id, track in self.displayed_tracks_selected.items():
            self.spotify.add_to_queue(track.spotify_id)
        self.rmb_track_menu.dismiss()
        self.prompt_snackbar(text="Added to queue", width=188)

    def prompt_snackbar(self, text=None, width=None):
        self.fading_queue_snackbar = FadingSnackbar(
            text=text,
            snackbar_x=Window.width/2 - width/2,
            snackbar_y="100dp",
            size_hint=[None, None],
            font_size='14sp',

            minimum_height=40,
            size=[width, 44],
            bg_color=[0.18039215686, 0.46666666666, 0.81568627451]
        )
        self.fading_queue_snackbar.ids.text_bar.font_style = 'Arialbd'
        self.fading_queue_snackbar.ids.text_bar.halign = 'center'
        self.fading_queue_snackbar.open()

    def remove_from_dict(self, key_to_remove, dict_to_remove_from):
        return_dict = {}
        for key, value in dict_to_remove_from.items():
            if key != key_to_remove:
                if isinstance(value, dict):
                    return_dict[key] = self.remove_from_dict(
                        key_to_remove, value)
                elif isinstance(value, list):

                    return_dict[key] = self.remove_from_list(
                        key_to_remove, value)
                else:
                    return_dict[key] = value
        return return_dict

    def remove_from_list(self, key_to_remove, list_to_remove_from):
        return_list = []
        for item in list_to_remove_from:
            if item is not key_to_remove:
                if isinstance(item, dict):
                    return_list.append(
                        self.remove_from_dict(key_to_remove, item))
                elif isinstance(item, list):
                    return_list.append(
                        self.remove_from_list(key_to_remove, item))
        return return_list

    def go_to_song_radio(self):
        self.rmb_track_menu.dismiss()

        if len(self.displayed_tracks_selected) > 0:
            arr = [track.spotify_id for id,
                   track in self.displayed_tracks_selected.items()]

            new_playlist = self.spotify.recommendations(seed_tracks=arr)

            self.uris = [item['uri'] for item in new_playlist['tracks']]
            self.set_playlist_details()
            self.create_context_playback_panel(self.selected_playlist['uri'])
            
            tracks, tracks_widget = get_song_radio_table_track(new_playlist['tracks'])
            self.tracks_table = tracks
            self.screen.ids.main_screen.add_widget(tracks_widget)

    def open_right_clicked_track_menu(self, caller=None, touch=None):
        set_rmb_menu_items()

        self.rmb_track_menu.caller = caller
        self.rmb_track_menu.touch = touch
        self.rmb_track_menu.items = self.rmb_menu_items
        self.rmb_track_menu.open()

    def get_add_to_playlist_dropdown_items(self):
        items = [
            {
                "text": '',
                "viewclass": "RightMouseButtonSearchField",
                "divider": None,
                "divider_color": "#ffffff",
                "height": 39,
                "on_release": lambda: print('create playlist'),
            },
            {
                "text": 'Create playlist',
                "viewclass": "RightMouseButtonNestedListItem",
                "divider": None,
                "divider_color": "#ffffff",
                "height": 39,
                "on_release": lambda: print('create playlist'),
            },
            {
                "text": '',
                "viewclass": "RightMouseButtonListDivider",
                "divider": None,
                "divider_color": "#ffffff",
                "height": 1,
                "on_release": self.right_click_call_back,
            }, ]
        longest_playlist_name = 0
        for item in self.playlists:
            longest_playlist_name = max(
                longest_playlist_name, len(item['name']))
            items.append(
                {
                    "text": item['name'],
                    "viewclass": "RightMouseButtonNestedListItem",
                    "divider": None,
                    "divider_color": "#ffffff",
                    "height": 39,
                    "on_release": lambda: print(item['name']),
                }
            )
        return items, longest_playlist_name

    def open_nested_rmb_menu(self, caller=None, position=None, row_width=None, hor_growth=None):

        rmb_nested_menu_items, longest_playlist_name = self.get_add_to_playlist_dropdown_items()
        touch = [position[0]+row_width, position[1]]
        if position[0]+row_width+longest_playlist_name*7.5 >= Window.width:
            touch = [position[0]-longest_playlist_name*7.5, position[1]]
            if hor_growth == 'left':
                touch = [position[0]-row_width -
                         longest_playlist_name*7.5, position[1]]
        if touch[0] < 0:
            touch[0] = 0
        self.rmb_nested_menu = DropDownMenuTrackWithMousePos(
            row_width=longest_playlist_name*7.5,
            touch=touch,
            caller=self.rmb_track_menu,
            items=rmb_nested_menu_items,
            background_color='#282828',
            elevation=16,
            radius=[dp(4), dp(4), dp(4), dp(4)],
            max_height=440
        )
        self.rmb_nested_menu.menu.scroll_wheel_distance = 60
        self.rmb_nested_menu.menu.bar_width = 16
        self.rmb_nested_menu.menu.scroll_distance = 60
        self.rmb_nested_menu.menu.effect_cls = ScrollEffect
        self.rmb_nested_menu.menu.scroll_type = ['bars']
        self.rmb_nested_menu.menu.bar_margin = 0
        self.rmb_nested_menu.open()

    def right_click_call_back(self):
        self.rmb_track_menu.dismiss()
        print('right_clicked')

    def current_playback(self):
        out_playback = self.spotify.current_playback()
        self.playing_track = out_playback['item']['id']
        try:
            self.playing_context = out_playback['context']['uri']
        except TypeError:
            self.playing_context = None
        playback = out_playback['item']
        data = {
            'assets': {
                # 'large_image': 'mp:'+playback['album']['images'][0]['url'],
                'large_text': playback['album']['name']},
            'state': [artist['name'] for artist in playback['album']['artists']][0],
            'flags': 48,
            'details': playback['name'],
            'timestamps': {
                'start': out_playback['timestamp']
            }
        }
        return data

    def connect_to_discord(self):
        if not self.discord:
            self.discord = discor.DiscordClient()

        playback = self.current_playback()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.discord.change_status(**playback))
        loop.close()

    def connect_to_discord2(self):
        if not self.discord:
            self.discord = discor.DiscordClient()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.discord.change_status())
        loop.close()

    def clear_discord_status(self,):
        if not self.discord:
            self.discord = discor.DiscordClient()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.discord.clear_status())
        loop.close()

    def rmb_go_to_album_page(self):
        self.rmb_menu_items = None
        self.rmb_track_menu.dismiss()
        self.rmb_track_menu = None
        if len(self.displayed_tracks_selected) == 1:
            item = self.displayed_tracks_selected[next(
                iter(self.displayed_tracks_selected))]
            self.selected_playlist = self.spotify.album(item.album_id)
            self.get_album_details()

    def go_to_album_page(self, id):
        self.selected_playlist = self.spotify.album(id)
        self.get_album_details()

    def get_album_details(self):
        self.set_playlist_details()
        tracks, tracks_widget =get_album_tracks_table(
            self.selected_playlist['tracks']['items'])
        self.tracks_table = tracks
        self.screen.ids.main_screen.add_widget(tracks_widget)

    def rmb_go_to_artist_page(self):
        self.rmb_menu_items = None
        self.rmb_track_menu.dismiss()
        self.rmb_track_menu = None
        if len(self.displayed_tracks_selected) == 1:
            item = self.displayed_tracks_selected[next(
                iter(self.displayed_tracks_selected))]
            self.selected_playlist = self.spotify.artist_top_tracks(item.artists_ids[0])
            self.uris = [item['uri'] for item in self.selected_playlist['tracks']]
            self.set_artist_details(item.artists_ids[0])
            tracks, tracks_widget =get_artist_top_tracks_table(
                self.selected_playlist['tracks'])
            self.tracks_table = tracks
            self.screen.ids.main_screen.add_widget(tracks_widget)

    def go_to_artist_page(self, id):
        self.selected_playlist = self.spotify.artist_top_tracks(id)
        self.uris = [item['uri'] for item in self.selected_playlist['tracks']]
        self.set_artist_details(id)
        tracks, tracks_widget =get_artist_top_tracks_table(
            self.selected_playlist['tracks'])
        self.tracks_table = tracks
        self.screen.ids.main_screen.add_widget(tracks_widget)

    def changed_context_to_playlist(self, playlist_id):
        self.selected_playlist = self.spotify.playlist(playlist_id)
        self.set_playlist_details()
        self.create_context_playback_panel(self.selected_playlist['uri'])
        trigger = Clock.create_trigger(self.get_tracks)
        trigger()
        # tracks, tracks_widget = get_playlist_tracks_table(
        #     self.selected_playlist['tracks']['items'])
        # self.tracks_table = tracks
        # self.selected_playlists_tables[id]=tracks
        # self.screen.ids.main_screen.add_widget(tracks_widget)
        
    def get_tracks(self, iter):
        tracks, tracks_widget = get_playlist_tracks_table(
            self.selected_playlist['tracks']['items'])
        self.tracks_table = tracks
        self.selected_playlists_tables[self.selected_playlist['id']]=tracks
        self.screen.ids.main_screen.add_widget(tracks_widget)
        
        self.selected_playlists_tables[self.selected_playlist['id']]=self.selected_playlist
        self.selected_playlists_widgets[self.selected_playlist['id']]=self.screen.ids.main_screen.children[::-1]
    def create_context_playback_panel(self, context_uri):
        panel = StackLayout(height=90, size_hint=[
                            1, None], orientation='lr-tb')
        playback_layout = AnchorLayout(
            anchor_x='center', anchor_y='center', size_hint_x=None, width=75)
        save_button_layout = AnchorLayout(
            anchor_x='center', anchor_y='center', size_hint_x=None, width=56)

        playback_details = {'tooltip': 'Pause', 'icon': 'pause-circle'} if self.playing_context == self.selected_playlist['uri'] and self.is_playing else {
            'tooltip': 'Play', 'icon': 'play-circle'}
        self.context_playback_button = PlaybackButton(app=self,
                                                      theme_text_color='Custom',
                                                      text_color='#1ed760',
                                                      shift_y=132,
                                                      pos_hint={
                                                          'center_x': .5, 'center_y': .5},
                                                      tooltip_radius=[3, ],
                                                      tooltip_font_style='Subtitle1',
                                                      tooltip_text=playback_details['tooltip'],
                                                      icon=playback_details['icon'],
                                                      target='context',
                                                      user_font_size=68
                                                      )
        icon = 'heart-outline'
        self.context_save_button = PlaybackButton(
            app=self,
            icon=icon,
            theme_text_color='Secondary',
            size=[32, 32],
            shift_y=102,
            tooltip_radius=[3, ],
            tooltip_font_style='Subtitle1',
            tooltip_text='Save to Your Library',
            target='context',
            user_font_size=40
        )
        playback_layout.add_widget(self.context_playback_button)
        panel.add_widget(playback_layout)
        save_button_layout.add_widget(self.context_save_button)
        panel.add_widget(save_button_layout)
        self.screen.ids.main_screen.add_widget(panel)

    def set_artist_details(self, id):
        self.tracks_table = []
        artist = self.spotify.artist(id)
        playlist_details_container = AnchorLayout(padding=[10, 10, 10, 10],
                                                  size_hint=[1, None],
                                                  anchor_x='left',
                                                  anchor_y='bottom',
                                                  height=340)
        container = BoxLayout(size_hint=[1, 1], spacing=10)

        playlist_details_container.add_widget(container)

        image = AsyncImage(size_hint=[None, None],
                           size=[232, 232],
                           pos_hint={'bot': 1},
                           source='')
        container.add_widget(image)

        label_details_container = BoxLayout(orientation='vertical',
                                            spacing=10,
                                            size_hint=[1, None])
        container.add_widget(label_details_container)

        verified_label = MDLabel(theme_text_color='Primary',
                                 size_hint=[1, None],
                                 strip=True,)
        name_label = MDLabel(font_style='H2',
                             size_hint=[1, None],
                             theme_text_color='Primary',
                             strip=True,)

        followers_label = MDLabel(size_hint=[1, None],
                                  theme_text_color='Primary',
                                  strip=True,)

        label_details_container.add_widget(verified_label)
        label_details_container.add_widget(name_label)
        label_details_container.add_widget(followers_label)

        image.source = artist['images'][0]['url']
        image.opacity = 1
        verified_label.text = "Verified artist"
        name_label.text = artist['name']
        followers_label.text = f'{artist["followers"]["total"]}'

        self.screen.ids.main_screen.clear_widgets()
        self.screen.ids.main_screen.add_widget(playlist_details_container)

    def set_playlist_details(self):
        self.tracks_table = []
        playlist_details_container = AnchorLayout(padding=[10, 10, 10, 10],
                                                  size_hint=[1, None],
                                                  anchor_x='left',
                                                  anchor_y='bottom',
                                                  height=340)
        container = BoxLayout(size_hint=[1, 1], spacing=10)

        playlist_details_container.add_widget(container)

        image = AsyncImage(size_hint=[None, None],
                           size=[232, 232],
                           pos_hint={'bot': 1},
                           source='')
        container.add_widget(image)

        label_details_container = BoxLayout(orientation='vertical',
                                            spacing=10,
                                            size_hint=[1, None])
        container.add_widget(label_details_container)

        privacy_playlist_label = MDLabel(theme_text_color='Primary',
                                         size_hint=[1, None],
                                         strip=True,)
        playlist_name_label = MDLabel(font_style='H2',
                                      size_hint=[1, None],
                                      theme_text_color='Primary',
                                      strip=True,)

        playlist_owner_label = MDLabel(size_hint=[1, None],
                                       theme_text_color='Primary',
                                       strip=True,)

        label_details_container.add_widget(privacy_playlist_label)
        label_details_container.add_widget(playlist_owner_label)
        label_details_container.add_widget(playlist_name_label)
        duration = 0
        if 'track' in self.selected_playlist['tracks']['items'][0]:
            for item in self.selected_playlist['tracks']['items']:

                duration += item['track']['duration_ms']
        else:
            for item in self.selected_playlist['tracks']['items']:

                duration += item['duration_ms']

        image.source = self.selected_playlist['images'][0]['url']
        image.opacity = 1
        try:
            privacy_playlist_label.text = "Public playlist" if self.selected_playlist[
                'public'] == "True" else "Private playlist"
        except KeyError:
            privacy_playlist_label.text = self.selected_playlist['album_type'].upper(
            )
        playlist_name_label.text = self.selected_playlist['name'] = "Public playlist"
        try:
            playlist_owner_label.text = f'{self.selected_playlist["owner"]["display_name"]}'\
                + f' {self.selected_playlist["tracks"]["total"]} tracks'\
                + ' {0} min {1} sec'.format(*to_timer(duration))
        except KeyError:
            artists = [artist['name']
                       for artist in self.selected_playlist['artists']]
            playlist_owner_label.text = f"{','.join(artists)} {self.selected_playlist['release_date']} {self.selected_playlist['tracks']['total']} " + ' {0} min {1} sec'.format(
                *to_timer(duration))

        self.screen.ids.main_screen.clear_widgets()
        self.screen.ids.main_screen.add_widget(playlist_details_container)

    def on_start(self):
        self.fps_monitor_start()

    def get_current_track(self, interval):

        try:
            if self.current_track_flag != self.current_track["item"]["name"]:
                current_track_layout = self.screen.ids.current_track
                current_track_layout.clear_widgets()

                image_grid = GridLayout(cols=1, size_hint=(
                    None, None), pos=[13, 16], size=(56, 56))
                image_grid.add_widget(AsyncImage(
                    source=self.current_track['item']['album']['images'][2]['url'], size=(42, 42), allow_stretch=True))
                self.current_track_flag = self.current_track["item"]["name"]
                label = Label(
                    text=self.current_track["item"]["name"],
                    font_size=13,
                    color='#ffffff',
                    halign='left',
                    pos=[83, 40],
                    font_name='arialbd',
                    bold=False

                    # theme_text_color='Primary',
                )
                label2 = Label(
                    text=self.current_track["artists"],
                    font_size=11,
                    color='#b3b3b3',
                    halign='left',
                    # theme_text_color='Primary',
                    pos=[83, 25],
                    font_name='arial',
                    bold=False
                )

                label.texture_update()
                label.size = label.texture_size
                label.texture_update()
                label2.texture_update()
                label2.size = label2.texture_size
                label2.texture_update()
                max_width = max(label.texture_size[0], label2.texture_size[0])
                deeper_layout = FloatLayout(
                    rows=2, size_hint=(None, 1), width=max_width)
                label.bind(size=label.setter('text_size'))
                label2.bind(size=label2.setter('text_size'))
                deeper_layout.add_widget(label)
                deeper_layout.add_widget(label2)

                current_track_layout.add_widget(image_grid)
                current_track_layout.add_widget(deeper_layout)
                likegrid = CurrentTrackLayout(cols=1, elevation=20, size_hint=(
                    1, 1), max_x_pos=109+max_width, pos=(Window.width*0.3-48, 35))
                #likegrid = CurrentTrackLayout(cols=1, size=(36, 36), pos=[46+current_track_layout.width+2*max(len(label2.text), len(label.text)), current_track_layout.height/2-18])
                current_track_layout.add_widget(likegrid)
        except TypeError as te:
            raise NoTrackAvailable

    def get_user_playlists(self):
        self.screen.ids.playlists.clear_widgets()
        self.playlists = self.spotify.current_user_playlists()['items'][::-1]
        for index, playlist in enumerate(self.playlists):
            layout = FloatLayout(size_hint=(1, None), height=32)
            label = PlaylistLabel(
                text=f'{playlist["name"]}',
                id=playlist['id'],
                snapshot_id=playlist['snapshot_id'],
                font_size=13,
                size_hint=(None, None),
                height=32,
                font_name='arialbd',
                color='#b3b3b3',
                pos=[10, index*32],
                shorten=True,
                detect_visible=False,
                halign='left',
                markup=True,
                shorten_from='right')
            layout.bind(size=self.resize_playlists_panel)
            label.texture_update()
            label.size = label.texture_size

            layout.add_widget(label)
            self.screen.ids.playlists.add_widget(
                layout)

    def schedule_clock_update_interface(self, interval):
        Clock.unschedule(self.clock)
        self.clock = Clock.schedule_interval(self.update_interface, 1)

    def update_current_track_layout(self, interval):
        self.screen.ids.current_track.children[0].on_window_resize(
            Window, Window.width, Window.height)

    def playlist_panel_resizing_on(self):
        self.playlist_panel_resizing = True

    def playlist_panel_resizing_off(self):
        self.playlist_panel_resizing = False

    def resize_playlists_panel(self, *args):
        if args:
            args[0].children[0].on_parent_resize()

    def resize_main_panel(self, *args):
        if args:
            args[0].children[0].on_parent_resize()

    def resize_header_label_minimum_size(self, label):
        if label.parent.width <= 100:
            label.parent.width = 100


if __name__ == '__main__':

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.call_soon_threadsafe(BetterSpotifyApp().run())
    BetterSpotifyApp().stop()
    loop.close()
