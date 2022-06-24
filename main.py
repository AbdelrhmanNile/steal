import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import threading
from steal_db_api import StealApi
import pwd
import json
import multiprocessing
from pandas import read_csv
from pebble import concurrent


Window.size = (1881, 996)
############ CUSTOM ELEMENTS ###################


class DownloadBtn(Button):
    def __init__(self, name, magnet, cover, pltfrm, **kwargs):
        super(DownloadBtn, self).__init__(**kwargs)
        self.g_magnet = magnet
        self.g_name = name
        self.g_cover = cover
        self.g_pltfrm = pltfrm
        self.background_color = (0.67, 0.70, 0.75, 1)
        self.text = "Download"

    def download(self):
        command = f"webtorrent download '{self.g_magnet}' -o '{app.conf['lib_path']}'"
        os.system(command)
        self.add_to_lib()

    def add_to_lib(self):
        arc_file, arc_type = self.get_arc_type()

        start_script = ""

        if arc_type == "zpaq":
            ## extract zpaq and get folder
            game_dir = arc_file[:-5:]
            command = f"cd {app.conf['lib_path']} && zpaq x {arc_file}"
            zpaq_task = multiprocessing.Process(
                target=os.system, args=(f"{command}",)
            ).start()
            start_script = f"{self.g_pltfrm[0]}start.sh"

        elif arc_type == "zst":
            ## extract zst and get folder name
            game_dir = arc_file[:-8:]
            command = f"cd {app.conf['lib_path']} && tar -xvf {arc_file}"
            zst_task = multiprocessing.Process(
                target=os.system, args=(f"{command}",)
            ).start()
            start_script = "start.sh"
            
        else:
            ## dwarfs
            game_dir = self.get_game_dir_dwarfs()
            start_script = f"start.{self.g_pltfrm[0]}.sh"

        params = f"{self.g_name},{self.g_cover},{app.conf['lib_path']}/{game_dir}/{start_script}\n"

        ## add to library csv
        with open(f"{app.steal_path}/library.csv", "a") as file:
            file.write(params)

        app.lib = read_csv(f"{app.steal_path}/library.csv")

    def get_game_dir_dwarfs(self):
        game_dir = ""
        for root, dirs, files in os.walk(app.conf["lib_path"]):
            for dirname in dirs:
                if (
                    dirname.find(self.g_name[1:].split(" ", 1)[0].replace(":", ""))
                    != -1
                ):
                    game_dir = dirname
                    break
            break

        return game_dir

    def get_arc_type(self):
        for root, dirs, files in os.walk(app.conf["lib_path"]):
            for filename in files:
                if (
                    filename.find(self.g_name[1:].split(" ", 1)[0]) != -1
                    and filename.find(".zpaq") != -1
                ):
                    return filename, "zpaq"
                if (
                    filename.find(self.g_name[1:].split(" ", 1)[0]) != -1
                    and filename.find(".zst") != -1
                ):
                    return filename, "zst"
        return None, "dwarfs"

    def on_press(self):
        download_task = multiprocessing.Process(target=self.download).start()


class BackToBrowseBtn(Button):
    def __init__(self, **kwargs):
        super(BackToBrowseBtn, self).__init__(**kwargs)
        self.background_color = (0.67, 0.70, 0.75, 1)

    def on_release(self):
        app.Sm.transition = SlideTransition(direction="right", duration=0.25)
        app.Sm.current = "main_screen"


class BtnAsyncImage(ButtonBehavior, AsyncImage):
    def __init__(
        self, g_cover_url, g_name, g_size, g_magnet, g_pltfrm, start_script, **kwargs
    ):
        super(BtnAsyncImage, self).__init__(**kwargs)
        self.g_cover_url = g_cover_url
        self.g_name = g_name
        self.g_size = g_size
        self.g_magnet = g_magnet
        self.g_pltfrm = g_pltfrm
        self.start_script = start_script

    def on_press(self):
        if self.g_magnet:
            app.Sm.gamescr.clear_widgets()
            app.Sm.gamescr.layout = GameDetailsLayout(
                g_cover_url=self.g_cover_url,
                g_name=self.g_name,
                g_size=self.g_size,
                g_magnet=self.g_magnet,
                g_pltfrm=self.g_pltfrm,
            )
            app.Sm.gamescr.add_widget(app.Sm.gamescr.layout)

    def on_release(self):
        if self.g_magnet:
            app.Sm.transition = SlideTransition(direction="left", duration=0.25)
            app.Sm.current = "game_screen"
        else:
            os.system(f"sh {self.start_script}")


class Card(BoxLayout):
    def __init__(
        self,
        cover_url=None,
        g_name=None,
        g_size=None,
        g_magnet=None,
        g_pltfrm=None,
        start_script=None,
        **kwargs,
    ):
        super(Card, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = (170, 270)
        self.padding = (7, 7)
        self.cover = BtnAsyncImage(
            source=str(cover_url),
            size_hint=(1, 1),
            g_cover_url=cover_url,
            g_name=g_name,
            g_size=g_size,
            g_magnet=g_magnet,
            g_pltfrm=g_pltfrm,
            start_script=start_script,
        )
        self.name = Label(
            text=g_name if len(g_name) <= 13 else g_name[:11] + "....",
            size_hint=(0.7, 0.1),
            padding=(0.2, 0),
        )
        self.add_widget(self.cover)
        self.add_widget(self.name)


class SearchBar(TextInput):
    def __init__(self, **kwargs):
        super(SearchBar, self).__init__(**kwargs)
        self.multiline = False
        self.background_color = (0.12, 0.13, 0.16, 1)
        self.foreground_color = (1, 1, 1, 1)
        self.hint_text = "Search..."
        self.hint_text_color = (1, 1, 1, 1)

        self.api = StealApi()

    @concurrent.process
    def get_search(self, g_name):
        return self.api.search(g_name)

    def on_text_validate(self):
        if self.text == "update":
            app.lib = read_csv(f"{app.steal_path}/library.csv")
            app.library.layout.clear_widgets()
            print(app.lib)
            for i in range(len(app.lib)):
                app.library.layout.add_widget(
                    Card(
                        cover_url=app.lib["cover"][i],
                        g_name=app.lib["name"][i],
                        start_script=app.lib["script"][i],
                        size_hint_y=None,
                        height=40,
                    )
                )
        else:
            task = self.get_search(self.text)
            response = task.result()
            app.browse.layout.clear_widgets()
            num_cards = (
                int(app.conf["num_of_cards"]) if self.text == "" else len(response)
            )

            for i in range(num_cards):
                game = response[i]
                app.browse.layout.add_widget(
                    Card(
                        cover_url=game["cover"],
                        g_name=game["name"],
                        g_size=game["size"],
                        g_magnet=game["magnet"],
                        g_pltfrm=game["pltfrm"],
                        size_hint_y=None,
                        height=40,
                    )
                )
            app.lib = read_csv(f"{app.steal_path}/library.csv")


########## SCREENS #################
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.name = "main_screen"

        self.add_widget(MainLayout())


class GameScreen(Screen):
    def __init__(self, layout=None, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.name = "game_screen"
        self.layout = None
        if layout:
            self.add_widget(layout)


class ScreensManager(ScreenManager):
    def __init__(self, **kwargs):
        super(ScreensManager, self).__init__(**kwargs)
        self.mainscr = MainScreen()
        self.gamescr = GameScreen()
        self.add_widget(self.mainscr)
        self.add_widget(self.gamescr)


######### LAYOUTS ###########
class MainLayout(TabbedPanel):
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)

        self.do_default_tab = True
        self.default_tab_text = "Browse"

        self.default_tab_content = app.browse
        self.background_color = (0.12, 0.13, 0.16, 1)

        self.library = TabbedPanelHeader(text="Library")
        self.library.content = app.library
        self.add_widget(self.library)
        self._tab_strip.add_widget(Label(text="                "))
        self._tab_strip.add_widget(SearchBar())
        self.tab_width = Window.width / 4


class BrowseTabLayout(ScrollView):
    def __init__(self, response=None, **kwargs):
        super(BrowseTabLayout, self).__init__()
        self.layout = StackLayout(size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter("height"))

        self.size_hint = (1, None)
        self.size = (Window.width, Window.height + 120)
        self.add_widget(self.layout)

    def add_cards(self):
        # task = self.get_db()
        self.response = self.get_db()
        self.cards = []
        if self.response:
            threading.Thread(target=self.create_cards, name="create_cards").run()

            for card in self.cards:
                self.layout.add_widget(card)

    # @concurrent.process
    def get_db(self):
        return api.search("")

    def create_cards(self):
        for i in range(int(app.conf["num_of_cards"])):
            game = self.response[i]
            self.cards.append(
                Card(
                    cover_url=game["cover"],
                    g_name=game["name"],
                    g_size=game["size"],
                    g_magnet=game["magnet"],
                    g_pltfrm=game["pltfrm"],
                    size_hint_y=None,
                    height=40,
                )
            )


class LibraryTabLayout(ScrollView):
    def __init__(self, **kwargs):
        super(LibraryTabLayout, self).__init__()
        self.layout = StackLayout(size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter("height"))
        self.cards = []

        threading.Thread(target=self.create_cards, name="create_cards_lib").run()

        for card in self.cards:
            self.layout.add_widget(card)

        self.size_hint = (1, None)
        self.size = (Window.width, Window.height + 120)
        self.add_widget(self.layout)

    def create_cards(self):
        for i in range(len(app.lib)):
            self.cards.append(
                Card(
                    cover_url=app.lib["cover"][i],
                    g_name=app.lib["name"][i],
                    start_script=app.lib["script"][i],
                    size_hint_y=None,
                    height=40,
                )
            )


class GameDetailsLayout(FloatLayout):
    def __init__(self, g_cover_url, g_name, g_size, g_magnet, g_pltfrm, **kwargs):
        super(GameDetailsLayout, self).__init__(**kwargs)
        self.g_name = g_name
        self.g_size = g_size
        self.g_magnet = g_magnet
        self.g_pltfrm = g_pltfrm

        self.cover = AsyncImage(
            source=g_cover_url, size_hint=(0.7, 0.7), pos=(-290, 140)
        )
        self.back_to_browse_btn = BackToBrowseBtn(
            text="back", size_hint=(None, None), size=(100, 50), pos=(100, 900)
        )
        self.add_widget(self.back_to_browse_btn)
        self.add_widget(self.cover)

        self.labelg_name = Label(text=self.g_name, pos=(300, 315), font_size=70)
        self.add_widget(self.labelg_name)

        self.g_size = Label(
            text=f"Size: {self.g_size}\nPlatform: {self.g_pltfrm}",
            pos=(-50, 200),
            font_size=50,
        )
        self.add_widget(self.g_size)

        self.download_btn = DownloadBtn(
            name=self.g_name,
            magnet=self.g_magnet,
            cover=g_cover_url,
            pltfrm=g_pltfrm,
            size_hint=(None, None),
            size=(100, 50),
            pos=(1600, 150),
        )
        self.add_widget(self.download_btn)


class StealApp(App):
    def build(self):
        init_task = threading.Thread(target=self.init_steal, name="init_steal").run()
        self.browse = BrowseTabLayout()
        self.library = LibraryTabLayout()
        self.Sm = ScreensManager()

        return self.Sm

    def on_start(self):
        self.browse.add_cards()

    def get_db(self):
        self.gamesdb = api.search("")

    def init_steal(self):
        # get linux username
        self.usr = pwd.getpwuid(os.getuid())[0]
        # define config path
        self.steal_path = f"/home/{self.usr}/.config/steal"
        # if conf.json doesnt exist make it
        self.check_conf()
        # load config as json obj
        self.conf = json.load(open(f"{self.steal_path}/conf.json"))

        self.check_lib()
        self.lib = read_csv(f"{self.steal_path}/library.csv")

    def check_conf(self):  # function to check if conf path and file exit
        if not os.path.isdir(self.steal_path):  # if path doesnt exit
            os.makedirs(self.steal_path)  # make it
            # config params
            params = {"lib_path": f"/home/{self.usr}/Games", "num_of_cards": "50"}
            # dump the config file
            with open(f"{self.steal_path}/conf.json", "w") as file:
                json.dump(params, file, indent=4)
        elif os.path.exists(self.steal_path) and not os.path.isfile(
            f"{self.steal_path}/conf.json"  # else if path exist but not config file
        ):
            params = {"lib_path": f"/home/{self.usr}/Games", "num_of_cards": "50"}
            # dump config file
            with open(f"{self.steal_path}/conf.json", "w") as file:
                json.dump(params, file, indent=4)
        else:  # else exit the function
            return

    def check_lib(self):
        if not os.path.isfile(f"{self.steal_path}/library.csv"):
            params = "name,cover,script"

            with open(f"{self.steal_path}/library.csv", "a") as file:
                file.write(params)


if __name__ == "__main__":
    api = StealApi()
    app = StealApp()
    app.run()
