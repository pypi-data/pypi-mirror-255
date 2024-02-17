import pygame
from datetime import datetime

def log(logTxt: str, exitCode:int=None, printLog:bool=False, logFile:str="./log.txt"):
    currentTime = datetime.now().time().strftime("%H:%M:%S")
    logTxt = f"{currentTime}: {logTxt}\n"

    if printLog:
        print(logTxt)

    with open(logFile, "a") as logFile:
        logFile.write(logTxt)
    if exitCode:
        logTxt = f"---- EXITING WITH CODE {exitCode} ----\n"
        log(logTxt)

        exit(exitCode)

class text:
    """A simple text renderer."""
    def __init__(self, x:int, y:int, text:str, fontColour:tuple=(0, 0, 0), font=None, fontSize:int=24, antialias:bool=False):
        self.position = (x, y)
        self.text = text
        self.colour = fontColour
        self.font = pygame.font.Font(font, fontSize)
        self.aa = antialias

        self.textSurface = self.font.render(self.text, self.aa, self.colour)

    def draw(self, screen):
        screen.blit(self.textSurface, self.position)

    def setText(self, newText):
        self.text = newText

    def setPosition(self, x, y):
        self.position = (x, y)

    def alignPosition(self, screen, type:str="centre"):
        """Accepts the following alignment types:
        - 'centre'
        - 'left'
        - 'right'
        - 'top'
        - 'bottom'"""

        textSurfaceRect = self.textSurface.get_rect()

        if type == "centre":
            x = screen.get_width()//2 - textSurfaceRect.width//2
            y = screen.get_height()//2 - textSurfaceRect.height//2

            self.position = (x, y)
        elif type == "left":
            self.position = (0, screen.get_height()//2 - textSurfaceRect.height//2)
        elif type == "right":
            textSurfaceWidth = self.textSurface.get_rect().width
            self.position = (screen.get_width()-textSurfaceWidth, screen.get_height()//2 - textSurfaceRect.height//2)
        elif type == "top":
            self.position = (screen.get_width()//2 - textSurfaceRect.width//2, 0)
        elif type == "bottom":
            textSurfaceHeight = self.textSurface.get_rect().height
            self.position = (screen.get_width()//2- textSurfaceRect.width//2, screen.get_height()-textSurfaceHeight)
        else:
            log("Unknown position type.")

    def alignToText(self, text:'text', type="centre"):
        """Accepts the following alignment types:
        - 'centre'
        - 'left'
        - 'right'
        - 'top'
        - 'bottom'"""

        otherTextSurfaceRect = text.textSurface.get_rect()
        textSurfaceRect = self.textSurface.get_rect()

        x = text.position[0]
        y = text.position[1]

        if type == "centre":
            x += textSurfaceRect.width//2
            y -= (otherTextSurfaceRect.height - textSurfaceRect.height)//2

            self.position = (x, y)
        elif type == "left":
            x -= textSurfaceRect.width
            y -= (otherTextSurfaceRect.height - textSurfaceRect.height)//2

            self.position = (x, y)
        elif type == "right":
            x += otherTextSurfaceRect.width
            y -= (otherTextSurfaceRect.height - textSurfaceRect.height)//2
            
            self.position = (x, y)
        elif type == "top":
            x += textSurfaceRect.width//2
            y -= (otherTextSurfaceRect.height + textSurfaceRect.height)//2
            
            self.position = (x, y)
        elif type == "bottom":
            x += textSurfaceRect.width//2
            y += (otherTextSurfaceRect.height + textSurfaceRect.height)//2
            
            self.position = (x, y)
        else:
            log("Unknown position type.")

class progressBar:
    """A non-interactable progress bar, used to display progress.
    Does not support textures."""
    def __init__(self, x:int, y:int, width:int, height:int=16, progress:float=0, maxValue:float=100, colours:list=[(255, 255, 255), (25, 25, 25)]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.progress = progress
        self.maxValue = maxValue
        self.colours = colours

    def draw(self, screen):
        pygame.draw.rect(screen, self.colours[0], (self.x, self.y, self.width, self.height))

        progressWidth = int(self.width * (self.progress / self.maxValue))
        pygame.draw.rect(screen, self.colours[1], (self.x, self.y, progressWidth, self.height))

    def setValue(self, progress):
        self.progress = max(0, min(progress, self.maxValue))