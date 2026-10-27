import curses
import sys
import os
import time

from screen import Screen
from file import File
from input import get_keybind, resolve_keybind
from editor_mode import EditorMode
from editor import Editor
import command

TAB_WIDTH = 4


class State:
    def __init__(self):
        self.file_path = "*NEW*"
        self.filename = "*NEW*"  # only basename, displayed in status line etc.
        self.mode = "normal"  # mode for interpreting input
        self.ending = False  # whether to quit the application yet.


def create_prompt(stdscr, x, y, width, message):
    """
    Creates a prompt screen, lets the user do something and then returns the value.
    """
    prompt_screen = Screen(len(message) + 1, curses.LINES-2, curses.COLS, stdscr, stype="prompt")


def handle_input(state, editor: Editor):
    # get ncurses char.
    key_ch = editor.screen.curses_screen.get_wch()
    # turn this char into a keybind string.
    key_str = get_keybind(key_ch, editor.screen.curses_screen)

    if key_str == "RESIZE":
        editor.screen.handle_resize()
        return

    # Check keybindings for a command for this keybind.
    command_str = resolve_keybind(key_str)
    if not command_str:
        editor.screen.draw_status_message(f"Unbound key '{key_str}'.")
        return

    # Look up the command in the command registry, and if found,
    # execute the command.
    resolved_command = editor.command_registry.resolve(command_str)
    if resolved_command and command_str == "insert-char":
        # For 'insert-char', pass the key char along as argument.
        editor.command_registry.execute(command_str, editor, arg=key_ch)
    elif resolved_command:
        editor.command_registry.execute(command_str, editor)
    else:
        editor.screen.draw_status_message(f"No such command '{command_str}'.")

    # Redraw the screen's dirty lines if there are any.
    if len(editor.screen.dirty_lines) > 0:
        editor.screen.draw_screen()


def register_basic_commands(cmd_reg: 'command.CommandRegistry'):
    """
    Registers the most basic commands into the command registry.
    Includes things like basic movement and typing.
    """
    # Movement commands
    cmd_reg.register(command.move_left_cmd)
    cmd_reg.register(command.move_right_cmd)
    cmd_reg.register(command.move_up_cmd)
    cmd_reg.register(command.move_down_cmd)

    # Insert commands
    cmd_reg.register(command.insert_tab_cmd)
    cmd_reg.register(command.insert_newline_cmd)
    cmd_reg.register(command.insert_char_cmd)

    # Deletion commands
    cmd_reg.register(command.delete_line_cmd)
    cmd_reg.register(command.delete_forward_cmd)
    cmd_reg.register(command.delete_backward_cmd)

    # Save command
    cmd_reg.register(command.save_file_cmd)

    # Quit command
    cmd_reg.register(command.quit_cmd)

        
def main_loop(stdscr, file_path, state):
    # Set up curses
    curses.use_default_colors()
    curses.raw()
    stdscr.clear()
    # Set up editor dimensions
    editor_width = curses.COLS
    editor_height = curses.LINES
    # TODO: check this code as it defines the screen twice, but once with a file.
    if file_path:
        file = File(file_path)
        screen = Screen(0, 0, editor_width, editor_height, stdscr, file=file)
    else:
        screen = Screen(0, 0, editor_width, editor_height, stdscr)
    screen.draw_screen(redraw=True)
    # Create editor state instance.
    editor = Editor(editor_width, editor_height, screen)
    # This is there so the initial "Loaded in file" message can appear
    if not screen.message_shown:
        screen.draw_status()
    else:
        screen.message_shown = False
    screen.put_terminal_cursor()

    # Register commands
    register_basic_commands(editor.command_registry)

    while True:
        # Disable processing of ctrl+{c,z} etc.
        curses.raw()
        # check if we need to quit.
        if editor.mode == EditorMode.EXIT:
            return

        handle_input(state, editor)
        if screen.message_shown:
            # Remove status message after one loop iteration.
            screen.message_shown = False
        else:
            # Draw the status line only when no message is there.
            screen.draw_status()
        # After all the drawing, put the cursor back where it belongs.
        screen.put_terminal_cursor()


def main():
    # Windows check. ncurses does not work well on Windows if you do not
    # have curses and even then it still is buggy and works unexpectedly.
    # Therefore, for now, we do not support Windows!
    if os.name == 'nt':
        print("neot does not support Windows, due to ncurses not being supported\n"
              "and different behavior by Windows in the terminal which neot cannot\n"
              "yet account for. I apologize but in the future, since I do use Windows\n"
              "sometimes, I might add support with some caveats later.\n"
              "Just note neot's main platform is and will remain Linux.")
        exit(2)

    # TODO: Remove this 'state' object!
    state = State()
    file_path = None
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
        state.filename = os.path.basename(file_path)

    curses.wrapper(main_loop, file_path, state)


if __name__ == "__main__":
    main()
