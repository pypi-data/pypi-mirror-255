from ..interface import *

class Shadows:
    @staticmethod
    def render(img: AbstractImageSurface, target_surface: ImageSurface, alpha: int = 100, percentage: int = 80) -> None: ...
