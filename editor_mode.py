from enum import Enum

# Editor modes. Right now there are no modes so we use the new mode system for
# quitting.
class EditorMode(Enum):
    NORMAL = 0
    EXIT = 1
