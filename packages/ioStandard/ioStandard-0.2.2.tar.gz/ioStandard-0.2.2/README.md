# ioStandard Library

The `ioStandard` library provides a simple and customizable set of input and output elements for Pygame applications. This library includes a text box (`textBox`), slider (`slider`), button (`button`), check box (`checkBox`), file uploader (`fileUploader`), text display (`text`), and progress bar (`progressBar`).

## Installation

To use `ioStandard` in your Pygame project, install it using the following command:

```bash
pip install ioStandard
```

## Usage

### `textBox`

The `textBox` class allows you to create customizable input boxes. Each input box can have its own theme, which defines the colors for various states such as unselected, hovering, and selected.

#### Example:

```python
import pygame
from ioStandard import textBox

# Initialize Pygame
pygame.init()

# Create a Pygame window
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Input Box Example")

# Create a textBox instance
input_box = textBox(100, 100, prompt="Enter Text: ", fontSize=24)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            input_box.handleEvent(event)

    # Render the input box
    input_box.draw(screen)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
```

### `text`

The `text` class is used for rendering text on the screen. It allows you to customize the text's position, content, and theme.

#### Example:

```python
import pygame
from ioStandard import text

# Initialize Pygame
pygame.init()

# Create a Pygame window
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Text Display Example")

# Create a text instance
output_text = text(100, 200, text="Hello, ioStandard!", fontSize=32)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Render the text
    output_text.draw(screen)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
```

### `slider`

The `slider` class provides a slider element for selecting a value within a specified range.

#### Example:

```python
import pygame
from ioStandard import slider, text

# Initialize Pygame
pygame.init()

# Create a Pygame window
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Slider Example")

# Create a slider instance
input_slider = slider(100, 100, 200, maxValue=10, theme={"hover": (200, 200, 200)})

# Create a text instance to display slider value
slider_text = text(100, 150)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            input_slider.handleEvent(event)

    # Render the slider
    input_slider.draw(screen)

    # Display the slider value
    slider_text.text = f"Value: {input_slider.value}"
    slider_text.draw(screen)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
```

### `button`

The `button` class represents a clickable button element. It can be used for triggering actions in response to user input.

#### Example:

```python
import pygame
from ioStandard import button, text

# Initialize Pygame
pygame.init()

# Create a Pygame window
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Button Example")

# Create a button instance
click_button = button(100, 100, lambda: print("Button Clicked"))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            click_button.handleEvent(event)

    # Render the button
    click_button.draw(screen)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
```

### `checkBox`

The `checkBox` class represents a toggleable check box element. It can be used for creating options with binary states.

#### Example:

```python
import pygame
from ioStandard import checkBox, text

# Initialize Pygame
pygame.init()

# Create a Pygame window
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Check Box Example")

# Create a checkBox instance
toggle_checkbox = checkBox(100, 100, lambda: print("Toggled"))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            toggle_checkbox.handleEvent(event)

    # Render the check box
    toggle_checkbox.draw(screen)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
```

### `fileUploader`

The `fileUploader` class provides a file selection interface for the user. It allows the user to browse and select files or folders.

#### Example:

```python
import pygame
from ioStandard import fileUploader, text

# Initialize Pygame
pygame.init()

# Create a Pygame window
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("File Uploader Example")

# Create a fileUploader instance
upload_file = fileUploader(100, 100)

# Create a text instance to display selected file/folder path
selected_file_text = text(100, 150)

# Main loop


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            upload_file.handleEvent(event)

    # Render the file uploader
    upload_file.draw(screen)

    # Display the selected file/folder path
    selected_file_text.text = f"Selected: {upload_file.selected_file}"
    selected_file_text.draw(screen)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
```

### `progressBar`

The `progressBar` class represents a progress bar element that visually indicates the progress of a task.

#### Example:

```python
import pygame
from ioStandard import progressBar, text

# Initialize Pygame
pygame.init()

# Create a Pygame window
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Progress Bar Example")

# Create a progressBar instance
progress_bar = progressBar(100, 100, 200, maxValue=100, theme={"hover": (200, 200, 200)})

# Create a text instance to display progress value
progress_text = text(100, 150)

# Main loop
running = True
while running:
    for event in pygame.event.get():
       

 if event.type == pygame.QUIT:
            running = False

    # Update the progress value (for example, based on some task completion)
    progress_bar.setValue(50)

    # Render the progress bar
    progress_bar.draw(screen)

    # Display the progress value
    progress_text.text = f"Progress: {progress_bar.progress}%"
    progress_text.draw(screen)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
```

## Themes

Both `textBox`, `text`, `slider`, `button`, `checkBox`, `fileUploader`, and `progressBar` classes support theming to customize the appearance of elements. The default theme includes colors for unselected, hovering, and selected states, as well as text and prompt colors.

To customize the theme, you can pass a dictionary of color values when creating an instance of each class.

### Example Theme:

```python
custom_theme = {
    "unselect": (255, 0, 0),    # Red for unselected state
    "hover": (0, 255, 0),       # Green for hovering state
    "select": (0, 0, 255),      # Blue for selected state
    "txt": (255, 255, 255),     # White text color
    "prompt": (128, 128, 128)   # Gray prompt color
}

# Create a textBox instance with a custom theme
custom_input_box = textBox(200, 100, theme=custom_theme)
```

## License

This library is distributed under the MIT license. See the `LICENSE` file for details.

Feel free to contribute or report issues on [GitHub](https://github.com/Jackfiddilydimss/ioStandard).