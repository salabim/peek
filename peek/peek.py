#   _ __    ___   ___ | | __
#  | '_ \  / _ \ / _ \| |/ /
#  | |_) ||  __/|  __/|   <
#  | .__/  \___| \___||_|\_\
#  |_| like print, but easy.

__version__ = "24.0.0"

"""
See https://github.com/salabim/peek for details

(c)2024/2025 Ruud van der Ham - rt.van.der.ham@gmail.com

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
import traceback
import executing
import types
import pprint
import builtins
import traceback

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
colors["-"] = "\033[0m"


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


def dealias(name):
    return alias_name.get(name, name)


def check_validity(name, value, message=""):
    name_org = name
    name = dealias(name)
    if name not in name_default:
        raise ValueError(f"parameter {name} not allowed{message}")

    if value is None:
        return
    if name == "output":
        if callable(value):
            return
        if isinstance(value, (str, Path)):
            return
        try:
            value.write("")
            return
        except Exception:
            pass
        raise TypeError("output should be a callable, str, Path or open text file.")

    if name == "serialize":
        if callable(value):
            return

    if name in ("color", "color_value"):
        if name == "color_value" and value == "":
            return
        if isinstance(value, str) and value.lower() in colors:
            return

    elif name == "enforce_line_length":
        if value:
            if isinstance(value, numbers.Number) and value > 0:
                return
        else:
            return

    elif name == "line_length":
        if isinstance(value, numbers.Number) and value > 0:
            return

    elif name == "indent":
        if isinstance(value, numbers.Number) and value >= 0:
            return

    elif name == "level":
        if isinstance(value, numbers.Number) or value == "":
            return

    elif name == "wrap_indent":
        if isinstance(value, str):
            return
        if isinstance(value, numbers.Number):
            if value > 0:
                return

    elif name == "filter":
        if value.strip() == "":
            return
        try:
            eval(value, name_and_alias_default)
            return
        except Exception:
            ...

    else:
        return

    raise ValueError(f"incorrect {name_org}: {value}{message}")


class Source(executing.Source):
    def get_text_with_indentation(self, node):
        result = self.asttokens().get_text(node)
        if "\n" in result:
            result = " " * node.first_token.start[1] + result
            result = textwrap.dedent(result)
        result = result.strip()
        return result


def change_path(new_path):  # used in tests
    global Path
    Path = new_path


_fixed_perf_counter = None


def read_toml():
    this_path = Path(".").resolve()

    for i in range(len(this_path.parts), 0, -1):
        toml_file = Path(this_path.parts[0]).joinpath(*this_path.parts[1:i], "peek.toml")
        if toml_file.is_file():
            with open(toml_file, "r") as f:
                config_as_str = f.read()
            config = tomlib.loads(config_as_str)
            for name, value in config.items():
                check_validity(name, value, message=f" while processing {toml_file}")
            return config
            break
    return {}


def no_source_error():

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
    def __init__(self, parent=None, **kwargs):
        self._attributes = {}
        for name, value in kwargs.items():
            check_validity(name, value)
            setattr(self, name, value)
        self._parent = parent

    def __repr__(self):
        pairs = [str(name) + "=" + repr(getattr(self, name)) for name in name_default if name != "serialize"]
        return "peek.new(" + ", ".join(pairs) + ")"

    def fix_perf_counter(self, val):  # for tests
        global _fixed_perf_counter
        _fixed_perf_counter = val

    def __getattr__(self, item):
        item = dealias(item)
        if item in name_default:
            node = self
            while not item in node._attributes or node._attributes[item] is None:
                node = node._parent
            if item == "delta":
                return perf_counter() - node._attributes[item]
            else:
                return node._attributes[item]
        else:
            return self.__getattribute__(item)

    def __setattr__(self, item, value):
        if item in ("_parent", "is_context_manager", "line_number_with_filename_and_parent", "save_traceback", "enter_time", "as_str", "_attributes"):
            return super().__setattr__(item, value)

        if item not in name_and_alias_default:
            raise AttributeError(f"attribute {item} not allowed")

        check_validity(item, value)
        item = dealias(item)

        if item == "delta" and value is not None:
            self._attributes[item] = perf_counter() - value

        else:
            self._attributes[item] = value

    def do_show(self):
        if self.filter.strip() != "":
            if not eval(self.filter, {name: getattr(self, name) for name in list(name_default) + list(alias_default)}):
                return False
        return self.enabled

    def copy_to_clipboard(self, value, confirm=True):
        if Pythonista:
            clipboard.set(str(value))
        else:
            pyperclip.copy(str(value))
        if confirm:
            print(f"copied to clipboard: {value}")

    def __call__(self, *args, as_str=False, **kwargs):
        codes = {}
        this = self.fork(**kwargs)

        this.as_str = as_str
        if len(args) != 0 and not this.do_show():
            if as_str:
                return ""
            else:
                return return_args(args, this.return_none)

        self.is_context_manager = False

        Pair = collections.namedtuple("Pair", "left right")

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
                parent_function = f" in {parent_function}()"
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
            this.line_number_with_filename_and_parent = f"#{line_number}{filename_name}{parent_function}"

            def real_decorator(function):
                @functools.wraps(function)
                def wrapper(*args, **kwargs):
                    enter_time = perf_counter()
                    context = this.context()

                    args_kwargs = [repr(arg) for arg in args] + [f"{k}={repr(v)}" for k, v in kwargs.items()]
                    function_arguments = function.__name__ + "(" + (", ".join(args_kwargs)) + ")"

                    if this.show_enter:
                        this.do_output(f"{context}called {function_arguments}{this.traceback()}")
                    result = function(*args, **kwargs)
                    duration = perf_counter() - enter_time

                    context = this.context()
                    if this.show_exit:
                        this.do_output(f"{context}returned {repr(result)} from {function_arguments} in {duration:.6f} seconds{this.traceback()}")

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

            this.line_number_with_filename_and_parent = f"#{line_number}{filename_name}{parent_function}"

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
        if this.to_clipboard:
            peek.copy_to_clipboard(pairs[-1].right if "pairs" in locals() else "", confirm=False)
        this.do_output(out)

        return return_args(args, this.return_none)

    def configure(self, **kwargs):
        for name, value in kwargs.items():
            check_validity(name, value)
            self._attributes[name] = value
        return self

    def new(self, ignore_toml=False, **kwargs):
        if ignore_toml:
            return _Peek(**kwargs, parent=peek_no_toml)
        else:
            return _Peek(**kwargs, parent=peek_toml)

    def fork(self, **kwargs):
        return _Peek(**kwargs, parent=self)

    def clone(self, **kwargs):
        clone = _Peek(parent=self._parent)
        clone._attributes=self._attributes.copy()
        for name,value in kwargs:
            setattr(clone,name,value)    
        return clone

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
            self.do_output(f"{context}exit in {duration:.6f} seconds{self.save_traceback}")
        self.is_context_manager = False

    def context(self, omit_context_separator=False):
        if self.show_line_number and self.line_number_with_filename_and_parent != "":
            parts = [self.line_number_with_filename_and_parent]
        else:
            parts = []
        if self.show_time:
            parts.append("@ " + str(datetime.datetime.now().strftime("%H:%M:%S.%f")))

        if self.show_delta:
            parts.append(f"delta={self.delta:.3f}")

        context = " ".join(parts)
        if not omit_context_separator and context:
            context += self.context_separator

        return (self.prefix() if callable(self.prefix) else self.prefix) + context

    def add_color_value(self, s):
        if self.output != "stdout" or self.as_str:
            return s
        if self.color_value.lower() not in (self.color.lower(), ""):
            return colors[self.color_value.lower()] + s + colors[self.color.lower()]
        else:
            return s

    def do_output(self, s):
        if self.enforce_line_length:
            s = "\n".join(line[: self.line_length] for line in s.splitlines())
        if self.do_show():
            if callable(self.output):
                self.output(s)
            elif self.output == "stderr":
                print(s, file=sys.stderr)
            elif self.output == "stdout":
                if self.color != "-" or self.color_value != "-":
                    s = colors[self.color.lower()] + s + colors["-"]
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
                        print(s)
                else:
                    print(s)
            elif self.output == "stdout_nocolor":
                print(s)
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

    def serialize_kwargs(self, obj, width):
        if isinstance(obj, str) and not self.quote_string:
            return self.add_color_value(obj)
        kwargs = {
            key: getattr(self, key)
            for key in ("sort_dicts", "compact", "indent", "depth", "underscore_numbers")
            if key in inspect.signature(self.serialize).parameters
        }
        if "width" in inspect.signature(self.serialize).parameters:
            kwargs["width"] = width

        return self.add_color_value(self.serialize(obj, **kwargs).replace("\\n", "\n"))


name_alias_default = (
    ("color", "col", "-"),
    ("color_value", "colv", ""),
    ("context_separator", "cs", " ==> "),
    ("compact", "", False),
    ("delta", "", 0),
    ("depth", "", 1000000),
    ("enabled", "", True),
    ("enforce_line_length", "", False),
    ("equals_separator", "", "="),
    ("filter", "f", ""),
    ("indent", "", 1),
    ("level", "lvl", 0),
    ("line_length", "ll", 80),
    ("output", "", "stdout"),
    ("prefix", "pr", ""),
    ("quote_string", "qs", True),
    ("return_none", "", False),
    ("separator", "sep", ", "),
    ("serialize", "", pprint.pformat),
    ("show_delta", "sd", False),
    ("show_enter", "se", True),
    ("show_exit", "sx", True),
    ("show_line_number", "sln", False),
    ("show_time", "st", False),
    ("show_traceback", "", False),
    ("sort_dicts", "", False),
    ("to_clipboard", "clip", False),
    ("underscore_numbers", "un", False),
    ("wrap_indent", "", "    "),
    ("values_only", "vo", False),
    ("values_only_for_fstrings", "voff", False),
)

alias_name = {alias: name for (name, alias, default) in name_alias_default if alias}
name_default = {name: default for (name, alias, default) in name_alias_default}
alias_default = {alias: default for (name, alias, default) in name_alias_default if alias}
name_and_alias_default = {**name_default, **alias_default}

peek_no_toml = _Peek(**name_default)
peek_toml = peek_no_toml.fork(**read_toml())
#_Peek(parent=peek_no_toml)
# for name, value in read_toml().items():
#     setattr(peek_toml,name,value)

peek=peek_toml.new()
builtins.peek = peek


class PeekModule(types.ModuleType):
    def __call__(self, *args, **kwargs):
        return peek(*args, **kwargs)

    def __setattr__(self, item, value):
        setattr(peek, item, value)

    def __getattr__(self, item):
        return getattr(peek, item)


if __name__ != "__main__":
    sys.modules["peek"].__class__ = PeekModule

