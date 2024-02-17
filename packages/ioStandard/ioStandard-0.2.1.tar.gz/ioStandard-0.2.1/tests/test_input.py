import pygame
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ioStandard.input import inputBox, slider, button, checkbox, fileExplorer
from ioStandard.output import text, progressBar

pygame.init()
clock = pygame.time.Clock()

width, height = 800, 600
sc = pygame.display.set_mode((width, height))
pygame.display.set_caption("Input Test")

def test01():
    # Create UI Elements
    testBox = inputBox(100, 100, prompt="Enter Text: ")
    currentText = text(100, 164, "")
    outputText = text(100, 196, "")

    inputSlider = slider(0, 250, width)
    sliderText = text(100, 282, "")
    percentText = text(100, 314, "")
    progressBarTest = progressBar(0, 200, width)

    buttonTest = button(100, 350, 1, action=fileExplorer)

    buttonTestToggle = button(100, 400, action=lambda: print("Pressed"), toggle=True)

    checkBoxTest = checkbox(100, 500)

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            testBox.handleEvent(event)
            inputSlider.handleEvent(event)
            buttonTest.handleEvent(event)
            buttonTestToggle.handleEvent(event)
            checkBoxTest.handleEvent(event)

        # Logic
        currentText.text = testBox.text
        outputText.text = testBox.finalText
        sliderText.text = f"Value: {inputSlider.value}"
        percentText.text = f"Value: {inputSlider.value}%"
        progressBarTest.setValue(inputSlider.value)

        if buttonTestToggle.select:
            print("Toggled On.")

        # Render
        sc.fill((255,214,186))
        testBox.draw(sc)
        currentText.draw(sc)
        outputText.draw(sc)
        inputSlider.draw(sc)
        sliderText.draw(sc)
        percentText.draw(sc)
        buttonTest.draw(sc)
        buttonTestToggle.draw(sc)
        checkBoxTest.draw(sc)
        progressBarTest.draw(sc)

        pygame.display.flip()

    pygame.quit()

test01()