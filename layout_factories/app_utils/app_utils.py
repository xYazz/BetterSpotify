from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout

from uix.tracktablelabel import TrackTableLabel

def to_timer(value_in_ms):
        value_in_s = value_in_ms/1000
        min = int(value_in_s/60)
        if int(value_in_s-min*60) > 9:
            seconds = str(int(value_in_s-min*60))
        else:
            seconds = str('0' + str(value_in_s-min*60)[0])
        return (str(min), seconds)

def get_text_label_centered_in_anchor_layout(
            label_text,
            label_class=Label,
            halign='left',
            font_name='arialbd',
            font_size=13,
            size_hint_x=1,
            size_hint_y=1,
            width=100,
            height=100,
            shorten=False,
            padding=[0, 0, 0, 0],
            anchor_halign='left',
            **kwargs):
        label_box = AnchorLayout(anchor_x=anchor_halign, anchor_y='center', size_hint=(
            size_hint_x, size_hint_y), width=width, height=height, padding=padding)
        if 'on_enter_color' not in kwargs:
            kwargs['color'] = '#b3b3b3'
        label = label_class(text=label_text,
                            font_size=font_size,
                            halign=halign,
                            size_hint=(None, None),
                            font_name=font_name,
                            bold=False,
                            shorten=True,
                            shorten_from='right',
                            **kwargs)
        if label_class == TrackTableLabel:
            app = App.get_running_app()
            label_box.bind(size=app.resize_main_panel)
        label.texture_update()
        label.size = label.texture_size
        label_box.add_widget(label)
        return label_box