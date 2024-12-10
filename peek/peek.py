#   _ __    ___   ___ | | __
#  | '_ \  / _ \ / _ \| |/ /
#  | |_) ||  __/|  __/|   <
#  | .__/  \___| \___||_|\_\
#  |_| like print, but easy.

__version__ = "1.8.3"

"""
See https://github.com/salabim/peek for details

(c)2024 Ruud van der Ham - rt.van.der.ham@gmail.com

Inspired by IceCream "Never use print() to debug again".
Also contains some of the original code.
IceCream was written by Ansgar Grunseid / grunseid.com / grunseid@gmail.com
"""

import inspect
import sys
import datetime
import time
import textwrap
import contextlib
import functools
import logging
import collections
import numbers
import ast
import os
import copy
import traceback
import executing
import types
import pprint
import builtins

from pathlib import Path

Pythonista = sys.platform == "ios"
if Pythonista:
    import console
    import clipboard
else:
    import colorama
    import pyperclip

try:
    import tomlib
except ModuleNotFoundError:
    import tomli as tomlib

nv = object()


def perf_counter():
    return time.perf_counter() if _fixed_perf_counter is None else _fixed_perf_counter


colors = dict(
    black="\033[0;30m",
    red="\033[0;31m",
    green="\033[0;32m",
    yellow="\033[0;33m",
    blue="\033[0;34m",
    magenta="\033[0;35m",
    cyan="\033[0;36m",
    white="\033[0;37m",
)
colors[""] = "\033[0m"


ansi_to_hexa = {
    "\033[0;30m": "#000000",
    "\033[0;31m": "#FF0000",
    "\033[0;32m": "#00FF00",
    "\033[0;33m": "#FFFF00",
    "\033[0;34m": "#0080FF",
    "\033[0;35m": "#FF00FF",
    "\033[0;36m": "#00FFFF",
    "\033[0;37m": "#FFFFFF",
    "\033[0m": "",
}


def flatten(x):
    for item in x:
        if isinstance(item, str):
            yield item
        else:
            try:
                yield from flatten(item)
            except TypeError:
                yield item


# def colorname_to_rgb(colorname):
#    return tuple(int(ansito_rgb[colorname.lower()][i : i + 2], 16) / 255 for i in range(1, 7, 2))


def check_validity(item, value, message=""):
    if value is None:
        return

    if item in ("color", "color_value"):
        if not value or (isinstance(value, str) and value.lower() in colors):
            return

    elif item in ("line_length", "enforce_line_length"):
        if isinstance(value, numbers.Number) and value > 0:
            return

    elif item == "indent":
        if isinstance(value, numbers.Number) and value >= 0:
            return

    elif item == "level":
        if isinstance(value, numbers.Number) or value == "":
            return

    elif item == "wrap_indent":
        if isinstance(value, numbers.Number):
            if value > 0:
                return
        else:
            return

    else:
        return

    raise ValueError(f"incorrect {item}: {value}{message}")


class show_level:
    def __new__(cls, *values, min=None, max=None, message=""):
        if len(values) == 0 and min is None and max is None:
            return _show_level
        return super().__new__(cls)

    def __init__(self, *values, min=None, max=None, message=""):
        result = ["False"]
        if min is not None or max is not None:
            if values:
                raise ValueError(f"min or max cannot be combined with other specifiers (={values})")
            if min is not None and max is not None and min > max:
                raise ValueError(f"min (={min}) > max (={max})")
            if min is None:
                min = ""
            else:
                if min < 0:
                    min = f"({min})"
            if max is None:
                max = ""
            else:
                if max < 0:
                    max = f"({max})"
            values = [f"{min}-{max}"]

        valuex = tuple(flatten(values))
        for element in valuex:
            if isinstance(element, numbers.Number):
                result.append(f"level == {element}")
            elif element is None:
                ...
            elif isinstance(element, str):
                elementx = element.strip().replace("(-", "$$$").replace(")", "").replace("-", "/").replace("$$$", "-")
                if elementx.lower() == "all":
                    elementx = "/"
                if elementx == "":
                    ...
                elif "/" in elementx:
                    part0, part1 = elementx.split("/", 1)
                    if part0 == "":
                        part0 = "-1e30"
                    if part1 == "":
                        part1 = "1e30"
                    try:
                        float(part0)
                        float(part1)
                    except ValueError as e:
                        raise ValueError(f"incorrect show_level spec: {element} in {values} {message}") from None
                    if float(part0) > float(part1):
                        raise ValueError(f"incorrect order in show_level spec: {element} in {values} {message}")
                    result.append(f"{part0} <= level <= {part1}")
                else:
                    try:
                        float(elementx)
                    except ValueError as e:
                        raise ValueError(f"incorrect show_level spec: {element} in {values} {message}") from None
                    result.append(f"level == {element}")
            else:
                raise ValueError(f"incorrect show_level spec: {element} in {values} {message}")

        expression = f"level != '' and ({' or '.join(result)})"

        global _show_level
        global _show_level_expression
        self.saved_show_level = _show_level
        self.saved_show_level_expression = _show_level_expression
        _show_level = values[0] if len(values) == 1 else values
        _show_level_expression = expression

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, exc_tb):
        global _show_level
        global _show_level_expression
        _show_level = self.saved_show_level
        _show_level_expression = self.saved_show_level_expression


def peek_pformat(obj, width, compact, indent, depth, sort_dicts, underscore_numbers):
    return pprint.pformat(obj, width=width, compact=compact, indent=indent, depth=depth, sort_dicts=sort_dicts, underscore_numbers=underscore_numbers).replace(
        "\\n", "\n"
    )


class Source(executing.Source):
    def get_text_with_indentation(self, node):
        result = self.asttokens().get_text(node)
        if "\n" in result:
            result = " " * node.first_token.start[1] + result
            result = dedent(result)
        result = result.strip()
        return result


class Default(object):
    pass


default = Default()


def change_path(new_path):  # used in tests
    global Path
    Path = new_path


_fixed_perf_counter = None

_show_level = "-"
_show_level_expression = "True"

attrs = set()  # ***


def fix_perf_counter(val):  # for tests
    global _fixed_perf_counter
    _fixed_perf_counter = val


shortcut_to_name = {
    "pr": "prefix",
    "o": "output",
    "sln": "show_line_number",
    "st": "show_time",
    "sd": "show_delta",
    "sdi": "sort_dicts",
    "un": "underscore_numbers",
    "se": "show_enter",
    "sx": "show_exit",
    "stb": "show_traceback",
    "e": "enabled",
    "ll": "line_length",
    "c": "compact",
    "i": "indent",
    "de": "depth",
    "wi": "wrap_indent",
    "cs": "context_separator",
    "sep": "separator",
    "es": "equals_separator",
    "vo": "values_only",
    "voff": "values_only_for_fstrings",
    "rn": "return_none",
    "col": "color",
    "colv": "color_value",
    "l": "level",
    "ell": "enforce_line_length",
    "dl": "delta",
}


def set_defaults():
    default.prefix = ""
    default.output = "stdout"
    default.serialize = pprint.pformat
    default.show_line_number = False
    default.show_time = False
    default.show_delta = False
    default.sort_dicts = False
    default.underscore_numbers = False
    default.show_enter = True
    default.show_exit = True
    default.show_traceback = False
    default.enabled = True
    default.line_length = 80
    default.compact = False
    default.indent = 1
    default.depth = 1000000
    default.wrap_indent = "    "
    default.context_separator = " ==> "
    default.separator = ", "
    default.equals_separator = "="
    default.values_only = False
    default.values_only_for_fstrings = False
    default.return_none = False
    default.color = ""
    default.color_value = ""
    default.level = 0
    default.enforce_line_length = False
    default.one_line_per_pairenforce_line_length = False
    default.start_time = perf_counter()


def apply_toml():
    def process(config):
        for k, v in config.items():
            if k in ("serialize", "start_time"):
                raise ValueError("error in {toml_file}: key {k} not allowed".format(toml_file=toml_file, k=k))

            if k in shortcut_to_name:
                k = shortcut_to_name[k]
            if hasattr(default, k):
                check_validity(k, v, " in peek.toml file")
                setattr(default, k, v)
            else:
                if k == "show_level":
                    show_level(v, " in peek.toml file")
                elif k == "delta":
                    setattr(default, "start_time", perf_counter() - v)
                else:
                    raise ValueError("error in {toml_file}: key {k} not recognized".format(toml_file=toml_file, k=k))

    this_path = Path(".").resolve()
    for i in range(len(this_path.parts), 0, -1):
        toml_file = Path(this_path.parts[0]).joinpath(*this_path.parts[1:i], "peek.toml")
        if toml_file.is_file():
            with open(toml_file, "rb") as f:
                config = tomlib.load(f)
                process(config)
                return  # stop searching


def no_source_error(s=None):
    if s is not None:
        print(s)  # for debugging only
    raise NotImplementedError(
        """
Failed to access the underlying source code for analysis. Possible causes:
- decorated function/method definition spawns more than one line
- used from a frozen application (e.g. packaged with PyInstaller)
- underlying source code was changed during execution"""
    )


def return_args(args, return_none):
    if return_none:
        return None
    if len(args) == 0:
        return None
    if len(args) == 1:
        return args[0]
    return args


class _Peek:
    def __init__(
        self,
        prefix=nv,
        output=nv,
        serialize=nv,
        show_line_number=nv,
        show_time=nv,
        show_delta=nv,
        show_enter=nv,
        show_exit=nv,
        show_traceback=nv,
        sort_dicts=nv,
        underscore_numbers=nv,
        enabled=nv,
        line_length=nv,
        compact=nv,
        indent=nv,
        depth=nv,
        wrap_indent=nv,
        context_separator=nv,
        separator=nv,
        equals_separator=nv,
        values_only=nv,
        values_only_for_fstrings=nv,
        return_none=nv,
        color=nv,
        color_value=nv,
        level=nv,
        enforce_line_length=nv,
        delta=nv,
        _parent=nv,
        **kwargs,
    ):
        self._attributes = {}
        if _parent is nv:
            self._parent = default
        else:
            self._parent = _parent
        for key in vars(default):
            setattr(self, key, None)

        if _parent == default:
            func = "peek.new()"
        else:
            func = "peek.fork()"
        self.assign(kwargs, locals(), func=func)

        self.check()

    def __repr__(self):
        pairs = []
        for key in vars(default):
            if not key.startswith("__"):
                value = getattr(self, key)
                if not callable(value):
                    pairs.append(str(key) + "=" + repr(value))
        return "peek.new(" + ", ".join(pairs) + ")"

    def __getattr__(self, item):
        if item in shortcut_to_name:
            item = shortcut_to_name[item]
        if item == "delta":
            return perf_counter() - getattr(self, "start_time")

        if item == "show_level":
            return _show_level

        if item in self._attributes:
            if self._attributes[item] is None:
                return getattr(self._parent, item)
            else:
                return self._attributes[item]
        raise AttributeError("{item} not found".format(item=item))

    def __setattr__(self, item, value):
        if item in shortcut_to_name:
            item = shortcut_to_name[item]
        if item == "delta":
            item = "start_time"
            if value is not None:
                value = perf_counter() - value
        check_validity(item, value)
        if item == "show_level":
            raise NameError("reassigning show_level not allowed")

        if item in ["_attributes"]:
            super(_Peek, self).__setattr__(item, value)
        else:
            self._attributes[item] = value

    def do_show(self):
        return eval(_show_level_expression, dict(level=self.level)) and self.enabled

    def assign(self, shortcuts, source, func):
        for key, value in shortcuts.items():
            if key in shortcut_to_name:
                if value is not nv:
                    full_name = shortcut_to_name[key]
                    if source[full_name] is nv:
                        source[full_name] = value
                    else:
                        raise ValueError("can't use {key} and {full_name} in {func}".format(key=key, full_name=full_name, func=func))
            else:
                raise TypeError("{func} got an unexpected keyword argument {key}".format(func=func, key=key))
        for key, value in source.items():
            if value is not nv:
                if key == "delta":
                    key = "start_time"
                    if value is not None:
                        value = perf_counter() - value
                setattr(self, key, value)

    def fork(self, **kwargs):
        kwargs["_parent"] = self
        return _Peek(**kwargs)
        
    def to_clipboard(self, value, confirm=True):
        if Pythonista:
            clipboard.set(str(value))
        else:
            pyperclip.copy(str(value))
        if confirm:
            print(f'copied to clipboard: {value}')            
                 

    def __call__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", nv)
        output = kwargs.pop("output", nv)
        serialize = kwargs.pop("serialize", nv)
        show_line_number = kwargs.pop("show_line_number", nv)
        show_time = kwargs.pop("show_time", nv)
        show_delta = kwargs.pop("show_delta", nv)
        show_enter = kwargs.pop("show_enter", nv)
        show_exit = kwargs.pop("show_exit", nv)
        show_traceback = kwargs.pop("show_traceback", nv)
        sort_dicts = kwargs.pop("sort_dicts", nv)
        underscore_numbers = kwargs.pop("underscore_numbers", nv)
        enabled = kwargs.pop("enabled", nv)
        line_length = kwargs.pop("line_length", nv)
        compact = kwargs.pop("compact", nv)
        indent = kwargs.pop("indent", nv)
        depth = kwargs.pop("depth", nv)
        wrap_indent = kwargs.pop("wrap_indent", nv)
        context_separator = kwargs.pop("context_separator", nv)
        separator = kwargs.pop("separator", nv)
        equals_separator = kwargs.pop("equals_separator", nv)
        values_only = kwargs.pop("values_only", nv)
        values_only_for_fstrings = kwargs.pop("values_only_for_fstrings", nv)
        return_none = kwargs.pop("return_none", nv)
        color = kwargs.pop("color", nv)
        color_value = kwargs.pop("color_value", nv)
        level = kwargs.pop("level", nv)
        enforce_line_length = kwargs.pop("enforce_line_length", nv)
        delta = kwargs.pop("delta", nv)
        to_clipboard=kwargs.pop("to_clipboard", nv)
        as_str = kwargs.pop("as_str", nv)
        provided = kwargs.pop("provided", nv)
        pr = kwargs.pop("pr", nv)

        if pr is not nv and provided is not nv:
            raise TypeError("can't use both pr and provided")

        as_str = False if as_str is nv else bool(as_str)
        to_clipboard=False if to_clipboard is nv else bool(to_clipboard)
        provided = True if provided is nv else bool(provided)

        this = self.fork()
        this.assign(kwargs, locals(), func="__call__")

        if len(args) != 0 and not this.do_show():
            if as_str:
                return ""
            else:
                return return_args(args, this.return_none)

        self.is_context_manager = False

        Pair = collections.namedtuple("Pair", "left right")

        if not provided:
            this.enabled = False

        this.check()

        call_frame = inspect.currentframe()
        filename0 = call_frame.f_code.co_filename

        call_frame = call_frame.f_back
        filename = call_frame.f_code.co_filename

        if filename == filename0:
            call_frame = call_frame.f_back
            filename = call_frame.f_code.co_filename

        if filename in ("<stdin>", "<string>"):
            filename_name = ""
            code = "\n\n"
            this_line = ""
            this_line_prev = ""
            line_number = 0
            parent_function = ""
        else:
            try:
                main_file = sys.modules["__main__"].__file__
                main_file_resolved = os.path.abspath(main_file)
            except AttributeError:
                main_file_resolved = None
            filename_resolved = os.path.abspath(filename)
            if (filename.startswith("<") and filename.endswith(">")) or (main_file_resolved is None) or (filename_resolved == main_file_resolved):
                filename_name = ""
            else:
                filename_name = "[" + os.path.basename(filename) + "]"

            if filename not in codes:
                frame_info = inspect.getframeinfo(call_frame, context=1000000)  # get the full source code
                if frame_info.code_context is None:
                    no_source_error()
                codes[filename] = frame_info.code_context
            code = codes[filename]
            frame_info = inspect.getframeinfo(call_frame, context=1)

            #            parent_function = frame_info.function
            parent_function = Source.executing(call_frame).code_qualname()  # changed in version 1.3.10 to include class name
            parent_function = parent_function.replace(".<locals>.", ".")
            if parent_function == "<module>" or str(this.show_line_number) in ("n", "no parent"):
                parent_function = ""
            else:
                parent_function = " in {parent_function}()".format(parent_function=parent_function)
            line_number = frame_info.lineno
            if 0 <= line_number - 1 < len(code):
                this_line = code[line_number - 1].strip()
            else:
                this_line = ""
            if 0 <= line_number - 2 < len(code):
                this_line_prev = code[line_number - 2].strip()
            else:
                this_line_prev = ""
        if this_line.startswith("@") or this_line_prev.startswith("@"):
            if as_str:
                raise TypeError("as_str may not be True when peek used as decorator")

            for ln, line in enumerate(code[line_number - 1 :], line_number):
                if line.strip().startswith("def") or line.strip().startswith("class"):
                    line_number = ln
                    break
            else:
                line_number += 1
            this.line_number_with_filename_and_parent = "#{line_number}{filename_name}{parent_function}".format(
                line_number=line_number, filename_name=filename_name, parent_function=parent_function
            )

            def real_decorator(function):
                @functools.wraps(function)
                def wrapper(*args, **kwargs):
                    enter_time = perf_counter()
                    context = this.context()

                    args_kwargs = [repr(arg) for arg in args] + ["{k}={repr_v}".format(k=k, repr_v=repr(v)) for k, v in kwargs.items()]
                    function_arguments = function.__name__ + "(" + (", ".join(args_kwargs)) + ")"

                    if this.show_enter:
                        this.do_output(
                            "{context}called {function_arguments}{traceback}".format(
                                context=context, function_arguments=function_arguments, traceback=this.traceback()
                            )
                        )
                    result = function(*args, **kwargs)
                    duration = perf_counter() - enter_time

                    context = this.context()
                    if this.show_exit:
                        this.do_output(
                            "{context}returned {repr_result} from {function_arguments} in {duration:.6f} seconds{traceback}".format(
                                context=context, repr_result=repr(result), function_arguments=function_arguments, duration=duration, traceback=this.traceback()
                            )
                        )

                    return result

                return wrapper

            if not this.do_show():
                return lambda x: x

            return real_decorator

        if filename in ("<stdin>", "<string>"):
            this.line_number_with_filename_and_parent = ""
        else:
            call_node = Source.executing(call_frame).node
            if call_node is None:
                no_source_error()
            line_number = call_node.lineno
            this_line = code[line_number - 1].strip()

            this.line_number_with_filename_and_parent = "#{line_number}{filename_name}{parent_function}".format(
                line_number=line_number, filename_name=filename_name, parent_function=parent_function
            )

        if this_line.startswith("with ") or this_line.startswith("with\t"):
            if as_str:
                raise TypeError("as_str may not be True when peek used as context manager")
            if args:
                raise TypeError("non-keyword arguments are not allowed when peek used as context manager")

            this.is_context_manager = True
            return this

        if not this.do_show():
            if as_str:
                return ""
            else:
                return return_args(args, this.return_none)
        if args:
            context = this.context()
            pairs = []
            if filename in ("<stdin>", "<string>") or this.values_only:
                for right in args:
                    pairs.append(Pair(left="", right=right))
            else:
                source = Source.for_frame(call_frame)
                for node, right in zip(call_node.args, args):
                    left = source.asttokens().get_text(node)
                    if "\n" in left:
                        left = " " * node.first_token.start[1] + left
                        left = textwrap.dedent(left)
                    try:
                        ast.literal_eval(left)  # it's indeed a literal
                        left = ""
                    except Exception:
                        pass
                    if left:
                        try:
                            if isinstance(left, str):
                                s = ast.parse(left, mode="eval")
                            if isinstance(s, ast.Expression):
                                s = s.body
                            if s and isinstance(s, ast.JoinedStr):  # it is indeed an f-string
                                if this.values_only_for_fstrings:
                                    left = ""
                        except Exception:
                            pass
                    if left:
                        left += this.equals_separator
                    pairs.append(Pair(left=left, right=right))

            just_one_line = False
            if not (len(pairs) > 1 and this.separator == ""):
                if not any("\n" in pair.left for pair in pairs):
                    as_one_line = context + this.separator.join(pair.left + this.serialize_kwargs(obj=pair.right, width=10000) for pair in pairs)
                    if len(as_one_line) <= this.line_length and "\n" not in as_one_line:
                        out = as_one_line
                        just_one_line = True

            if not just_one_line:
                if isinstance(this.wrap_indent, numbers.Number):
                    wrap_indent = int(this.wrap_indent) * " "
                else:
                    wrap_indent = str(this.wrap_indent)

                if context.strip():
                    if len(context.rstrip()) >= len(wrap_indent):
                        indent1 = wrap_indent
                        indent1_rest = wrap_indent
                        lines = [context]
                    else:
                        indent1 = context.rstrip().ljust(len(wrap_indent))
                        indent1_rest = wrap_indent
                        lines = []
                else:
                    indent1 = ""
                    indent1_rest = ""
                    lines = []

                for pair in pairs:
                    do_right = False
                    if "\n" in pair.left:
                        for s in pair.left.splitlines():
                            lines.append(indent1 + s)
                            do_right = True
                    else:
                        start = indent1 + pair.left
                        line = start + this.serialize_kwargs(obj=pair.right, width=this.line_length - len(start))
                        if "\n" in line:
                            lines.append(start)
                            do_right = True
                        else:
                            lines.append(line)
                    indent1 = indent1_rest
                    if do_right:
                        indent2 = indent1 + wrap_indent
                        line = this.serialize_kwargs(obj=pair.right, width=this.line_length - len(indent2))
                        for s in line.splitlines():
                            lines.append(indent2 + s)

                out = "\n".join(line.rstrip() for line in lines)

        else:
            if not this.show_line_number:  # if "n" or "no parent", keep that info
                this.show_line_number = True
            out = this.context(omit_context_separator=True)

        if this.show_traceback:
            out += this.traceback()

        if as_str:
            if this.do_show():
                if this.enforce_line_length:
                    out = "\n".join(line[: this.line_length] for line in out.splitlines())
                return out + "\n"
            else:
                return ""
        peek.to_clipboard(pairs[0].right if "pairs" in locals() else '',confirm=False)
        this.do_output(out)

        return return_args(args, this.return_none)

    def configure(
        self,
        prefix=nv,
        output=nv,
        serialize=nv,
        show_line_number=nv,
        show_time=nv,
        show_delta=nv,
        show_enter=nv,
        show_exit=nv,
        show_traceback=nv,
        sort_dicts=nv,
        underscore_numbers=nv,
        enabled=nv,
        line_length=nv,
        compact=nv,
        indent=nv,
        depth=nv,
        wrap_indent=nv,
        context_separator=nv,
        separator=nv,
        equals_separator=nv,
        values_only=nv,
        values_only_for_fstrings=nv,
        return_none=nv,
        color=nv,
        color_value=nv,
        level=nv,
        enforce_line_length=nv,
        delta=nv,
        **kwargs,
    ):
        self.assign(kwargs, locals(), "configure()")
        self.check()
        return self

    def new(self, ignore_toml=False, **kwargs):
        if ignore_toml:
            return _Peek(_parent=default_pre_toml, **kwargs)
        else:
            return _Peek(**kwargs)

    def clone(
        self,
        prefix=nv,
        output=nv,
        serialize=nv,
        show_line_number=nv,
        show_time=nv,
        show_delta=nv,
        show_enter=nv,
        show_exit=nv,
        show_traceback=nv,
        sort_dicts=nv,
        underscore_numbers=nv,
        enabled=nv,
        line_length=nv,
        compact=nv,
        indent=nv,
        depth=nv,
        wrap_indent=nv,
        context_separator=nv,
        separator=nv,
        equals_separator=nv,
        values_only=nv,
        values_only_for_fstrings=nv,
        return_none=nv,
        color=nv,
        color_value=nv,
        level=nv,
        enforce_line_length=nv,
        delta=nv,
        **kwargs,
    ):
        this = _Peek(_parent=self._parent)
        this.assign({}, self._attributes, func="clone()")
        this.assign(kwargs, locals(), func="clone()")

        return this

    def assert_(self, condition):
        if self.do_show():
            assert condition

    @contextlib.contextmanager
    def preserve(self):
        save = dict(self._attributes)
        yield
        self._attributes = save

    def __enter__(self):
        if not hasattr(self, "is_context_manager"):
            raise ValueError("not allowed as context_manager")
        self.save_traceback = self.traceback()
        self.enter_time = perf_counter()
        if self.show_enter:
            context = self.context()
            self.do_output(context + "enter" + self.save_traceback)
        return self

    def __exit__(self, *args):
        if self.show_exit:
            context = self.context()
            duration = perf_counter() - self.enter_time
            self.do_output("{context}exit in {duration:.6f} seconds{traceback}".format(context=context, duration=duration, traceback=self.save_traceback))
        self.is_context_manager = False

    def context(self, omit_context_separator=False):
        if self.show_line_number and self.line_number_with_filename_and_parent != "":
            parts = [self.line_number_with_filename_and_parent]
        else:
            parts = []
        if self.show_time:
            parts.append("@ " + str(datetime.datetime.now().strftime("%H:%M:%S.%f")))

        if self.show_delta:
            t0 = perf_counter() - self.start_time
            parts.append("delta={t0:.3f}".format(t0=t0))

        context = " ".join(parts)
        if not omit_context_separator and context:
            context += self.context_separator

        return (self.prefix() if callable(self.prefix) else self.prefix) + context

    def add_color_value(self, s):
        if self.output != "stdout" or self.color_value == "" or self.as_str:
            return s
        return colors[self.color_value] + s + colors[self.color]

    def do_output(self, s):
        if self.enforce_line_length:
            s = "\n".join(line[: self.line_length] for line in s.splitlines())
        if self.do_show():
            if callable(self.output):
                self.output(s)
            elif self.output == "stderr":
                print(s, file=sys.stderr)
            elif self.output == "stdout":
                s = colors[self.color] + s + colors[""]
                if Pythonista:
                    while s:
                        for ansi, hexa in ansi_to_hexa.items():
                            if s.startswith(ansi):
                                if hexa == "":
                                    console.set_color()
                                else:
                                    rgb = tuple(int(hexa[i : i + 2], 16) / 255 for i in range(1, 7, 2))
                                    console.set_color(*rgb)
                                s = s[len(ansi) :]
                                break
                        else:
                            print(s[0], end="", file=sys.stdout)
                            s = s[1:]
                    print()
                else:
                    colorama.init()
                    print(s, file=sys.stdout)
                    colorama.deinit()

            elif self.output == "logging.debug":
                logging.debug(s)
            elif self.output == "logging.info":
                logging.info(s)
            elif self.output == "logging.warning":
                logging.warning(s)
            elif self.output == "logging.error":
                logging.error(s)
            elif self.output == "logging.critical":
                logging.critical(s)
            elif self.output in ("", "null"):
                pass
            elif isinstance(self.output, str):
                with open(self.output, "a+", encoding="utf-8") as f:
                    print(s, file=f)
            elif isinstance(self.output, Path):
                with self.output.open("a+", encoding="utf-8") as f:
                    print(s, file=f)

            else:
                print(s, file=self.output)

    def traceback(self):
        if self.show_traceback:
            if isinstance(self.wrap_indent, numbers.Number):
                wrap_indent = int(self.wrap_indent) * " "
            else:
                wrap_indent = str(self.wrap_indent)

            result = "\n" + wrap_indent + "Traceback (most recent call last)\n"
            #  Python 2.7 does not allow entry.filename, entry.line, etc, so we have to index entry
            return result + "\n".join(
                wrap_indent + '  File "' + entry[0] + '", line ' + str(entry[1]) + ", in " + entry[2] + "\n" + wrap_indent + "    " + entry[3]
                for entry in traceback.extract_stack()[:-2]
            )
        else:
            return ""

    def check(self):
        if callable(self.output):
            return
        if isinstance(self.output, (str, Path)):
            return
        try:
            self.output.write("")
            return

        except Exception:
            pass
        raise TypeError("output should be a callable, str, Path or open text file.")

    def serialize_kwargs(self, obj, width):
        kwargs = {
            key: getattr(self, key)
            for key in ("sort_dicts", "compact", "indent", "depth", "underscore_numbers")
            if key in inspect.signature(self.serialize).parameters
        }
        if "width" in inspect.signature(self.serialize).parameters:
            kwargs["width"] = width

        return self.add_color_value(self.serialize(obj, **kwargs).replace("\\n", "\n"))


codes = {}

set_defaults()
default_pre_toml = copy.copy(default)
apply_toml()
peek = _Peek()
builtins.peek = peek
p = peek.fork()


class PeekModule(types.ModuleType):
    def __call__(self, *args, **kwargs):
        return peek(*args, **kwargs)

    def __setattr__(self, item, value):
        setattr(peek, item, value)

    def __getattr__(self, item):
        return getattr(peek, item)


if __name__ != "__main__":
    sys.modules["peek"].__class__ = PeekModule

