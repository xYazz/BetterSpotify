from kivy.app import App
from kivy.metrics import dp
from uix.dropdownmenu import DropDownMenuTrackWithMousePos

def set_rmb_menu_items():
    app = App.get_running_app()
    app.rmb_menu_items = None
    app.rmb_track_menu = DropDownMenuTrackWithMousePos(
        width_mult=3,
        background_color='#282828',
        elevation=16,
        radius=[dp(4), dp(4), dp(4), dp(4)],
        max_height=0
    )
    ids = [item.spotify_id for idx,
            item in app.displayed_tracks_selected.items()]
    is_selected_in_liked_songs = app.spotify.current_user_saved_tracks_contains(
        tracks=ids)
    to_save_ids = [id for idx, id in enumerate(
        ids) if not is_selected_in_liked_songs[idx]]
    is_action_remove = all(is_selected_in_liked_songs)

    if is_action_remove:
        app.rmb_track_menu.row_width = 223

    app.rmb_menu_items = [
        {
            "text": 'Add to queue',
            "viewclass": "RightMouseButtonListItem",
            "divider": None,
            "divider_color": "#ffffff",
            "height": 40,
            "on_release": app.add_tracks_to_queue,
        },
        {
            "text": '',
            "viewclass": "RightMouseButtonListDivider",
            "divider": None,
            "divider_color": "#ffffff",
            "height": 1,
            "on_release": app.right_click_call_back,
        },
        {
            "text": 'Remove from your Liked Songs' if is_action_remove else 'Save to your Liked Songs',
            "viewclass": "RightMouseButtonListItem",
            "height": 40,
            "divider": None,
            "on_release": lambda: app.save_or_remove_from_saved_songs(to_save_ids if not is_action_remove else ids, is_action_remove),
        }, ]
    if 'owner' in app.selected_playlist:
        if app.current_user['id'] == app.selected_playlist['owner']['id']:
            app.rmb_menu_items.append({
                "text": 'Remove from this playlist',
                "viewclass": "RightMouseButtonListItem",
                "height": 40,
                "divider": None,
                "on_release": app.remove_from_playlist,
            })
    app.rmb_menu_items.append(
        {
            "text": 'Add to playlist',
            "viewclass": "RightMouseButtonNestedMenu",
            "height": 40,
            "divider": None,
            "on_release": lambda: app.open_nested_rmb_menu(app.screen.ids.main_screen, [100, 800]),
        }
    )

    if len(app.displayed_tracks_selected) == 1:
        item = app.displayed_tracks_selected[next(
            iter(app.displayed_tracks_selected))]

        app.rmb_menu_items[2:2] = (
            {
                "text": 'Go to song radio',
                "viewclass": "RightMouseButtonListItem",
                "divider": None,
                "height": 40,
                "on_release": app.go_to_song_radio,
            },
            {
                "text": 'Go to artist',
                "viewclass": "RightMouseButtonListItem" if len(item.artists_ids) == 1 else "RightMouseButtonNestedMenu",
                "divider": None,
                "height": 40,
                "on_release": app.rmb_go_to_artist_page if len(item.artists_ids) == 1 else lambda: None,
            },
            {
                "text": 'Go to album',
                "viewclass": "RightMouseButtonListItem",
                "divider": None,
                "height": 40,
                "on_release": app.rmb_go_to_album_page,
            },
            {
                "text": 'Show credits',
                "viewclass": "RightMouseButtonListItem",
                "divider": None,
                "height": 40,
                "on_release": app.right_click_call_back,
            },
            {
                "text": '',
                "viewclass": "RightMouseButtonListDivider",
                "divider": None,
                "divider_color": "#ffffff",
                "height": 1,
                "on_release": app.right_click_call_back,
            })
        app.rmb_menu_items.extend((
            {
                "text": '',
                "viewclass": "RightMouseButtonListDivider",
                "divider": None,
                "divider_color": "#ffffff",
                "height": 1,
                "on_release": app.right_click_call_back,
            },
            {
                "text": 'Share',
                "viewclass": "RightMouseButtonListItem",
                "divider": None,
                "height": 40,
                "on_release": app.share_song_link,
            })
        )