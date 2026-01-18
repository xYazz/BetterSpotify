from kivy.app import App
from kivy.core.window import Window
from kivy.effects.scroll import ScrollEffect
from kivy.metrics import dp
from uix.dropdownmenu import DropDownMenuTrackWithMousePos
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivymd.uix.label import MDLabel

from layout_factories.context_table_layouts import set_playlist_details, get_album_tracks_table, get_artist_top_tracks_table, get_song_radio_table_track, get_playlist_tracks_table


class Rmb_on_track_menu():
    def __init__(self):
        self.app = App.get_running_app()
        self.rmb_menu_items = None
        self.rmb_menu = None

    def set_params(self, caller, touch):
        self.rmb_menu.caller = caller
        self.rmb_menu.touch = touch
        self.rmb_menu.items = self.rmb_menu_items

    def reset(self):
        self.dismiss()
        self.rmb_menu_items = None
        self.rmb_menu = None

    def open(self):
        self.rmb_menu.open()

    def set_rmb_menu_items(self):
        self.rmb_menu_items = None
        self.rmb_menu = DropDownMenuTrackWithMousePos(
            width_mult=3,
            background_color='#282828',
            elevation=16,
            radius=[dp(4), dp(4), dp(4), dp(4)],
            max_height=0
        )
        ids = [item.spotify_id for idx,
                item in self.app.displayed_tracks_selected.items()]
        is_selected_in_liked_songs = self.app.spotify.current_user_saved_tracks_contains(
            tracks=ids)
        to_save_ids = [id for idx, id in enumerate(
            ids) if not is_selected_in_liked_songs[idx]]
        is_action_remove = all(is_selected_in_liked_songs)

        if is_action_remove:
            self.rmb_menu.row_width = 223

        self.rmb_menu_items = [
            {
                "text": 'Add to queue',
                "viewclass": "RightMouseButtonListItem",
                "divider": None,
                "divider_color": "#ffffff",
                "height": 40,
                "on_release": self.app.add_tracks_to_queue,
            },
            {
                "text": '',
                "viewclass": "RightMouseButtonListDivider",
                "divider": None,
                "divider_color": "#ffffff",
                "height": 1,
                "on_release": self.dismiss,
            },
            {
                "text": 'Remove from your Liked Songs' if is_action_remove else 'Save to your Liked Songs',
                "viewclass": "RightMouseButtonListItem",
                "height": 40,
                "divider": None,
                "on_release": lambda: self.app.save_or_remove_from_saved_songs(to_save_ids if not is_action_remove else ids, is_action_remove),
            }, ]
        if 'owner' in self.app.selected_playlist:
            if self.app.current_user['id'] == self.app.selected_playlist['owner']['id']:
                self.rmb_menu_items.append({
                    "text": 'Remove from this playlist',
                    "viewclass": "RightMouseButtonListItem",
                    "height": 40,
                    "divider": None,
                    "on_release": self.app.remove_from_playlist,
                })
        self.rmb_menu_items.append(
            {
                "text": 'Add to playlist',
                "viewclass": "RightMouseButtonNestedMenu",
                "height": 40,
                "divider": None,
                "on_release": lambda: self.app.open_nested_rmb_menu(self.app.screen.ids.main_screen, [100, 800]),
            }
        )

        if len(self.app.displayed_tracks_selected) == 1:
            item = self.app.displayed_tracks_selected[next(
                iter(self.app.displayed_tracks_selected))]

            self.rmb_menu_items[2:2] = (
                {
                    "text": 'Go to song radio',
                    "viewclass": "RightMouseButtonListItem",
                    "divider": None,
                    "height": 40,
                    "on_release": self.go_to_song_radio,
                },
                {
                    "text": 'Go to artist',
                    "viewclass": "RightMouseButtonListItem" if len(item.artists_ids) == 1 else "RightMouseButtonNestedMenu",
                    "divider": None,
                    "height": 40,
                    "on_release": self.rmb_go_to_artist_page if len(item.artists_ids) == 1 else lambda: None,
                },
                {
                    "text": 'Go to album',
                    "viewclass": "RightMouseButtonListItem",
                    "divider": None,
                    "height": 40,
                    "on_release": self.rmb_go_to_album_page,
                },
                {
                    "text": 'Show credits',
                    "viewclass": "RightMouseButtonListItem",
                    "divider": None,
                    "height": 40,
                    "on_release": self.dismiss,
                },
                {
                    "text": '',
                    "viewclass": "RightMouseButtonListDivider",
                    "divider": None,
                    "divider_color": "#ffffff",
                    "height": 1,
                    "on_release": self.dismiss,
                })
            self.rmb_menu_items.extend((
                {
                    "text": '',
                    "viewclass": "RightMouseButtonListDivider",
                    "divider": None,
                    "divider_color": "#ffffff",
                    "height": 1,
                    "on_release": self.dismiss,
                },
                {
                    "text": 'Share',
                    "viewclass": "RightMouseButtonListItem",
                    "divider": None,
                    "height": 40,
                    "on_release": self.app.share_song_link,
                })
            )

    
    def get_add_to_playlist_dropdown_items(self):
        if len(self.app.displayed_tracks_selected) > 0:
            tracks_ids = ["spotify:track:"+track.spotify_id for id,
                   track in self.app.displayed_tracks_selected.items()]

            def add_to_playlist(playlist_id, playlist_name, items_ids):
                self.app.spotify.playlist_add_items(playlist_id=playlist_id, items=items_ids)
                self.app.prompt_snackbar(text=f"Added to playlist {playlist_name}", width=188)
            items = [
                {
                    "text": '',
                    "viewclass": "RightMouseButtonSearchField",
                    "divider": None,
                    "divider_color": "#ffffff",
                    "height": 39,
                    "max_length": 0,
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
                    "on_release": self.dismiss,
                }, ]
            longest_playlist_name = 0
            
            for item in self.app.playlists:
                longest_playlist_name = max(
                    longest_playlist_name, len(item['name']))
                items.append(
                    {
                        "text": item['name'],
                        "viewclass": "RightMouseButtonNestedListItem",
                        "divider": None,
                        "divider_color": "#ffffff",
                        "height": 39,
                        "on_release": lambda playlist_id=item['id'], playlist_name=item['name']: add_to_playlist(playlist_id, playlist_name, tracks_ids),
                    }
                )
            items[0]['max_length'] = longest_playlist_name
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
            caller=self.rmb_menu,
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

    
    def rmb_go_to_album_page(self):
        self.reset()
        if len(self.app.displayed_tracks_selected) == 1:
            item = self.app.displayed_tracks_selected[next(
                iter(self.app.displayed_tracks_selected))]
            self.app.selected_playlist = self.app.spotify.album(item.album_id)
            self.get_album_details()

    def go_to_album_page(self, id):
        self.app.selected_playlist = self.spotify.album(id)
        self.get_album_details()

    def get_album_details(self):
        set_playlist_details()
        tracks, tracks_widget = get_album_tracks_table(
            self.app.selected_playlist['tracks']['items'])
        self.app.tracks_table = tracks
        self.app.screen.ids.main_screen.add_widget(tracks_widget)

    def rmb_go_to_artist_page(self):
        self.reset()
        if len(self.app.displayed_tracks_selected) == 1:
            item = self.app.displayed_tracks_selected[next(
                iter(self.app.displayed_tracks_selected))]
            self.app.selected_playlist = self.app.spotify.artist_top_tracks(
                item.artists_ids[0])
            self.app.uris = [item['uri']
                         for item in self.app.selected_playlist['tracks']]
            self.set_artist_details(item.artists_ids[0])
            tracks, tracks_widget = get_artist_top_tracks_table(
                self.app.selected_playlist['tracks'])
            self.app.tracks_table = tracks
            self.app.screen.ids.main_screen.add_widget(tracks_widget)

    def go_to_artist_page(self, id):
        self.selected_playlist = self.app.spotify.artist_top_tracks(id)
        self.uris = [item['uri'] for item in self.selected_playlist['tracks']]
        self.set_artist_details(id)
        tracks, tracks_widget = get_artist_top_tracks_table(
            self.selected_playlist['tracks'])
        self.app.tracks_table = tracks
        self.app.screen.ids.main_screen.add_widget(tracks_widget)

    def go_to_song_radio(self):
        self.reset()

        if len(self.app.displayed_tracks_selected) > 0:
            arr = [track.spotify_id for id,
                   track in self.app.displayed_tracks_selected.items()]

            new_playlist = self.app.spotify.recommendations(seed_tracks=arr)

            self.app.uris = [item['uri'] for item in new_playlist['tracks']]
            self.set_playlist_details()
            self.app.create_context_playback_panel(self.app.selected_playlist['uri'])

            del self.app.selected_playlist['uri']
            tracks, tracks_widget = get_song_radio_table_track(
                new_playlist['tracks'])
            self.app.tracks_table = tracks
            self.app.screen.ids.main_screen.add_widget(tracks_widget)
 
 
    def set_artist_details(self, id):
        self.app.tracks_table = []
        artist = self.app.spotify.artist(id)
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

        self.app.screen.ids.main_screen.clear_widgets()
        self.app.screen.ids.main_screen.add_widget(playlist_details_container)

    def dismiss(self):
        self.rmb_menu.dismiss()