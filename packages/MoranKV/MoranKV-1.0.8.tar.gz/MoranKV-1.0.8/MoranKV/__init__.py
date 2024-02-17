import darkdetect, pyperclip
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.button import MDFlatButton
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from kivy import Config


Config.set('graphics', 'resizable', 0)
Config.set('input', 'mouse', 'mouse, multitouch_on_demand')
Config.set('kivy', 'exit_on_escape', 0)
Config.write()

from kivy.uix.settings import ContentPanel
from Filhanterare import FileManager
from screeninfo import get_monitors
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import *
from kivymd.app import MDApp
from .methods import *


__version__ = '1.0.8'

class Content(BoxLayout):
    pass

class MoranKV(MDApp):
    dark_mode_icon = StringProperty('')
    text_color = ListProperty([0, 0, 0, 1])

    def __init__(self, string: str, app_name: str, toolbar=True, dict_of_files: dict[str, str] = None,
            list_of_dirs: list[str] = None,
            screen_size=None, minimum=None, center: bool = True,
            sun_icon: str = 'white-balance-sunny', moon_icon: str = 'weather-night',
            main_color: str = 'Blue', icon: str = '', app_data: bool = True,
            disable_x: bool = False, pre_string: str = '', toolbar_name: str = None, **kwargs):
        super().__init__(**kwargs)

        if minimum is None:
            minimum = [0.1, 0.1]

        self.app_name = app_name
        self.builder_string = '''<Content>
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "100dp"'''
        self.file_manager = FileManager(app_name)

        if app_data:
            self.create_files(dict_of_files)
            self.create_dirs(list_of_dirs)

            self.moon_icon = moon_icon
            self.sun_icon = sun_icon
            self.is_dark_mode()

        self.dialog = None
        self.set_properties(main_color, icon, toolbar, string, pre_string, toolbar_name)
        self.disable_x = disable_x

        screen = get_monitors()[0]
        self.width = screen.width
        self.height = screen.height

        self.screen_positions(screen_size, minimum, center)

    @property
    def ids(self):
        return self.root.ids

    def set_properties(self, main_color, icon, toolbar, string, pre_string, toolbar_name):
        for x in pre_string.split('\n'):
            if 'x,y=' in x.replace(' ', '') and '#' not in x:
                self.builder_string += '\n' + self.x_y(x)

            elif 'Text:' in x:
                self.builder_string += '\n' + x
                spaces = x.split('Text:')[0].count(' ')
                self.builder_string += '\n' + spaces * ' ' + 'color: app.text_color'

            else:
                self.builder_string += '\n' + x

        self.builder_string += self.custom_classes()

        if toolbar:
            self.builder_string += self.get_toolbar(toolbar, toolbar_name)

            for x in string.split('\n'):
                if 'x,y=' in x.replace(' ', '') and '#' not in x:
                    self.builder_string += '\n            ' + self.x_y(x)

                elif 'Text:' in x:
                    self.builder_string += '\n            ' + x
                    spaces = x.split('Text:')[0].count(' ') + 4
                    self.builder_string += '\n            ' + spaces * ' ' + 'color: app.text_color'

                else:
                    self.builder_string += '\n            ' + x

        self.theme_cls.primary_palette = main_color
        self.icon = icon

    def build(self):
        self.use_kivy_settings = False
        self.settings_cls = ContentPanel
        self.title = self.app_name

        Window.bind(on_dropfile=lambda *args: self.on_drop_file(*args),
                    on_request_close=lambda x: self.on_request_close(self.disable_x))

        self.pre_build()
        return Builder.load_string(self.builder_string)

    def pre_build(self):
        pass

    def screen_positions(self, screen_size, minimum=None, center=True):
        if minimum is None:
            minimum = [0.1, 0.1]

        min_x, min_y = minimum

        if screen_size is None:
            x, y = 0.6, 0.6

        else:
            x, y = screen_size[0], screen_size[1]

        if x <= 1 or y <= 1:
            Window.size = (self.width * x, self.height * y)
            Window.minimum_height = self.height * min_y
            Window.minimum_width = self.width * min_x

        else:
            Window.size = (x, y)
            Window.minimum_height = min_y
            Window.minimum_width = min_x

            if center:
                Window.left = (self.width - x) / 2
                Window.top = (self.height - y) / 2
                return

            else:
                return

        if center:
            Window.left = (self.width - (self.width * x)) / 2
            Window.top = (self.height - (self.height * y)) / 2

    def create_files(self, list_of_files: dict[str, str]):
        if list_of_files is None:
            return

        self.file_manager.create_files(list_of_files)

    def create_dirs(self, list_of_dirs: list[str]):
        if list_of_dirs is None:
            return

        self.file_manager.create_dirs(list_of_dirs)

    def set_file(self, file, value, encoding="utf-8"):
        self.file_manager.set_file(file, value, encoding=encoding)

    def get_file(self, file, default=None, create_file_if_not_exist="", encoding='utf-8'):
        try:
            return self.file_manager.get_file(file, default, encoding=encoding)

        except FileNotFoundError:
            if create_file_if_not_exist:
                self.set_file(file, create_file_if_not_exist)

            return default

        except Exception as e:
            print(e)
            return default

    def is_dark_mode(self, filename='dark mode.txt'):
        default = darkdetect.theme()
        mode = self.get_file(filename, create_file_if_not_exist=default, default=default)
        self.set_dark_mode_icon(mode)
        return mode == 'Dark'

    def on_theme_change(self, value):
        self.text_color = [0, 0, 0, 1] if value == "Light" else [1, 1, 1, 1]

    def set_dark_mode(self, value=None, filename='dark mode'):
        if value is None:
            value = darkdetect.theme()

        self.set_file(filename, value)
        self.set_dark_mode_icon(value)

    def reverse_dark_mode(self, filename: str = 'dark mode.txt'):
        current_mode = self.get_file(filename, default=darkdetect.theme())
        reversed_mode = 'Dark' if current_mode == 'Light' else 'Light'
        self.set_dark_mode(reversed_mode, filename)
        return reversed_mode

    def set_dark_mode_icon(self, value):
        if value == 'Dark':
            self.dark_mode_icon = self.moon_icon

        else:
            self.dark_mode_icon = self.sun_icon

        self.theme_cls.theme_style = value
        self.on_theme_change(value)

    def get_toolbar(self, properties: list, toolbar_name: str):
        if properties is True:
            right_icons, left_icons = '[[app.dark_mode_icon, lambda x: app.reverse_dark_mode()]]', '[]'

        elif len(properties) == 2:
            left_icons, right_icons, name = properties[0], properties[1], self.app_name

        else:
            left_icons, right_icons, name = properties

        if toolbar_name:
            name = toolbar_name

        else:
            name = self.app_name

        return f'''
Screen:
    MDTopAppBar:
        id: toolbar
        pos_hint: {{"top": 1}}
        elevation: 3
        title: "{name}"
        right_action_items: {right_icons}
        left_action_items: {left_icons}

    MDNavigationLayout:
        x: toolbar.height
        ScreenManager:
            id: screen_manager
'''

    @staticmethod
    def toast(text, duration=2.5):
        from kivymd.toast import toast

        toast(text=text, duration=duration)

    @staticmethod
    def snack(text, button_text=None, func=None):
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.snackbar import Snackbar

        snack = Snackbar(text=text)

        if func and button_text:
            snack.buttons = [MDFlatButton(text=f"[color=#1aaaba]{button_text}[/color]", on_release=func)]

        snack.open()

    @staticmethod
    def x_y(x_y):
        x, y = eval(x_y.split("=")[1])
        return f"{x_y.index('x') * ' '}pos_hint: {{'center_x': {x}, 'center_y': {y}}}"

    @staticmethod
    def custom_classes():
        return '''
<Text@MDLabel>:
    halign: 'center'

<Input@MDTextField>:
    mode: "rectangle"
    text: ""
    size_hint_x: 0.5

<Check@MDCheckbox>:
    group: 'group'
    size_hint: None, None
    size: dp(48), dp(48)

<Btn@MDFillRoundFlatButton>:
    text: ""

<BtnIcon@MDFillRoundFlatIconButton>:
    text: ""

<Img@Image>:    
    allow_stretch: True

<CircleIcon@MDFloatingActionButton>:
    md_bg_color: app.theme_cls.primary_color
'''

    @staticmethod
    def on_drop_file(*args):
        print(*args)

    @staticmethod
    def on_request_close(disable_x: bool = False):
        return disable_x

    @staticmethod
    def write_to_clipboard(text: str):
        pyperclip.copy(text)

    def copy(self, text: str):
        self.write_to_clipboard(text)

    def show_date_picker(self, on_save, mode='picker'):
        date_dialog = MDDatePicker(mode=mode)
        date_dialog.bind(on_save=on_save, on_cancel=self.on_cancel_picker)
        date_dialog.open()

    def show_time_picker(self, on_save):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=on_save, on_cancel=self.on_cancel_picker)
        time_dialog.open()

    def on_cancel_picker(self, instance, value):
        pass

    def popup_morankv(self, title='My popup', content=Content(), cancel_text='CANCEL', okay_text='OKAY',
            okay_func=lambda *args: print('yes'), cancel_func=None, auto_dismiss=True):
        if cancel_func is None:
            cancel_func = lambda *args: self.dismiss()

        if self.dialog:
            self.dismiss()

        buttons = []
        if cancel_text:
            buttons.append(MDFlatButton(
                    text=cancel_text,
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=cancel_func
            ))

        if okay_text:
            buttons.append(MDFlatButton(
                    text=okay_text,
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=okay_func
            ))

        self.dialog = MDDialog(
                title=title,
                type="custom",
                content_cls=content,
                buttons=buttons,
                auto_dismiss=auto_dismiss
        )

        self.dialog.open()

    def dismiss(self):
        try:
            self.dialog.dismiss()
        except Exception as e:
            print(e)

    def delete_file(self, path):
        self.file_manager.delete_file(path)

    def create_from_base64(self, file_path: str, b64: str):
        self.file_manager.write(file_path, base64.b64decode(b64), wb=True)

    @property
    def appdata_path(self):
        return self.file_manager.path

    @property
    def appdata(self):
        return self.appdata_path

    @property
    def path(self):
        return self.appdata_path
