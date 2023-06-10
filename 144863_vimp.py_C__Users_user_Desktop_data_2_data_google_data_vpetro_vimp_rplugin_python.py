import neovim
import os
from datetime import datetime


@neovim.plugin
class VimpBuffers(object):
    def __init__(self, vim):
        self.vim = vim

    @neovim.command("ToggleTerminalBuffer")
    def toggle_terminal_buffer(self):
        current_buffer = self.vim.current.buffer
        # find the currently open terminal and close it
        for idx, window in enumerate(self.vim.current.tabpage.windows, 1):
            if window.buffer.name.startswith("term://"):
                self.vim.command("{0}wincmd w".format(idx))
                self.vim.command("wincmd c".format(idx))

                # go back to the window where the command was executed from
                window_number = self.vim.eval(
                    "bufwinnr({0})".format(current_buffer.number)
                )
                self.vim.command("{0}wincmd w".format(window_number))

                return

        # find the terminal buffer in the list of buffers, open it in a split
        for buf in self.vim.buffers:
            if buf.name.startswith("term://"):
                self.vim.command("botright sb {0}".format(buf.number))
                return

        # create a new terminal when there is no terminal buffer
        self.vim.command("botright new")
        self.vim.command(":terminal")

    @neovim.command("ShowTodaysNotes")
    def open_log_file(self):
        filepath = os.path.join(
            os.environ.get("NOTES_DIR"),
            "%s.md" % datetime.now().strftime("%Y-%m-%d")
        )
        self.vim.command("vs %s" % filepath)
