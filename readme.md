 <img src="https://www.salabim.org/peek/peek_logo1.png">

# Introduction

Do you use `print()` or `log()` to debug your code?
If so,  peek will make printing debug information really easy.
And on top of that, you get some basic benchmarking functionality.

# Table of contents

* [Installation](#installation)

* [Importing peek](#importing-peek)

* [Inspect variables and expressions](#inspect-variables-and-expressions)

* [Inspect execution](#inspect-execution)

* [Return value](#return-value)

* [Debug entry and exit of function calls](#debug-entry-and-exit-of-function-calls)

* [Benchmarking with peek](#benchmarking-with-peek)

* [Configuration](#configuration)

* [Use peek.print to use peek like print with extras](#use-peek.print-to-to use peek like-with-extras)

* [Return a string instead of sending to output](#return-a-string-instead-of-sending-to-output)

* [Disabling peek's output](#disabling-peeks-output)

* [Using level to control peek output](#Using-level-to-control-peek-output)

* [Using color to control peek output](#Using-color-to-control-peek-output)

* [Copying to the clipboard](#Copying-to-the-clipboard)

* [Interpreting the line number information](#interpreting-the-line-number-information)

* [Configuring at import time](#configuring-at-import-time)

* [Working with multiple instances of peek](#working-with-multiple-instances-of-peek)

* [Test script](#test-script)

* [Using peek in a REPL](#using-peek-in-a-repl)

* [Limitations](#limitations)

* [Changelog](#changelog)

* [Acknowledgement](#acknowledgement)

* [Differences with IceCream](#differences-with-icecream)


# Installation

Installing peek with pip is easy.
```
pip install peek-python
```
or when you want to upgrade,
```
pip install peek-python --upgrade
```

Alternatively, peek.py can be just copied into you current work directory from GitHub
(https://github.com/salabim/peek).

Note that peek requires the `asttokens`,  `colorama`, `executing`. `six`,  `tomli` and `pyperclip` modules, all of which will be automatically installed.

# Importing peek

All you need is:

```
import peek
```

, or the more conventional, but more verbose

```
from peek import peek
```

Note that after this, `peek` is automatically a builtin and can thus be used in any module without
importing it there.

# Inspect variables and expressions

Have you ever printed variables or expressions to debug your program? If you've
ever typed something like

```
print(add2(1000))
```

or the more thorough

```
print("add2(1000)", add2(1000)))
```
or:
```
print(f"{add2(1000)=}")
```

then `peek()` is here to help. With arguments, `peek()` inspects itself and prints
both its own arguments and the values of those arguments.

```
def add2(i):
    return i + 2

peek(add2(1000))
```

prints
```
add2(1000)=1002
```

Similarly,

```
class X:
    a = 3
world = {"EN": "world", "NL": "wereld", "FR": "monde", "DE": "Welt"}

peek(world, X.a)
```

prints
```
world={"EN": "world ", "NL": "wereld", "FR": "monde", "DE": "Welt"}, X.a: 3
```
Just give `peek()` a variable or expression and you're done.


# Inspect execution

Have you ever used `print()` to determine which parts of your program are
executed, and in which order they're executed? For example, if you've ever added
print statements to debug code like

```
def add2(i):
    print("***add2 1")
    result = i + 2
    print("***add2 2")
    return result
```
then `peek()` helps here, too. Without arguments, `peek()` inspects itself and
prints the calling line number and -if applicable- the file name and parent function.

```
def add2(i):
    peek()
    result = i + 2
    peek()
    return result
peek(add2(1000))
```

prints something like
```
#3 in add2()
#5 in add2()
add2(1000)=1002
```

# Return Value

`peek()` returns its argument(s), so `peek()` can easily be inserted into
pre-existing code.

```
def add2(i):
    return i + 2
b = peek(add2(1000))
peek(b)
```
prints
```
add2(1000)=1002
b=1002
```
# Debug entry and exit of function calls

When you apply `peek()` as a decorator to a function or method, both the entry and exit can be tracked.
The (keyword) arguments passed will be shown and upon return, the return value.

```
@peek()
def mul(x, peek):
    return x * peek
    
print(mul(5, 7))
```
prints
```
called mul(5, 7)
returned 35 from mul(5, 7) in 0.000006 seconds
35
```
It is possible to suppress the print-out of either the enter or the exit information with
the show_enter and show_exit parameters, like:

```
@peek(show_exit=False)
def mul(x, peek):
    return x * peek
    
print(mul(5, 7))
```
prints
```
called mul(5, 7)
35
```

# Benchmarking with peek

If you decorate a function or method with peek(), you will be offered the duration between entry and exit (in seconds) as a bonus.

That opens the door to simple benchmarking, like:
```
import time

@peek(show_enter=False,show_line_number=True)
def do_sort(i):
    n = 10 ** i
    x = sorted(list(range(n)))
    return f"{n:9d}"  
    
for i in range(8):
    do_sort(i)
```
the ouput will show the effects of the population size on the sort speed:
```
#5 ==> returned '        1' from do_sort(0) in 0.000027 seconds
#5 ==> returned '       10' from do_sort(1) in 0.000060 seconds
#5 ==> returned '      100' from do_sort(2) in 0.000748 seconds
#5 ==> returned '     1000' from do_sort(3) in 0.001897 seconds
#5 ==> returned '    10000' from do_sort(4) in 0.002231 seconds
#5 ==> returned '   100000' from do_sort(5) in 0.024014 seconds
#5 ==> returned '  1000000' from do_sort(6) in 0.257504 seconds
#5 ==> returned ' 10000000' from do_sort(7) in 1.553495 seconds
```

It is also possible to time any code by using peek() as a context manager, e.g.
```
with peek():
    time.sleep(1)
```
wil print something like
```
enter
exit in 1.000900 seconds
```
You can include parameters here as well:
```
with peek(show_line_number=True, show_time=True):
    time.sleep(1)
```
will print somethink like:
```
#8 @ 13:20:32.605903 ==> enter
#8 @ 13:20:33.609519 ==> exit in 1.003358 seconds
```

Finally, to help with timing code, you can request the current delta with
```
peek.delta
```
or (re)set it  with
```
peek.delta = 0
```
So, e.g. to time a section of code:
```
peek.delta = 0
time.sleep(1)
duration = peek.delta
peek(duration)
```
might print something like:
```
duration=1.0001721999999997
```

# Configuration

For the configuration, it is important to realize that `peek` is an instance of a class, which has
a number of configuration attributes:

```
------------------------------------------------------
attribute               alternative     default
------------------------------------------------------
color                   col             "-"
color_value				col_val	        "-"
compact                 -               False
context_separator       cs              " ==> "
depth                   -               1000000
delta                   -               0
enabled                 -               True
end						-				"\n"
equals_separator        -               "="
filter                  f               ""
indent                  -               1
level                   lvl             0
line_length             ll              80
output                  -               "stdout"
prefix                  pr              ""
print_like              print           False
quote_string			qs				True
return_none             -               False
separator               sep             ", "
separator_print         sepp            "" "
serialize               -               pprint.pformat
show_delta              sd              False
show_enter              se              True
show_exit               sx              True
show_line_number        sln             False
show_time               st              False
show_traceback          -               False
sort_dicts              -               False
to_clipboard            clip            False
underscore_numbers      un              False   
values_only             vo              False
value_only_for_fstrings voff            False 
wrap_indent             -               "     "
------------------------------------------------------
```
It is perfectly ok to set/get any of these attributes directly, like
```
peek.prefix = "==> "
print(peek.prefix)
```

But, it is also possible to apply configuration directly, only here, in the call to `peek`:
So, it is possible to say
```
peek(12, prefix="==> ")
```
, which will print
```
==> 12
```
It is also possible to configure several attributes permanently with the configure method. 
```
peek.configure(prefix="==> ", color="blue")
peek(12)
```
will print in blue
```
==> 12
```
It is arguably easier to say:
```
peek.prefix = "==> "
peek.color = "blue"
peek(12)
```
or even
```
peek.pr = "==> "
peek.col = "blue"
peek(12)
```
to print
```
==> 12
```
Yet another way to configure peek is to get a new instance of peek with peek.new() and the required configuration:
```
z = peek.new(prefix="==> ", color="blue")
z(12)
```
will print
```
==> 12
```

Or, yet another possibility is to clone peek (optionally with modified attributes):
```
peek1 = peek.clone(show_time=True)
peek2 = peek.clone()
peek2.show_time = True
```
After this `peek1` and `peek2` will behave similarly (but they are not the same!)

## prefix / pr
```
peek('world', prefix='hello -> ')
```
prints
```
hello -> 'world'
```

`prefix` can be a function, too.

```
import time
def unix_timestamp():
    return f"{int(time.time())} "
hello = "world"
peek.prefix = unix_timestamp
peek(hello) 
```
prints
```
1613635601 hello='world'
```

## output
This will allow the output to be handled by something else than the default (output being written to stdout).

The `output` attribute can be

* a callable that accepts at least one parameter (the text to be printed)
* a string or Path object that will be used as the filename
* a text file that is open for writing/appending

In the example below, 
```
import sys
peek(1, output=print)
peek(2, output=sys.stderr)
with open("test", "a+") as f:
    peek(3, output=f)
peek(4, output="")
```
* `1` will be printed to stdout
* `2` will be printed to stderr
* `3` will be appended to the file test
* nothing will be printed/written

As `output` may be a callable, you can even use this to automatically log any `peek` output:
```
import logging
logging.basicConfig(level="INFO")
log = logging.getLogger("demo")
peek.configure(output=log.info)
a = {1, 2, 3, 4, 5}
peek(a)
a.remove(4)
peek(a)
```
will print to stdout:
```
INFO:demo:a={1, 2, 3, 4, 5}
INFO:demo:a={1, 2, 3, 5}
```
Finally, you can specify the following strings:
```
"stderr"           to print to stderr
"stdout"           to print to stdout
"stdout_nocolor"   to print to stdout without any colors
"null" or ""       to completely ignore (dummy) output 
"logging.debug"    to use logging.debug
"logging.info"     to use logging.info
"logging.warning"  to use logging.warning
"logging.error"    to use logging.error
"logging.critical" to use logging.critical
```
E.g.
```
import sys
peek.output = "stderr"
```
to print to stderr.

## serialize
This will allow to specify how argument values are to be serialized to displayable strings.
The default is `pformat` (from `pprint`), but this can be changed.
For example, to handle non-standard datatypes in a custom fashion.
The serialize function should accept at least one parameter.
The function may optionally accept the keyword arguments `width` and `sort_dicts`, `compact`, `indent`, `underscore_numbers` and `depth`.

```
def add_len(obj):
    if hasattr(obj, "__len__"):
        add = f" [len={len(obj)}]"
    else:
        add = ""
    return f"{repr(obj)}{add}"

l7 = list(range(7))
hello = "world"
peek(7, hello, l7, serialize=add_len)
```
prints
```
7, hello='world' [len=5], l7=[0, 1, 2, 3, 4, 5, 6] [len=7]
```

## show_line_number / sln
If True, adds the `peek()` call's line number and possibly the filename and parent function to `peek()`'s output.

```
peek.configure(show_line_number=True)
def shout():
    hello="world"
    peek(hello)
shout()
```
prints something like
```
#5 in shout() ==> hello='world'
```

If "no parent" or "n", the parent function will not be shown.
```
peek.show_line_number = "n"
def shout():
    hello="world"
    peek(hello)
shout()
```
prints something like
```
#5 ==> hello='world'
```
Note that if you call `peek` without any arguments, the line number is always shown, regardless of the status `show_line_number`.

See below for an explanation of the information provided.

## show_time / st
If True, adds the current time to `peek()`'s output.

```
peek.configure(show_time=True)
hello="world"
peek(hello)
```
prints something like
```
@ 13:01:47.588125 ==> hello='world'
```

## show_delta / sd
If True, adds the number of seconds since the start of the program to `peek()`'s output.
```
import time
peek.show_delta = True
french = "bonjour le monde"
english = "hallo world"
peek(english)
time.sleep(1)
peek(french)
```
prints something like
```
delta=0.088 ==> english='hallo world'
delta=1.091 ==> french='bonjour le monde'
```

## show_enter / se
When used as a decorator or context manager, by default, peek ouputs a line when the decorated the
function is called  or the context manager is entered.

With `show_enter=False` this line can be suppressed.

## show_exit / sx
When used as a decorator or context manager, by default, peek ouputs a line when the decorated the
function returned or the context manager is exited.

With `show_exit=False` this line can be suppressed.


## show_traceback
When show_traceback is True, the ordinary output of peek() will be followed by a printout of the
traceback, similar to an error traceback.

```
def x():
    peek(show_traceback=True)

x()
x()
```
prints
```
#4 in x()
    Traceback (most recent call last)
      File "c:\Users\Ruud\Dropbox (Personal)\Apps\Python Ruud\peek\x.py", line 6, in <module>
        x()
      File "c:\Users\Ruud\Dropbox (Personal)\Apps\Python Ruud\peek\x.py", line 4, in x
        peek()
#4 in x()
    Traceback (most recent call last)
      File "c:\Users\Ruud\Dropbox (Personal)\Apps\Python Ruud\peek\x.py", line 7, in <module>
        x()
      File "c:\Users\Ruud\Dropbox (Personal)\Apps\Python Ruud\peek\x.py", line 4, in x
        peek()
```
The `show_traceback` functionality is also available when peek is used as a decorator or context manager. 

## line_length / ll
This attribute is used to specify the line length (for wrapping). The default is 80.
Peek tries to keep all output on one line, but if it can't it will wrap:

```
d = dict(a1=1,a2=dict(a=1,b=1,c=3),a3=list(range(10)))
peek(d)
peek(d, line_length=80)
```
prints
```
d={'a1': 1, 'a2': {'a': 1, 'b': 1, 'c': 3}, 'a3': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
d=
    {'a1': 1,
     'a2': {'a': 1, 'b': 1, 'c': 3},
     'a3': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
```

## color / col and color_value / colv
The color attribute is used to specify the color of the output.
There's a choice of black, white, red, green, blue, cyan, magenta and yellow.
To set the color to 'nothing', use "-".

On top of that, color_value may be used to specify the value part of an output item. By specifying color_value as "" (the default), the value part will be displayed with the same color as the rest of the output.

For instance:

```
x = "x"
y = "y"
peek(x, y)
peek(x, y, color_value="green")
peek(x, y, color="red")
peek(x, y, color="red", color_value="green")
```

will result in:

 <img src="https://www.salabim.org/peek/peek_colors.png">

Of course, color and color_value may be specified in a peek.toml file, to make all peek output in a specified color.

> [!NOTE]
>
> The color and color_value attributes are only applied when using stdout as output.
> 
> Colors can be ignored completely by using `peek.output = "stdout_nocolor`.

## compact
This attribute is used to specify the compact parameter for `pformat` (see the pprint documentation
for details). `compact` is False by default.

```
a = 9 * ["0123456789"]
peek.line_length = 80
peek(a)
peek(a, compact=True)
```
prints
```
a=
    ['0123456789',
     '0123456789',
     '0123456789',
     '0123456789',
     '0123456789',
     '0123456789',
     '0123456789',
     '0123456789',
     '0123456789']
a=
    ['0123456789', '0123456789', '0123456789', '0123456789', '0123456789',
     '0123456789', '0123456789', '0123456789', '0123456789']
```

## indent
This attribute is used to specify the indent parameter for `pformat` (see the pprint documentation
for details). `indent` is 1 by default.

```
s = "01234567890012345678900123456789001234567890"
peek.line_length = 80
peek( [s, [s]])
peek( [s, [s]], indent=4)
```
prints
```
[s, [s]]=
    ['01234567890012345678900123456789001234567890',
     ['01234567890012345678900123456789001234567890']]
[s, [s]]=
    [   '01234567890012345678900123456789001234567890',
        ['01234567890012345678900123456789001234567890']]
```

## depth
This attribute is used to specify the depth parameter for `pformat` (see the pprint documentation
for details). `depth` is `1000000` by default. 

```
s = "01234567890012345678900123456789001234567890"
peek([s,[s,[s,[s,s]]]])
peek([s,[s,[s,[s,s]]]], depth=3)
```
prints
```
[s,[s,[s,[s,s]]]]=
    ['01234567890012345678900123456789001234567890',
     ['01234567890012345678900123456789001234567890',
      ['01234567890012345678900123456789001234567890',
       ['01234567890012345678900123456789001234567890',
        '01234567890012345678900123456789001234567890']]]]
[s,[s,[s,[s,s]]]]=
    ['01234567890012345678900123456789001234567890',
     ['01234567890012345678900123456789001234567890',
      ['01234567890012345678900123456789001234567890', [...]]]]
```

## wrap_indent
This specifies the indent string if the output does not fit in the line_length (has to be wrapped).
Rather than a string, wrap_indent can be also be an integer, in which case the wrap_indent will be that amount of blanks.
The default is 4 blanks.

E.g.
```
d = dict(a1=1,a2=dict(a=1,b=1,c=3),a3=list(range(10)))
peek.line_length = 80
peek(d, wrap_indent="  ")
peek(d, wrap_indent="....")
peek(d, wrap_indent=2)
```
prints
```
d=
  {'a1': 1,
   'a2': {'a': 1, 'b': 1, 'c': 3},
   'a3': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
d=
....{'a1': 1,
.... 'a2': {'a': 1, 'b': 1, 'c': 3},
.... 'a3': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
d=
  {'a1': 1,
   'a2': {'a': 1, 'b': 1, 'c': 3},
   'a3': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
```

## enabled
Can be used to disable the output:
```
peek.enabled = False
s = 'the world is '
peek(s + 'perfect.')
peek.enabled = True
peek(s + 'on fire.')
```
prints
```
s + 'on fire.'='the world is on fire.'
```
and nothing about a perfect world.

## sort_dicts
By default, peek does not sort dicts (printed by pprint). However, it is possible to get the
default pprint behaviour (i.e. sorting dicts) with the sorted_dicts attribute:

```
world = {"EN": "world", "NL": "wereld", "FR": "monde", "DE": "Welt"}
peek(world))
peek(world, sort_dicts=False)
peek(world, sort_dicts=True)
```
prints
```
world={'EN': 'world', 'NL': 'wereld', 'FR': 'monde', 'DE': 'Welt'}
world={'EN': 'world', 'NL': 'wereld', 'FR': 'monde', 'DE': 'Welt'}
world={'DE': 'Welt', 'EN': 'world', 'FR': 'monde', 'NL': 'wereld'}
```

Note that under Python <=3.7, dicts are always printed sorted.

## underscore_numbers / un

By default, peek does not add underscores in big numbers (printed by pprint). However, it is possible to get the
default pprint behaviour with the underscore_numbers attribute:

```
numbers = dict(one= 1, thousand= 1000, million=1000000, x1234567890= 1234567890)
peek(numbers)
peek(numbers, underscore_numbers=True)
peek(numbers, un=False)
```
prints
```
numbers={'one': 1, 'thousand': 1000, 'million': 1000000, 'x1234567890': 1234567890}
numbers={'one': 1, 'thousand': 1_000, 'million': 1_000_000, 'x1234567890': 1_234_567_890}
numbers={'one': 1, 'thousand': 1000, 'million': 1000000, 'x1234567890': 1234567890}
```

Note that under Python <=3.7, numbers are never underscored.

## seperator / sep

By default, pairs (on one line) are separated by `", ""`.
It is possible to change this with the attribute ` separator`:

```
a = "abcd"
b = 1
c = 1000
d = list("peek")
peek(a, (b, c), d)
peek(a, (b, c), d, separator=" | ")
```
prints
```
a='abcd', (b,c)=(1, 1000), d=['p', 'e', 'e', 'k']
a='abcd' | (b,c)=(1, 1000) | d=['p', 'e', 'e', 'k']
```

## context_separator

By default the line_number, time and/or delta are followed by ` ==> `.
It is possible to change this with the attribute `context_separator`:
```
a = "abcd"
peek(a,show_time=True)
peek(a, show_time=True, context_separator = ' \u279c ')
```
prints:
```
@ 09:05:38.693840 ==> a='abcd'
@ 09:05:38.707914 ➜ a='abcd'
```
## equals_separator
By default name of a variable and its value are separated by `= `.
It is possible to change this with the attribute `equals_separator`:

```
a = "abcd"
peek(a)
peek(a, equals_separator = ' == ")
```
prints:
```
a='abcd'
a == 'abcd'
```
## quote_string / qs
If True (the default setting) strings will be displayed with surrounding quotes (like repr).
If False, string will be displayed without surrounding quotes (like str).
E.g.

```
test='test'
peek('==>', test)
peek('==>', test, quote_string=False)
```
This will print:
```
'==>', test='test'
==>, test=test
```
> [!NOTE]
>
> This setting does not influence how strings are displayed within other data structures, like dicts and lists.

## values_only / vo
If False (the default), both the left-hand side (if possible) and the
value will be printed. If True, the left hand side will be suppressed:

```
hello = "world"
peek(hello, 2 * hello)
peek(hello, 2 * hello, values_only=True)
```
prints
```
hello='world', 2 * hello='worldworld'
'world', 'worldworld'
```

## values_only_for_fstrings / voff
If False (the default), both the original f-string and the
value will be printed for f-strings.
If True, the left_hand side will be suppressed in case of an f-string:

```
x = 12.3
peek.quote_string = False
peek(f"{x=:0.3e}")
peek.values_only_for_fstrings = True
peek(f"{x=:0.3e}")
```
prints
```
f"{x=:0.3e}"=x=1.230e+01
x=1.230e+01
```
Note that if `values_only` is True, f-string will be suppressed, regardless of `values_only_for_fstrings`.


## end

The `end` attribute works like the end parameter of print. By default, `end` is "\n".
This can be useful to have several peek outputs on one line, like:

```
for i in range(5):
    peek(i*i, end=' ')
peek('')
```
Maybe more useful is to show the output change on the same line, e.g. a status.
```
import time
for i in range(50):
  peek(f"time {time.time()}",end="\r")
  time.sleep(0.1)
peek('')
```
The `end` parameter will be only applied when output is stdout, stdout_nocolor or stderr.

> [!NOTE]
>
> `\r` does not work under Pythonista.

## return_none
Normally, `peek()`returns the values passed directly, which is usually fine. However, when used in a notebook
or REPL, that value will be shown, and that can be annoying. Therefore, if `return_none`is True, `peek()`will
return None and thus not show anything.

```
a = 3
b = 4
print(peek(a, b))
peek.return_none = True
print(peek(a, b))
```
prints
```
a=3, b=4
(3, 4)
a=3, b=4
None
```

## delta
The delta attribute can be used to (re)set the current delta, e.g.
```
peek.delta = 0
print(peek.delta)
```
prints a value that id slightly more than 0.

## print_like / print
When print_like (or print) is False, peek will work by expanding the arguments to description/serialized value pairs.
But, when print_like is True, peek becomes a kind of supercharged print:

```
peek.print_like = True
peek(12, f"{min(1, 2)=}", list(range(4), color="yellow")
```
will print
```
12 min(1, 2)=1 [0, 1, 2, 3]
```
in yellow, but only if peek.enabled is False, nothing will be printed.

You can also use peek.print (see below).

> [!TIP]
>
> Of course, print_only can be put in a **peek.toml** file.

# Use peek.print to use peek like print with extras
The method `peek.print` allows peek to be used as alternative to print. Note that `peek.print` applies the `color`, `context_separator`, `enabled`, `filter` and `output`, `show_delta` and `show_time`. It is also possible to redirect the output to as string with `as_str`.

So,

```
peek.filter = "level==1"
peek.print(f"{max(1, 2)=}", color="blue")  # default level is 0, so this will be suppressed
peek.print(f"{min(1, 2)=}", color="red",level=1)
```

will print

  ```
min(1, 2)=1
  ```

in red, but only if peek.enabled is True (which is the default).

The `peek.print`() method applies the prefix, show_delta, show_line_number, show_time, show_ end attributes to the output.

In order to behave similar to print, `peek` has an extra attribute, `separator_print` (alias: `sepp`). This attribute (default " ") will be used when `peek.printing`.
When calling `peek.print`, `sep` may be used instead. So

```
peek.sepp = "|"
peek.print("test")
```

Has the same effect as

```
peek.print("test", sep="|")
```

and

```
peek.print("test", sepp="|")
```

but not the same as

```
peek.sep = "|"  # sets the 'normal' peek separator
```
> [!NOTE]
>
> `peek.print` does not obey the line length and will always return None (unless as_str is True). 

# Return a string instead of sending to output

`peek(*args, as_str=True)` is like `peek(*args)` but the output is returned as a string instead
of written to output.

```
hello = "world"
s = peek(hello, as_str=True)
print(s, end="")
```
prints
```
hello='world'
```

Note that if enabled=False, the call will return the null string (`""`).

# Disabling peek's output

```
peek1 = peek.fork(show_delta=True)
peek(1)
peek1(2)
peek.enabled = False
peek(3)
peek1(4)
peek1.enabled = True
peek(5)
peek1(6)
print(peek1.enabled)
```
prints
```
1
delta=0.011826 ==> 2
5
delta=0.044893 ==> 6
True
```
Of course `peek()` continues to return its arguments when disabled.

It is also possible to suppress output with the provided attribute (see above).

# Using filter to control peek output

It is possible to define a filter function that determines whether peek output should be suppressed
By default, the filter is defined as "" denoting no filter.

Suppose we a (float) level to a peek statement. By default, this level is 0. E.g.:

```
peek("critical", level=0)
peek("important", level=1)
peek("warning", level=2)
```

With `peek.filter ="level <= 1"` the program makes sure that level=2 is not displayed at all.

It is possible to use more than one attribute, like

```
peek.filter = "color == 'blue' and delta > 5"
```
As an alternative to `enabled` we can also say
```
peek.filter = "False"
```

# Copying to the clipboard

It is possible to copy a value to the clipboard. There are two ways:

### With peek(to_clipboard=True)

With the optional keyword argument, *to_clipboard*:

- If to_clipboard==False (the default), nothing is copied to the clipboard.
- If to_clipboard==True, the *value* of the the *last* parameter will be copied to the clipboard. The output itself is as usual.

Examples:

```
part1 = 200
extra = "extra"
peek(part1, extra, to_clipboard=True)
    # will print part1=200, extra='extra' and copy `extra` to the clipboard
peek(200, to_clipboard=True)\
    # will print 200 and copy 200 to the clipboard
peek(to_clipboard=True)
    # will print #5 (or similar) and empty the clipboard
```

Note that *to_clipboard* is a peek attribute.

If as_str==True, to_clipboard is ignored.

### With peek.to_clipboard

Just use peek.to_clipboard to copy any value to the clipboard. So,
```
part1 = 1234
peek.to_clipboard(part1)
```

will copy `1234` to the clipboard and write `copied to clipboard: 1234` to the console.
If the confirmation message is not wanted, just add confirm=False, like

```
peek.to_clipboard(part1, confirm=False)
```

### General

Implementation detail: the clipboard functionality uses pyperclip, apart from under Pythonista, where the
builtin clipboard module is used.

This functionality is particularly useful for entering an answer of an *Advent of Code* solution to the site.

# Interpreting the line number information

When `show_line_number` is True or peek() is used without any parameters, the output will contain the line number like:
```
#3 ==> a='abcd'
```
If the line resides in another file than the main file, the filename (without the path) will be shown as well:
```
#30[foo.py] ==> foo='Foo'
```
And finally when used in a function or method, that function/method will be shown as well:
```
#456[foo.py] in square_root ==> x=123
```
The parent function can be suppressed by setting `show_line_number` or `sln` to `"n"` or `"no parent"`.

# Configuring at import time

It can be useful to configure peek at import time. This can be done by providing a `peek.toml` file which
can contain any attribute configuration overriding the standard settings.
E.g. if there is a `peek.toml` file with the following contents

```
outpout = "stderr"
show_time = true
ll = 160
quote_string = false
```
in the same folder as the application, this program:
```
hello = "world"
peek(hello)
```
will print something like this to stderr (rather than stdout):
```
@ 14:53:41.392190 ==> hello=world
```
At import time current directory will be searched for `peek.toml` and if not found, one level up, etc. until the root directory is reached.

Please observe that toml values are slightly different from their Python equivalents:
```
-----------------------------------
Python     toml
-----------------------------------
True       true
False      false
strings    preferably double quoted
-----------------------------------
```
Note that not-specified attributes will remain the default settings.

Just for your information, the core developer of peek uses a peek.toml file with the contents:
```
line_length = 160
color = "yellow"
quote_string = false
```



# Working with multiple instances of peek

Normally, only the `peek` object is used.

It can be useful to have multiple instances, e.g. when some of the debugging has to be done with context information
and others requires an alternative prefix.

There are several ways to obtain a new instance of peek:

*    by using `peek.new()`
     
     With this a new peek object is created with the default attributes
*    by using `peek.new(ignore_toml=True)`

     With this a new peekobject is created with the default attributes. Any peek.toml files are ignored.
*    by using `peek.fork()`
     
     With this a new peek object is created with the same attributes as the object it is created ('the parent') from. Note that any non set attributes are copied (propagated) from the parent.
*    by using `peek.clone()`, which copies all attributes from peek()

     With this a new peek object is created with the same attributes as the object it is created ('the parent') from. Note that the attributes are not propagated from the parent, in this case.

*    with `peek()` used as a context manager

In either case, attributes can be added to override the default ones.

### Example
```
peek_with_line_number = peek.fork(show_line_number=True)
peek_with_new_prefix = peek.new(prefix="==> ")
peek_with_new_prefix_and_time = peek_with_new_prefix.clone(show_time=True)
hello="world"
peek_with_line_number(hello)
peek_with_new_prefix(hello)
peek_with_new_prefix_and_time(hello)
peek.equals_separator = " == "  # this affects only the forked objects
peek_with_line_number(hello)
peek_with_new_prefix(hello)
peek_with_new_prefix_and_time(hello)
with peek(prefix="peek_cm ") as peek_cm:
    peek_cm(hello)
    peek(hello)
```
prints something like
```
#28 ==> hello='world'
==> hello='world'
==> @ 09:55:52.122818 ==> hello='world'
#32 ==> hello == 'world'
==> hello='world'
==> @ 09:55:52.125928 ==> hello='world'
peek_cm enter
peek_cm hello == 'world'
hello == 'world'
peek_cm exit in 0.001843 seconds
```

## ignore_toml
With `peek.new(ignore_toml=True)` an instance of peek without having applied any toml configuration file will be returned. That can be useful when guaranteeing the same output in several setups.

### Example
Suppose we have a `peek.toml` file in the current directory with the contents
```
{prefix="==>"}
```
Then
```
peek_post_toml = peek.new()
peek_ignore_toml = peek.new(ignore_toml=True)
hello = "world"
peek(hello)
peek_post_toml(hello)
peek_ignore_toml(hello)
```
prints
```
==>hello='world'
==>hello='world'
hello='world'
```

# Test script

On GitHub is a file `test_peek.py` that tests (and thus also demonstrates) most of the functionality
of peek.

It is very useful to have a look at the tests to see the features (some may be not covered (yet) in this readme).

# Using peek in a REPL

Peek may be used in a REPL, but with limited functionality:
* all arguments are just presented as such, i.e. no left-hand side, e.g.
```
  >> hello = "world"
  >>> peek(hello, hello * 2)
  'hello', 'hellohello'
  ('hello', 'hellohello')
```
* line numbers are never shown  
* use as a decorator is not supported
* use as a context manager is not supported

> [!NOTE]
>
> Under Python >=3.13 most of the normal peek functionality is available in the REPL. A reason to upgrade!


# Limitations

It is not possible to use peek:
* from a frozen application (e.g. packaged with PyInstaller)
* when the underlying source code has changed during execution

# Changelog

The changelog can be found here:

* https://github.com/salabim/peek/blob/main/changelog.md or
* https://salabim.org/peek/changelog


# Acknowledgement

The **peek** package is inspired by the **IceCream** package, but is a nearly complete rewrite. See https://github.com/gruns/icecream

Many thanks to the author Ansgar Grunseid / grunseid.com / grunseid@gmail.com .

The peek package is a rebrand of the **ycecream** package, with many enhancements.

# Differences with IceCream

The peek module was originally a fork of **IceCream**, but has many differences:

```
-----------------------------------------------------------------------------------------
characteristic                    peek                        IceCream
-----------------------------------------------------------------------------------------
default name                      peek                        ic
import method                     import peek                 from icecream import ic
number of files                   1                           several
usable without installation       yes                         no
can be used as a decorator        yes                         no
can be used as a context manager  yes                         no
can show traceback                yes                         no
can be used like print w/extras   yes (with peek.print)       no
allows non linefeed printing      yes (via end parameter)     requires patching
PEP8 (Pythonic) API               yes                         no
sorts dicts                       no by default, optional *)  yes
supports compact, indent,
and underscore_numbers
parameters of pprint              yes **)                     no
use from a REPL                   limited functionality       no
external configuration            via toml file               no
level control                     yes                         no 
observes line_length correctly    yes                         no
benchmarking functionality        yes                         no
suppress f-strings at left hand   optional                    no
indentation                       4 blanks (overridable)      length of prefix
forking and cloning               yes                         no
test script                       pytest                      unittest
colorize ***)                     yes, off by default         yes, on by default
-----------------------------------------------------------------------------------------
*)   under Python <= 3.7, dicts are always sorted
**)  under Python <= 3.7, numbers are never underscored
***) peek allows selection of colors, whereas IceCream does coloring based on contents.

```
![PyPI](https://img.shields.io/pypi/v/peek-python) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/peek-python) ![PyPI - Implementation](https://img.shields.io/pypi/implementation/peek)
![PyPI - License](https://img.shields.io/pypi/l/peek) ![ruff](https://img.shields.io/badge/style-ruff-41B5BE?style=flat) 
![GitHub last commit](https://img.shields.io/github/last-commit/salabim/peek)

