from kivy.logger import Logger
from kivy.base import ExceptionHandler, ExceptionManager
from kivy.clock import Clock
class NoTrackAvailableHandler(ExceptionHandler):
    def empty_callback(self, interval):
        pass
    def handle_exception(self, inst):
        if isinstance(inst, NoTrackAvailable):
            Logger.exception('NoTrackAvailable caught by NoTrackAvailableHandler')
            Clock.schedule_once(self.empty_callback, .2)
            return ExceptionManager.PASS
        return ExceptionManager.RAISE

class NoTrackAvailable(Exception):
    pass

