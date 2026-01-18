from kivy.app import App
from kivymd.uix.button import MDIconButton
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.image import AsyncImage
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex


from uix.tracktablelabel import TrackTableLabel
from uix.tracktablerow import TrackTableRow
from layout_factories.app_utils.app_utils import to_timer, to_timer_with_hours, get_text_label_centered_in_anchor_layout
import datetime


def set_playlist_details(selected_playlist):
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
    if selected_playlist['tracks']['items']:
        if 'track' in selected_playlist['tracks']['items'][0]:
            for item in selected_playlist['tracks']['items']:

                duration += item['track']['duration_ms']
        else:
            for item in selected_playlist['tracks']['items']:

                duration += item['duration_ms']
    if selected_playlist['images']:
        image.source = selected_playlist['images'][0]['url']
    image.opacity = 1
    try:
        privacy_playlist_label.text = "Public playlist" if selected_playlist[
            'public'] == "True" else "Private playlist"
    except KeyError:
        privacy_playlist_label.text = selected_playlist['album_type'].upper(
        )
    playlist_name_label.text = selected_playlist['name'] = "Public playlist"
    try:
        playlist_owner_label.text = f'{selected_playlist["owner"]["display_name"]}'
            
        if selected_playlist["tracks"]["total"] > 0:
            playlist_owner_label.text += f' {selected_playlist["tracks"]["total"]} tracks'
        h, m, s =  to_timer_with_hours(duration)
        if h > 0:
            playlist_owner_label.text += f' {h} hr {m} min'
        else:
            if m > 0:
                playlist_owner_label.text += f' {m} min'
            if int(s) > 0:
                playlist_owner_label.text += f' {s} sec'
    except KeyError:
        artists = [artist['name']
                    for artist in selected_playlist['artists']]
        playlist_owner_label.text = f"{','.join(artists)} {selected_playlist['release_date']} {selected_playlist['tracks']['total']} " + ' {0} min {1} sec'.format(
            *to_timer(duration))

    return playlist_details_container
    
def get_song_radio_table_track(tracks_list):
    tracks = []
    tracks_table = StackLayout(size_hint=[1, None], padding=[
        12, 0, 12, 0], cols=1, spacing=1)
    tracks_table.bind(minimum_height=tracks_table.setter('height'))
    table_header = BoxLayout(orientation='horizontal', size_hint=(
        1, None), height=50, pos_hint={"top": 1}, padding=[12, 0, 12, 0])
    num = get_text_label_centered_in_anchor_layout(
        f'#', font_name='arial', font_size=15, size_hint_x=None, size_hint_y=None, width=36, height=50)
    table_header.add_widget(num)
    table_header.add_widget(
        get_text_label_centered_in_anchor_layout('TITLE', font_size=12, size_hint_x=.35))
    table_header.add_widget(
        get_text_label_centered_in_anchor_layout('ALBUM', font_size=12, size_hint_x=.3))
    table_header.add_widget(get_text_label_centered_in_anchor_layout(
        'DATE ADDED', font_size=12, size_hint_x=.2))
    icon = AnchorLayout(anchor_x='left', anchor_y='center',
                        size_hint=(None, None), size=(36, 50))
    icon.add_widget(
        MDIconButton(icon='clock-outline',
                     user_font_size='18sp', theme_text_color='Custom', text_color='#b3b3b3'))
    table_header.add_widget(icon
                            )

    with table_header.canvas.before:
        Color(*get_color_from_hex('#2a2a2a'))
        table_header.rect = Rectangle(
            pos=[table_header.pos[0], table_header.pos[1]+10],
            size=[table_header.size[0], 1],
        )

    table_header.bind(pos=lambda obj, pos: setattr(
        table_header.rect, "pos", [pos[0], pos[1]+10],))
    table_header.bind(size=lambda obj, size: setattr(
        table_header.rect, "size", [size[0], 1]))
    tracks_table.add_widget(table_header)
    for idx, item in enumerate(tracks_list):
        artists_ids = [artist["id"] for artist in item['artists']]

        row = TrackTableRow(orientation='horizontal',
                            pos_hint={"top": 1},
                            row_number=idx+1,
                            spotify_id=item['id'],
                            album_id=item['album']['id'],
                            song_link=item['external_urls']['spotify'],
                            artists_ids=artists_ids,
                            size_hint=(
                                1, None), height=55, padding=[12, 0, 12, 0])
        row.add_widget(get_text_label_centered_in_anchor_layout(
            f'{idx+1}', font_name='arial', font_size=15, size_hint_x=None, size_hint_y=None, width=26, padding=[0, 0, 18, 0], height=55, anchor_halign='right'))

        image_box = GridLayout(cols=1, size_hint=[None, None], size=[
            55, 55], padding=[0, 8, 8, 8])
        image_box.add_widget(AsyncImage(
            source=item['album']['images'][-1]['url'], size_hint=[None, None], height=40, width=40))
        row.add_widget(image_box)
        title_artists_box = GridLayout(
            rows=2, size_hint_x=.35, size_hint_y=None, height=55, padding=[0, 1, 0, 2])
        title_artists_box.add_widget(get_text_label_centered_in_anchor_layout(
            item['name'], label_class=TrackTableLabel, font_size=15, has_link=False, on_enter_color='#ffffff', shorten=True))
        artists = ', '.join([f'[ref={artist["id"]}]{artist["name"]}[/ref]'
                            for artist in item['artists']])
        title_artists_box.add_widget(get_text_label_centered_in_anchor_layout(
            artists, label_class=TrackTableLabel, font_size=13, markup=True, on_enter_color='#ffffff', on_leave_color='#b3b3b3', shorten=True))
        row.add_widget(title_artists_box)
        row.add_widget(get_text_label_centered_in_anchor_layout(
            item['album']['name'], label_class=TrackTableLabel, size_hint_x=.3, has_link='album_uri', link=item['album']['uri'], on_enter_color='#ffffff', on_leave_color='#b3b3b3', shorten=True))
        row.add_widget(get_text_label_centered_in_anchor_layout(
            str(datetime.datetime.now()), size_hint_x=.2))
        row.add_widget(
            get_text_label_centered_in_anchor_layout(
                '{0}:{1}'.format(
                    *to_timer(item['duration_ms'])),
                size_hint_x=None,
                size_hint_y=None,
                width=36,
                height=55,
                halign='right',
                shorten=True
            )
        )
        row.add_playback_button()
        row.add_playing_anim(1)
        row.row_num_label=row.get_row_numb_label()
        tracks_table.add_widget(row)
        tracks.append(row)
    return tracks, tracks_table


def get_playlist_tracks_table(tracks_list):
    tracks = []
    tracks_table = StackLayout(size_hint=[1, None], padding=[
        12, 0, 12, 0], cols=1, spacing=1)
    tracks_table.bind(minimum_height=tracks_table.setter('height'))
    table_header = BoxLayout(orientation='horizontal', size_hint=(
        1, None), height=50, pos_hint={"top": 1}, padding=[12, 0, 12, 0])
    num = get_text_label_centered_in_anchor_layout(
        f'#', font_name='arial', font_size=15, size_hint_x=None, size_hint_y=None, width=36, height=50)
    table_header.add_widget(num)
    table_header.add_widget(
        get_text_label_centered_in_anchor_layout('TITLE', font_size=12, size_hint_x=.35))
    table_header.add_widget(
        get_text_label_centered_in_anchor_layout('ALBUM', font_size=12, size_hint_x=.3))
    table_header.add_widget(get_text_label_centered_in_anchor_layout(
        'DATE ADDED', font_size=12, size_hint_x=.2))
    icon = AnchorLayout(anchor_x='left', anchor_y='center',
                        size_hint=(None, None), size=(36, 50))
    icon.add_widget(
        MDIconButton(icon='clock-outline',
                     user_font_size='18sp', theme_text_color='Custom', text_color='#b3b3b3'))
    table_header.add_widget(icon
                            )

    with table_header.canvas.before:
        Color(*get_color_from_hex('#2a2a2a'))
        table_header.rect = Rectangle(
            pos=[table_header.pos[0], table_header.pos[1]+10],
            size=[table_header.size[0], 1],
        )

    table_header.bind(pos=lambda obj, pos: setattr(
        table_header.rect, "pos", [pos[0], pos[1]+10],))
    table_header.bind(size=lambda obj, size: setattr(
        table_header.rect, "size", [size[0], 1]))
    tracks_table.add_widget(table_header)
    for idx, item in enumerate(tracks_list):
        artists_ids = [artist["id"] for artist in item['track']['artists']]
        row = TrackTableRow(orientation='horizontal',
                            pos_hint={"top": 1},
                            row_number=idx+1,
                            spotify_id=item['track']['id'],
                            album_id=item['track']['album']['id'],
                            song_link=item['track']['external_urls']['spotify'],
                            artists_ids=artists_ids, size_hint=(
                                1, None), height=55, padding=[12, 0, 12, 0])
        id_widget = get_text_label_centered_in_anchor_layout(
            f'{idx+1}',
            font_name='arial',
            font_size=15,
            size_hint_x=None,
            size_hint_y=None,
            width=26,
            padding=[0, 0, 18, 0],
            height=55,
            anchor_halign='right')
        row.add_widget(id_widget)
        image_box = GridLayout(cols=1, size_hint=[None, None], size=[
            55, 55], padding=[0, 8, 8, 8])
        image_box.add_widget(AsyncImage(
            source=item['track']['album']['images'][-1]['url'], size_hint=[None, None], height=40, width=40))
        row.add_widget(image_box)
        title_artists_box = GridLayout(
            rows=2, size_hint_x=.35, size_hint_y=None, height=55, padding=[0, 1, 0, 2])
        track_name_widget = get_text_label_centered_in_anchor_layout(
            item['track']['name'], label_class=TrackTableLabel, font_size=15, has_link=False, on_enter_color='#ffffff', shorten=True)

        title_artists_box.add_widget(track_name_widget)
        artists = ', '.join([f'[ref={artist["id"]}]{artist["name"]}[/ref]'
                            for artist in item['track']['artists']])
        artists_widget = get_text_label_centered_in_anchor_layout(
            artists, label_class=TrackTableLabel, font_size=13, markup=True, on_enter_color='#ffffff', on_leave_color='#b3b3b3', shorten=True)

        title_artists_box.add_widget(artists_widget)
        row.add_widget(title_artists_box)
        album_widget = get_text_label_centered_in_anchor_layout(
            item["track"]["album"]["name"], label_class=TrackTableLabel, size_hint_x=.3, has_link='album_uri', link=item['track']['album']['uri'], on_enter_color='#ffffff', on_leave_color='#b3b3b3', shorten=True)

        row.add_widget(album_widget)
        row.add_widget(get_text_label_centered_in_anchor_layout(
            str(datetime.datetime.strptime(item['added_at'], '%Y-%m-%dT%H:%M:%SZ').date()), size_hint_x=.2))
        row.add_widget(
            get_text_label_centered_in_anchor_layout(
                '{0}:{1}'.format(
                    *to_timer(item['track']['duration_ms'])),
                size_hint_x=None,
                size_hint_y=None,
                width=36,
                height=55,
                halign='right',
                shorten=True
            )
        )
        row.add_playback_button()
        row.add_playing_anim(1)
        row.row_num_label=row.get_row_numb_label()
        tracks_table.add_widget(row)
        tracks.append(row)
    return tracks, tracks_table


def get_artist_top_tracks_table(tracks_list):
    tracks = []
    tracks_table = StackLayout(size_hint=[1, None], padding=[
        12, 0, 12, 0], cols=1, spacing=1)
    tracks_table.bind(minimum_height=tracks_table.setter('height'))
    for idx, item in enumerate(tracks_list):
        app = App.get_running_app()
        track = app.spotify.track(item['id'])
        popularity = track['popularity']
        artists_ids = [artist["id"] for artist in item['artists']]
        row = TrackTableRow(orientation='horizontal',
                            pos_hint={"top": 1},
                            row_number=idx+1,
                            spotify_id=item['id'],
                            album_id=item['album']['id'],
                            song_link=item['external_urls']['spotify'],
                            artists_ids=artists_ids,

                            size_hint=(
                                .8, None), height=55, padding=[12, 0, 12, 0])
        row.add_widget(get_text_label_centered_in_anchor_layout(
            f'{idx+1}', font_name='arial', font_size=15, size_hint_x=None, size_hint_y=None, width=26, padding=[0, 0, 18, 0], height=55, anchor_halign='right'))

        image_box = GridLayout(cols=1, size_hint=[None, None], size=[
            55, 55], padding=[0, 8, 8, 8])
        image_box.add_widget(AsyncImage(
            source=item['album']['images'][-1]['url'], size_hint=[None, None], height=40, width=40))
        row.add_widget(image_box)

        row.add_widget(get_text_label_centered_in_anchor_layout(
            item['name'], label_class=TrackTableLabel, font_size=15, has_link=False, on_enter_color='#ffffff', shorten=True))

        row.add_widget(get_text_label_centered_in_anchor_layout(
            str(popularity), label_class=TrackTableLabel, size_hint_x=.45, has_link=False, shorten=True))
        row.add_widget(
            get_text_label_centered_in_anchor_layout(
                '{0}:{1}'.format(
                    *to_timer(item['duration_ms'])),
                size_hint_x=None,
                size_hint_y=None,
                width=36,
                height=55,
                halign='right',
                shorten=True
            )
        )
        row.add_playback_button()
        row.add_playing_anim(1)
        row.row_num_label=row.get_row_numb_label()
        tracks_table.add_widget(row)
        tracks.append(row)
    return tracks, tracks_table


def get_album_tracks_table(tracks_list):
    tracks = []
    tracks_table = StackLayout(size_hint=[1, None], padding=[
        12, 0, 12, 0], cols=1, spacing=1)
    tracks_table.bind(minimum_height=tracks_table.setter('height'))
    table_header = BoxLayout(orientation='horizontal', size_hint=(
        1, None), height=50, pos_hint={"top": 1}, padding=[12, 0, 12, 0])
    num = get_text_label_centered_in_anchor_layout(
        f'#', font_name='arial', font_size=15, size_hint_x=None, size_hint_y=None, width=36, height=50)
    table_header.add_widget(num)
    table_header.add_widget(
        get_text_label_centered_in_anchor_layout('TITLE', font_size=12, size_hint_x=.55))
    table_header.add_widget(
        get_text_label_centered_in_anchor_layout('POPULARITY', font_size=12, size_hint_x=.45))
    icon = AnchorLayout(anchor_x='left', anchor_y='center',
                        size_hint=(None, None), size=(36, 50))
    icon.add_widget(
        MDIconButton(icon='clock-outline',
                     user_font_size='18sp', theme_text_color='Custom', text_color='#b3b3b3'))
    table_header.add_widget(icon
                            )

    with table_header.canvas.before:
        Color(*get_color_from_hex('#2a2a2a'))
        table_header.rect = Rectangle(
            pos=[table_header.pos[0], table_header.pos[1]+10],
            size=[table_header.size[0], 1],
        )

    table_header.bind(pos=lambda obj, pos: setattr(
        table_header.rect, "pos", [pos[0], pos[1]+10],))
    table_header.bind(size=lambda obj, size: setattr(
        table_header.rect, "size", [size[0], 1]))
    tracks_table.add_widget(table_header)
    for idx, item in enumerate(tracks_list):
        app = App.get_running_app()
        track = app.spotify.track(item['id'])
        popularity = track['popularity']
        album_id = track['album']['id']
        artists_ids = [artist["id"] for artist in item['artists']]
        row = TrackTableRow(orientation='horizontal',
                            pos_hint={"top": 1},
                            row_number=idx+1,
                            context_type='album',
                            spotify_id=item['id'],
                            album_id=album_id,
                            song_link=item['external_urls']['spotify'],
                            artists_ids=artists_ids,
                            size_hint=(
                                1, None),
                            height=55,
                            padding=[12, 0, 12, 0])
        row.add_widget(get_text_label_centered_in_anchor_layout(
            f'{idx+1}', font_name='arial', font_size=15, size_hint_x=None, size_hint_y=None, width=20, height=55))

        title_artists_box = GridLayout(
            rows=2, size_hint_x=.55, size_hint_y=None, height=55, padding=[0, 1, 0, 2])
        title_artists_box.add_widget(get_text_label_centered_in_anchor_layout(
            item['name'], label_class=TrackTableLabel, font_size=15, has_link=False, on_enter_color='#ffffff', shorten=True))
        artists = ', '.join([f'[ref={artist["id"]}]{artist["name"]}[/ref]'
                            for artist in item['artists']])
        title_artists_box.add_widget(get_text_label_centered_in_anchor_layout(
            artists, label_class=TrackTableLabel, font_size=13, markup=True, on_enter_color='#ffffff', on_leave_color='#b3b3b3', shorten=True))
        row.add_widget(title_artists_box)

        row.add_widget(get_text_label_centered_in_anchor_layout(
            str(popularity), label_class=TrackTableLabel, size_hint_x=.45, has_link=False, shorten=True))
        row.add_widget(
            get_text_label_centered_in_anchor_layout(
                '{0}:{1}'.format(
                    *to_timer(item['duration_ms'])),
                size_hint_x=None,
                size_hint_y=None,
                width=36,
                height=55,
                halign='right',
                shorten=True
            )
        )
        tracks_table.add_widget(row)
        tracks.append(row)
    return tracks, tracks_table
