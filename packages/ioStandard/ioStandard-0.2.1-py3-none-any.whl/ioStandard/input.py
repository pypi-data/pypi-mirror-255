import pygame
import ioStandard.output as output

pygame.init()

class inputBox:
    """An input box that allows a custom ruleset for inputted characters.
    Should be used for development purposes only, because it does not take into consideration textures/custom colours."""
    def __init__(self, x:int, y:int, w:int=140, h:int=32, max:int=0, prompt:str="", filled:bool=False, text:str="", ruleset:str="abcdefghijklmnopqrstuvwxyz1234567890!£$%^&*()-_=+.,<>/?'@#~:; ""abcdefghijklmnopqrstuvwxyz1234567890!£$%^&*()-_=+.,<>/?'@#~:; ", font=None):
        self.ruleset = ruleset
        
        self.rect = pygame.Rect(x, y, w, h)
        self.colour = (150, 150, 150)
        self.max = max
        self.prompt = prompt
        self.text = text
        self.font = pygame.font.Font(font, h)
        self.textSurface = self.font.render(text, True, self.colour)
        self.active = False
        self.hover = False
        self.filled = filled
        self.finalText = "placeholder"

    # Handle events such as mouse clicks and key presses
    def handleEvent(self, event):
        # Mouse events
        modifiedText = ""
        for char in self.text:
            if char not in self.ruleset:
                modifiedText += ""  # Replace with your desired replacement
            else:
                modifiedText += char
        self.text = modifiedText

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if mouse clicked inside the input box
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            # Change color based on activity
            self.colour = (255, 255, 255) if self.active else (150, 150, 150)
        # Keyboard events
        if event.type == pygame.KEYDOWN:
            if self.active:
                # Handle Enter, Backspace, and Ctrl+V for paste
                if event.key == pygame.K_RETURN:
                    self.finalText = self.text
                    self.text = ""
                    self.active = False
                    self.colour = (150, 150, 150)
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif (event.key == pygame.K_v) and (event.mod & pygame.KMOD_CTRL):
                    try:
                        # Try to get text from the clipboard and append it to the input
                        pygame.scrap.init()
                        pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)
                        clipboard = pygame.scrap.get("text/plain;charset=utf-8").decode()
                        clipboard = ''.join(char for char in clipboard if char.isprintable())
                        self.text += clipboard
                    except:
                        pass
                else:
                    # Handle regular text input
                    if (len(self.text) < self.max or self.max == 0) and event.unicode in self.ruleset:
                        self.text += event.unicode
                        
                # Update the rendered text surface
                self.textSurface = self.font.render(self.text, True, (20, 20, 20))
        # Mouse motion events for hover effect
        elif event.type == pygame.MOUSEMOTION and not self.active:
            self.hover = self.rect.collidepoint(event.pos)
            self.colour = (200, 200, 200) if self.hover else (150, 150, 150)

    # Update the input box width based on text width
    def update(self):
        if not self.rect.w > self.max or self.max == 0:
            width = max(200, self.textSurface.get_width() + 10)
            self.rect.w = width

    # Draw the input box on the screen
    def draw(self, screen):
        # Draw filled or unfilled input box and text
        if self.filled:
            pygame.draw.rect(screen, self.colour, self.rect)
            screen.blit(self.textSurface, (self.rect.x + 5, self.rect.y + 8))
        else:
            screen.blit(self.textSurface, (self.rect.x + 5, self.rect.y + 8))
            pygame.draw.rect(screen, self.colour, self.rect, 2)

        # Display prompt if there's no text and a prompt is provided
        if not self.text and self.prompt:
            screen.blit(self.font.render(self.prompt, True, (30, 30, 30)), (self.rect.x + 5, self.rect.y + 8))

class button:
    """A simple button capable of completing an action, in the form of a callable."""
    def __init__(self, x: int, y: int, *args, action: callable, cycle: bool = True, toggle: bool =False, textures: list = None, hotkeys: list = [], sfx = None, colourScheme: dict = None, state: int =0):
        self.cycle = cycle
        self.toggle = toggle
        self.textures = textures
        self.hotkeys = hotkeys
        self.sfx = sfx
        self.size = (50, 50)
        self.position = (x, y)
        self.args = args

        self.interactionBox = pygame.Rect(x, y, self.size[0], self.size[1])
        self.action = action

        self.colourScheme = colourScheme
        if not self.colourScheme:
            self.colourScheme = {
                "unselect": (0, 0, 0),
                "hover": (50, 50, 50),
                "select": (100, 100, 100)
            }

        if not textures:
            self.textures = [pygame.Surface((50, 50))]
        self.size = self.textures[0].get_size()

        if not textures:
            self.textures[0].fill((255, 255, 255))


        self.state = state # Number value for texture number
        self.hover = False
        self.select = False

    def draw(self, screen):
        # This is a copy so that the changes do not become additive
        currentTexture = self.textures[self.state].copy()

        # "Tints" the Surface based on state. self.colourScheme can be {"select": (0, 0, 0, 0), (...)} to disable the effect.
        if self.select:
            tintColour = self.colourScheme["select"]
        elif self.hover:
            tintColour = self.colourScheme["hover"]
        else:
            tintColour = self.colourScheme["unselect"]

        currentTexture.fill(tintColour, special_flags=pygame.BLEND_SUB)

        # Draws the texture to the screen
        screen.blit(currentTexture, self.position)

    def handleEvent(self, event, posOffset:tuple=(0, 0)):
        if event.type == pygame.MOUSEMOTION:
            self.hover = True if self.interactionBox.collidepoint(pygame.mouse.get_pos()[0]+posOffset[0], pygame.mouse.get_pos()[1]+posOffset[1]) else False

        # If the hotkey is pressed, or the button is clicked, do the action and play the sfx
        try:
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover) or (event.type == pygame.KEYDOWN and event.key in self.hotkeys):
                self.select = True if not self.toggle else not self.select
                
                # Completes self.action, with any provided arguments
                try:
                    if self.args:
                        self.action(self.args[0])
                    else:
                        self.action()
                except Exception as e:
                    output.log(f"Error completing action: {e}")

                try:
                    if self.sfx:
                        self.sfx.play()
                except AttributeError as e:
                    output.log(f"Error loading 'self.sfx': {e}")

                # Cycles through textures. SHOULDN'T be wrong, but haven't tested.
                if self.cycle:
                    self.state += 1
                    if self.state + 1 > len(self.textures):
                        self.state = 0

                    # Updates the size and Rect of the button if changed.
                    self.size = self.textures[self.state].get_size()
                    self.interactionBox = pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
            
            # Inverse. Unless it is set to not toggle, self.select is set to False.
            elif (event.type == pygame.MOUSEBUTTONUP and not self.toggle and event.button == 1) or (event.type == pygame.KEYUP and not self.toggle and event.key in self.hotkeys):
                self.select = False
        except Exception as e:
            output.log(f"Error handling input: {e}")

#   TODO: - Add tint method (copy the self.textures[0] surface w/ value of colourScheme[state])
class slider:
    """A slider with a knob, each with a unique texture, with a configurable value set."""
    def __init__(self, x: int, y: int, value: int=100, textures:list=[], colourScheme:dict={"unselect": (0, 0, 0, 0),"hover": (0, 0, 0, 100),"select": (0, 0, 0, 150)}, minValue:int=0, maxValue:int=100, w: int=140, h: int=16):
        self.value = value
        self.minValue = minValue
        self.maxValue = maxValue

        self.value = value
        self.textures = textures
        self.colourScheme = colourScheme
        
        if not textures:
            rect = pygame.Surface((w, h))
            knobSurface = pygame.Surface((h*1.3, h*1.3), pygame.SRCALPHA)

            self.h = h
            self.w = w

            rect.fill((255, 255, 255))

            self.textures = [rect, knobSurface]
            self.defaultTextures = True
        else:
            self.defaultTextures = False

            self.w = self.textures[0].get_width()
            self.h = self.textures[0].get_height()
            h = self.h
            w = self.w

        self.position = (x, y)
        self.valueRange = maxValue - minValue
        self.knobX = (x + (value - minValue) / self.valueRange * w) - h//2

        self.collisionBox = pygame.Rect(x,y,w,h)
        self.knobBox = pygame.Rect(self.knobX, y, w, h)

        self.select = False
        self.hover = False

    def draw(self, screen):
        # Simplified equation to get the default "centre" for the knob's y position
        knobYPosition = self.position[1] - (self.textures[1].get_width())//2 + self.h//2

        # Render the rectangle at the position, and the knob in the centre of the rectangle
        screen.blit(self.textures[0], self.position)
        screen.blit(self.textures[1], (self.knobX, knobYPosition))

        # If the textures are default, the "knob" Surface is actually transparent, so it needs a circle rendered on top of it
        if self.defaultTextures:
            pygame.draw.circle(self.textures[1], (122, 122, 122), self.textures[1].get_rect().center, (self.textures[1].get_width())//2)

    def handleEvent(self, event, posOffset:tuple=(0, 0)):
        # Event handling
        if self.collisionBox.collidepoint(pygame.mouse.get_pos()[0]+posOffset[0], pygame.mouse.get_pos()[1]+posOffset[1]) or self.knobBox.collidepoint(pygame.mouse.get_pos()[0]+posOffset[0], pygame.mouse.get_pos()[1]+posOffset[1]):
            # If pressed or hovered over, set respective bool to True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.select = True
            elif event.type == pygame.MOUSEMOTION:
                self.hover = True
        # Otherwise, set respective bool to False
        else:
            self.hover = False
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.select = False

        # Moves the knob, sets the value
        if self.select:
            # Set the knob position's x value to the mouse, then centre it.
            mouseX = pygame.mouse.get_pos()[0]+posOffset[0]
            self.knobX = mouseX - (self.textures[1].get_width()//2)
            self.knobBox.x = self.knobX

            # Clamp the knob's x position between the min and max
            self.knobX = max(self.position[0]-(self.textures[1].get_width()//2), min(self.knobX, self.position[0]+self.collisionBox.width-(self.textures[1].get_width()//2)))

            # Gets a multiplier using the current position vs the width, then uses that to find the actual value.
            # To account for float inaccuracy, it is then rounded to 4dp.
            # This DOES make it slightly innacurate, but it probably won't be used for anything that requires that much accuracy.
            tempValue = self.knobX - self.valueRange + (self.textures[1].get_width()//2)
            multiplier = (tempValue/self.collisionBox.width)
            self.value = round(multiplier*self.valueRange, 4)

# TODO: -Add texture support
#           - Maybe only texture for outside?
#           - Inside being a filled box still.
#       - Add tint method (copy the self.textures[0] surface w/ alpha value of colourScheme[state][3])
class filledSlider:
    """A slider that, instead of a knob, has a filled rectangle filling it. DOES NOT SUPPORT TEXTURES."""
    def __init__(self, x: int, y: int, value: int=100, colourScheme:dict={"unselect": (0, 0, 0, 0),"hover": (0, 0, 0, 100),"select": (0, 0, 0, 150)}, minValue:int=0, maxValue:int=100, w: int=140, h: int=16):
        self.value = value
        self.minValue = minValue
        self.maxValue = maxValue
        self.valueRange = maxValue - minValue
        self.position = (x, y)
    
        self.colourScheme = colourScheme
        
        self.collisionBox = pygame.Rect(x,y,w,h)

        multiplier = (value - minValue) / self.valueRange
        progressBarWidth = w * multiplier

        rect = pygame.Surface((w, h))
        progressRect = pygame.Surface((progressBarWidth, h))

        self.h = h
        self.w = w

        rect.fill((200, 200, 200))
        progressRect.fill((255, 255, 255))

        self.textures = [rect, progressRect]
        self.defaultTextures = True

        self.select = False
        self.hover = False

    def draw(self, screen):
        # For some reason, the filled bar would turn black if the width ever reched zero. This prevents that.
        self.textures[1].fill((255, 255, 255))

        # Render the rectangle at the position, and the knob in the centre of the rectangle
        screen.blit(self.textures[0], self.position)
        screen.blit(self.textures[1], self.position)

    def setValue(self, newValue):
        if newValue < 0 or newValue > self.maxValue:
            output.log("New value is out of range!")
        self.value = max(0, min(newValue, self.maxValue))

        multiplier = (self.value - self.minValue) / self.valueRange
        self.progressBarWidth = self.w * multiplier
        self.textures[1] = pygame.transform.scale(self.textures[1], (self.progressBarWidth, self.h))

    def handleEvent(self, event, posOffset:tuple=(0, 0)):
        # Event handling
        if self.collisionBox.collidepoint(pygame.mouse.get_pos()[0]+posOffset[0], pygame.mouse.get_pos()[1]+posOffset[1]):
            # If pressed or hovered over, set respective bool to True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.select = True
            elif event.type == pygame.MOUSEMOTION:
                self.hover = True
        # Otherwise, set respective bool to False
        else:
            self.hover = False
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.select = False

        # Expands the "knob", sets the value
        if self.select:
            self.progressBarWidth = max(0, min(pygame.mouse.get_pos()[0]+posOffset[0]-self.position[0], self.collisionBox.width))

            self.textures[1] = pygame.transform.scale(self.textures[1], (self.progressBarWidth, self.h))

            # Gets the percentage filled.
            multiplier = (self.progressBarWidth/self.collisionBox.width)
            self.value = round(multiplier*self.valueRange, 4)

class window:
    """A self-contained window capable of drawing and handling element events."""
    def __init__(self, x:int, y:int, width:int=500, height:int=500, elements:list=[], windowColour=(220, 220, 255), rendering:bool=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.elements = elements
        self.surface = pygame.Surface((width, height))
        self.surface.fill(windowColour)
        self.rect = pygame.Rect(x, y, width, height)

        self.windowColour = windowColour

        self.rendering = rendering

        # Adds an exit button, for convenience.
        exitTexture = pygame.image.load("./icons/exit.png")
        exitButton = button(width-16, 0, action=self.exitWindow, cycle=False, toggle=False, textures=[exitTexture])
        elements.append(exitButton)

    def draw(self, screen):
        self.surface.fill(self.windowColour)

        if self.rendering:
            for element in self.elements:
                element.draw(self.surface)
            
            # Blits the actual screen onto the base screen.
            screen.blit(self.surface, (self.x, self.y))

    def handleEvent(self, event):
        if self.rendering:
            for element in self.elements:
                if hasattr(element, "handleEvent"):
                    element.handleEvent(event, (-self.x, -self.y))
            pygame.display.flip()

    def exitWindow(self):
        self.rendering = not self.rendering

# FIXME can't uncheck
class checkbox:
    """A very simple checkbox feature with the built-in option to use a label."""
    def __init__(self, x:int, y:int, label:str="", size:tuple=(20, 20), defaultState:bool=False):
        self.rect = pygame.Rect(x, y, size[0], size[1])
        self.size = size
        self.label = label
        self.state = defaultState

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        if self.state:
            pygame.draw.line(surface, (255, 255, 255), self.rect.topleft, self.rect.bottomright, 2)
            pygame.draw.line(surface, (255, 255, 255), self.rect.topright, self.rect.bottomleft, 2)

        font = pygame.font.Font(None, 24)
        labelText = font.render(self.label, True, (255, 255, 255))
        surface.blit(labelText, (self.rect.x + self.size[0] + 5, self.rect.y))
    
    def handleEvent(self, event, offset=(0, 0)):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos[0] + offset[0], event.pos[1] + offset[1]):
                self.state = not self.state

def fileExplorer(mode=0):
    import tkinter as tk
    import tkinter.filedialog

    top = tk.Tk()
    top.withdraw()

    try:
        mode = int(mode)
    except:
        raise ValueError("Invalid mode. Mode must be an integer (1 or 0).")

    if mode == 0:
        fileName = tkinter.filedialog.askopenfilename(parent=top)
    elif mode == 1:
        fileName = tkinter.filedialog.askdirectory(parent=top)
    else:
        raise ValueError("Invalid mode. Use 0 for file selection or 1 for folder selection.")
        
    top.destroy()
    
    return fileName