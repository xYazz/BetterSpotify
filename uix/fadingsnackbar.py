
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.uix.snackbar import Snackbar, BaseSnackbar


class FadingSnackbar(Snackbar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'size_hint' in kwargs:
            self.size_hint = kwargs['size_hint']
        if 'size' in kwargs:
            self.size = kwargs['size']
        self.opacity = 0

    def dismiss(self, *args):
        """Dismiss the snackbar."""

        def dismiss(interval):
            anim = Animation(opacity=0, d=0.2)

            anim.bind(
                on_complete=lambda *args: Window.parent.remove_widget(self)
            )
            anim.start(self)

        Clock.schedule_once(dismiss, 0.5)
        self.dispatch("on_dismiss")

    def open(self):
        """Show the snackbar."""

        def wait_interval(interval):
            self._interval += interval
            if self._interval > self.duration:
                self.dismiss()
                Clock.unschedule(wait_interval)
                self._interval = 0

        for c in Window.parent.children:
            if isinstance(c, BaseSnackbar):
                return

        self.x = self.snackbar_x
        self.y = self.snackbar_y

        Window.parent.add_widget(self)
        anim = Animation(
            opacity=1, d=0.2
        )

        if self.auto_dismiss:
            anim.bind(
                on_complete=lambda *args: Clock.schedule_interval(
                    wait_interval, 0
                )
            )
        anim.start(self)
        self.dispatch("on_open")

