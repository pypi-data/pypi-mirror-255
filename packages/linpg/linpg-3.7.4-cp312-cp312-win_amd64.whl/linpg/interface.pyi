from .battle import *

class _Loader:
    @staticmethod
    def img(path: str, size: tuple = ..., alpha: int = 255, ifConvertAlpha: bool = True) -> ImageSurface: ...
    @staticmethod
    def static_image(path: str, _position: tuple = (0, 0), size: tuple = (-1, -1), tag: str = '') -> StaticImage: ...
    @staticmethod
    def movable_static_image(path: str, _position: tuple, target_position: tuple, move_speed: tuple, size: tuple, tag: str = '') -> MovableStaticImage: ...
    @staticmethod
    def progress_bar_surface(img_on_top_path: str, img_on_bottom_path: str, _position: tuple[int, int], size: tuple[int, int], mode: Axis = ..., tag: str = '') -> ProgressBarSurface: ...
    @staticmethod
    def gif(gif_path_or_img_list: str | Sequence[PoI], _position: tuple[int, int], size: tuple[int, int], fps: int | None = None) -> AnimatedImage: ...
    @staticmethod
    def button(path: str, _position: tuple[int, int], size: tuple[int, int], alpha_when_not_hover: int = 255) -> Button: ...
    @staticmethod
    def text(txt: str | int, _color: color_liked, pos: tuple, size: int, ifBold: bool = False, ifItalic: bool = False) -> TextSurface: ...
    @staticmethod
    def resize_when_hovered_text(txt: str | int, _color: color_liked, pos: tuple[int, int], size: int, _bold: bool = False, _italic: bool = False) -> ResizeWhenHoveredTextSurface: ...
display = Display
lang = Lang
setting = Setting
info = Info
keys = Keys
config = Config
colors = Colors
global_variables = GlobalVariables
sounds = Sounds
music = Music
volume = Volume
media = Media
images = Images
controller = Controller
ui = UI
font = Font
position = Positions
coordinates = Coordinates
surfaces = Surfaces
debug = Debug
load = _Loader
numbers = Numbers
saves = Saves
db = DataBase
AbstractVisualNovelSystem = AbstractVisualNovelPlayer
VisualNovelSystem = VisualNovelPlayer
DialogEditor = VisualNovelEditor
