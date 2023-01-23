from kivy.lang import Builder

from kivymd.app import MDApp
from kivymd.uix.slider import MDSlider
KV = '''
MDScreen

    MDSlider:
        min: 0
        max: 100
        value: 40
'''


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)


Test().run()