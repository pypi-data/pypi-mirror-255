"""
# Debugging utilities

- Owners: piotrm
"""

from __future__ import annotations

from builtins import print as builtin_print
import inspect
import io
from pathlib import Path
import sys
import traceback
from types import TracebackType
from typing import Any, Callable, Tuple

from truera.client.util.python_utils import get_code_location
from truera.client.util.python_utils import get_def_site
from truera.client.util.python_utils import get_frameinfo


def is_notebook() -> bool:
    # https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


class Capture(object):
    """
    A class to manage the capture of outputs within and without a notebook.
    Handles std{in,out} as well as IPython display.

    Each instance also comes with the appropriate method for outputting
    text/other to the appropriate terminal type (stdout or IPython).
    """

    @staticmethod
    def for_term() -> Capture:
        """
        Create a capture instance appropriate for inferred terminal type.
        """

        # NOTE(piotrm): Temporarily disabling the notebook output/capture.
        #if is_notebook():
        #    return CaptureNotebook()
        #else:
        return CaptureStd()

    def __init__(self):
        # Track exceptions raised during capturing.
        self.exn = None

    def __enter__(self):
        # Required for handling "with Capture() ...".
        pass

    def __exit__(self, typ, value, tb):
        # Required for handling "with Capture() ...".
        self.exn = value
        self.exn_str = ""
        if value is not None:
            self.exn_str = str(traceback.format_exc())
            # self.exn_str += str(traceback.format_tb(tb))
            # self.exn_str = str(sys.exc_info()[2])
        return False

    def display(self, prefix="") -> None:
        """
        Output the captured content with possibly a prefix prepended.
        """
        pass

    def ok(self) -> bool:
        """
        Was there an exception raised during capture?
        """
        return self.exn is None

    def summary(self) -> Any:
        """
        Produce a string summary of captured outptus in terminal-appropriate
        form.
        """
        pass

    def exn_summary(self) -> str:
        """
        Produce a string describing a raised exception during the capture
        process.
        """
        if self.exn is not None:
            return self.exn_str
        else:
            return ""


class CaptureStd(Capture):
    """
    Capture / output to/from stdout and stderr.
    """

    def __init__(self):
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.original_stdout = None
        self.original_stderr = None

    def display(self, prefix=""):
        sum = self.summary()
        builtin_print(f"\n{prefix}".join(sum.split("\n")))

    def summary(self):
        sum = ""
        sum += self.stdout.getvalue()

        err = self.stderr.getvalue()
        if err != "":
            sum += "\n\nSTDERR:\n\n"
            sum += err

        exn = self.exn_summary()
        if exn != "":
            sum += "\n\nEXCEPTION:\n\n"
            sum += exn

        return sum

    def __enter__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        sys.stdout = self.stdout
        sys.stderr = self.stderr

        return self

    def __exit__(self, typ, value, tb):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

        return Capture.__exit__(self, typ, value, tb)


class CaptureNotebook(Capture):
    """
    Capture to/from IPython notebooks.
    """

    def __init__(self):
        from ipywidgets import widgets

        self.output = widgets.Output()

    def __enter__(self):
        self.output.__enter__()

        return self

    def display(self, prefix=""):
        from IPython.display import clear_output
        from IPython.display import display
        from ipywidgets import widgets

        display(widgets.HBox([widgets.HTML(prefix), self.summary()]))

    def summary(self):
        return self.output

    def __exit__(self, typ, value, tb):
        self.output.__exit__(typ, value, tb)
        return Capture.__exit__(self, typ, value, tb)


def render_exception(exc: Exception):
    """
    Create a representation of an exception that includes minimal frame
    information for exception raise site. This differs in the output of
    str(Exception) especially for assertion exceptions that do not print out the
    raise site.
    """

    tb_info = traceback.extract_tb(exc.__traceback__)
    filename, line_number, function_name, text = tb_info[-1]
    message = f"{str(type(exc).__name__)} {filename}:{line_number}:{function_name}:{text}"
    text = str(exc)
    if text:
        message += "\n" + retab(text, "\t")

    message += "\n".join(traceback.format_tb(tb=exc.__traceback__))

    return message


def retab(s, tab: str = "  ", tab_first: bool = True):
    """
    Changes the tab/margin of the given string `s` to the given `tab`. If
    `tab_first` is provided, also adds the marging to the first line of `s`.
    """

    if tab_first:
        return "\n".join([tab + s for s in s.split("\n")])
    else:
        return ("\n" + tab).join(s.split("\n"))


def _get_margin(s):
    if len(s) == 0:
        return ""

    margin = ""

    while s[0] in [" ", "\t"]:
        margin += s[0]
        s = s[1:]

    return margin


def code_location_string(locinfo) -> str:
    """
    Return a string representation of a callsite of frame or other object
    indicated by `locinfo`. Supported are `inspect.FrameInfo` that represent a
    callsite, `tracepoint` which represent the site of an exception throw, and
    function which points to its definition.

    Returned string has the format as below which some IDE's can parse to be
    clickable to navigate to mentioned code locations.

       FILENAME:LINENO
    """

    file, line = get_code_location(locinfo)

    return f"{file}:{line}"


def print(
    *objects,
    sep=' ',
    end='\n',
    file=None,
    flush=False,
    max_cols: int = 200
) -> None:
    """
    A print variant that prepends a margin on each line that is retrieved from
    the margin at the site where it was invoked. Other than max_cols, the
    signature is the same as `builtins.print`.
    """

    fi = get_frameinfo(depth=2)
    line = fi.code_context[0]

    name = fi.function
    margin = list(_get_margin(line))

    if len(name) < len(margin) - 1:
        margin[0:len(name)] = list(name)
    else:
        if len(margin) >= 3:
            margin = list(name[0:len(margin)])
            margin[-3:] = list(".. ")
        else:
            pass

    margin = ''.join(margin)

    content = sep.join(
        map(lambda obj: obj if isinstance(obj, str) else str(obj), objects)
    )

    if max_cols is not None:
        split_lines = []
        for line in content.split("\n"):
            prefix_line = margin + line
            while len(prefix_line) > max_cols:
                split_lines.append(prefix_line[0:max_cols])
                prefix_line = margin + prefix_line[max_cols:]

            split_lines.append(prefix_line)

        content = "\n".join(split_lines)
    else:
        content = "\n".join([margin + line for line in content.split("\n")])

    builtin_print(content, end=end, file=file, flush=flush)
