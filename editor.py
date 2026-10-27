# This file contains editor definitions.
from screen import Screen
from editor_mode import EditorMode
import command
        
# This class contains everything the editor needs to function.
class Editor:
    screen: Screen
    width: int
    height: int
    command_registry: 'command.CommandRegistry'
    mode: EditorMode

    def __init__(self, width, height, screen):
        self.screen = screen
        self.width = width
        self.height = height
        self.command_registry = command.CommandRegistry()
        self.mode = EditorMode.NORMAL
