import pytweening, pygame, sys, os


from pyredengine import Formatter as Formatter
from pyredengine import Utils as Utils
from pyredengine import EntityService as EntityService 
from pyredengine import SceneService as SceneService 
from pyredengine import GuiService as GuiService 
from pyredengine import TweenService as TweenService

class FPSCounter(GuiService.TextElement):
    def __init__(self, position, text, size, color):
        super().__init__(position, text, size, color)

    def update_position(self, position):
        return super().update_position(position)
    
    def update_text(self, text):
        return super().update_text(text)
    
    def draw(self, screen):
        return super().draw(screen)
    




class DebugService():
    def __init__(self, app, clock):
        self.app = app
        self.clock = clock

        #self.fps = FPSCounter((40,40), str(round(self.clock.get_fps(), 0)), 24, (255, 255, 255))

    def update(self):
        self.fps = FPSCounter((40,40), str(round(self.clock.get_fps(), 0)), 24, (255, 255, 255))


    def draw(self, screen):
        self.fps.draw(screen)