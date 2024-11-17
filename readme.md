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

* [Return a string instead of sending to output](#return-a-string-instead-of-sending-to-output)

* [Disabling peek's output](#disabling-peeks-output)

* [Speeding up disabled peek](#speeding-up-disabled-peek)

* [Using peek as a substitute for `assert`](#using-peek-as-a-substitute-for-assert)

* [Interpreting the line number information](#interpreting-the-line-number-information)

* [Configuring at import time](#configuring-at-import-time)

* [Working with multiple instances of peek](#working-with-multiple-instances-of-peek)

* [Test script](#test-script)

* [Using peek in a REPL](#using-peek-in-a-repl)

* [Alternative to `peek`](#alternative-to-peek)

* [Alternative installation](#alternative-installation)

* [Limitations](#limitations)

* [Implementation details](#implementation-details)

* [Acknowledgement](#acknowledgement)

* [Changelog](#changelog)

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

Alternatively, peek.py can be juist copied into you current work directory from GitHub (https://github.com/salabim/peek).

No dependencies!

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
Just give `peek()` a variable or expression and you're done. Easy, or what?


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
Just call `peek()` and you're done. Isn't that easy?


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
prefix                  pr              ""
output                  o               "stdout"
serialize                               pprint.pformat
show_line_number        sln             False
show_time               st              False
show_delta              sd              False
show_enter              se              True
show_exit               sx              True
show_traceback          stb             False
sort_dicts              sdi             False
underscore_numbers      un              False
enabled                 e               True
line_length             ll              160
compact                 c               False
indent                  i               1
depth                   de              1000000
wrap_indent             wi              "     "   
separator               sep             ", "
context_separator       cs              " ==> "
equals_separator        es              "="
values_only             vo              False
value_only_for_fstrings voff            False 
return_none             rn              False
enforce_line_length     ell             False
delta                   dl              0
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
It is also possible to configure peek permanently with the configure method. 
```
peek.configure(prefix="==> ")
peek(12)
```
will print
```
==> 12
```
It is arguably easier to say:
```
peek.prefix = "==> "
peek(12)
```
or even
```
peek.pr = "==> "
peek(12)
```
to print
```
==> 12
```
Yet another way to configure peek is to get a new instance of peek with peek.new() and the required configuration:
```
z = peek.new(prefix="==> ")
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

## output / o
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


## show_traceback / stb
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
This attribute is used to specify the line length (for wrapping). The default is 160.
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

## compact / c
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

## indent / i
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

## depth / de
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

## wrap_indent / wi
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

## enabled / e
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

## sort_dicts / sdi
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

## seperator / sep

By default, pairs (on one line) are separated by `, `.
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
a='abcd', (b,c)=(1, 1000), d=['peek', 'c', 'e', 'c', 'r', 'e', 'a', 'm']
a='abcd' | (b,c)=(1, 1000) | d=['peek', 'c', 'e', 'c', 'r', 'e', 'a', 'm']
```
Note that under Python <=3.7, numbers are never printed with underscores.

## context_separator / cs

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
## equals_separator / es
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
The values=True version of peek can be seen as a supercharged print/pprint.


## values_only_for_fstrings / voff
If False (the default), both the original f-string and the
value will be printed for f-strings.
If True, the left_hand side will be suppressed in case of an f-string:

```
x = 12.3
peek(f"{x:0.3e}")
peek.values_only_for_fstrings = True
peek(f"{x:0.3e}")
```
prints
```
f"{x:0.3e}"='1.230e+01'
'1.230e+01'
```
Note that if `values_only` is True, f-string will be suppressed, regardless of `values_only_for_fstrings`.

## return_none / rn
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

## enforce_line_length / ell
If enforce_line_length is True, all output lines are explicitly truncated to the given line_length, even those that are not truncated by pformat.

## delta / dl
The delta attribute can be used to (re)set the current delta, e.g.
```
peek.dl = 0
print(peek.delta)
```
prints a value that id slightly more than 0.


## provided / pr
If provided is False, all output for this call will be suppressed.
If provided is True, output will be generated as usual (obeying the enabled attribute).

```
x = 1
peek("should print", provided=x > 0)
peek("should not print", provided=x < 0)
```
This will print
```
should print
```

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
Of course `peek()` continues to return its arguments when disabled, of course.

It is also possible to suppress output with the provided attribute (see above).

# Using peek as a substitute for `assert`

Peek has a method `assert_` that works like `assert`, but can be enabled or disabled with the enabled flag.

```
temperature = -1
peek.assert_(temperature > 0)
```
This will raise an AttributeError.

But
```
peek.enabled = False
temperature = -1
peek.assert_(temperature > 0)
```
will not.

Note that with the attribute propagation method, you can in effect have a layered assert system.

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

It can be useful to configure peek at import time. This can be done by providing a `peek.json` file which
can contain any attribute configuration overriding the standard settings.
E.g. if there is an `peek.json` file with the following contents

```
{
    "o": "stderr",
    "show_time": true,
    "line_length": 80`
    'compact' : true
}
```
in the same folder as the application, this program:
```
hello = "world"
peek(hello)
```
will print to stderr (rather than stdout):
```
@ 14:53:41.392190 ==> hello='world'
```
At import time the sys.path will be searched for, in that order, to find a `peek.json` file and use that. This means that 
you can place a `peek.json` file in the site-packages folder where `peek` is installed to always use
these modified settings.

Please observe that json values are slightly different from their Python equivalents:
```
-------------------------------
Python     json
-------------------------------
True       true
False      false
None       none
strings    always double quoted
-------------------------------
```
Note that not-specified attributes will remain the default settings.

For obvious reasons, it is not possible to specify `serialize` in an peek.json file.

# Working with multiple instances of peek

Normally, only the `peek()` object is used.

It can be useful to have multiple instances, e.g. when some of the debugging has to be done with context information
and others requires an alternative prefix.

THere are several ways to obtain a new instance of peek:

*    by using `peek.new()`
     
     With this a new peek object is created with the default attributes
     and possibly peek.json overrides.
*    by using `peek.new(ignore_json=True)`

     With this a new peekobject is created with the default attibutes. Any peek.json files asre ignored.
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

## ignore_json
With `peek.new(ignore_json=True)` an instance of peek without having applied any json configuration file will be returned. That can be useful when guaranteeing the same output in several setups.

### Example
Suppose we have a `peek.json` file in the current directory with the contents
```
{prefix="==>"}
```
Then
```
peek_post_json = peek.new()
peek_ignore_json = peek.new(ignore_json=True)
hello = "world"
peek(hello)
peek_post_json(hello)
peek_ignore_json(hello)
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

# Alternative to `peek`

Sometimes, even peek is too long during a debug session or it is not suitable to use the name peek.

In that case, it is possible to use p instead
```
from peek import p
```
The `p` object is a *fork* of peek. That means that attributes of `peek` are propagated to `p`, unless overridden.


# Limitations

It is not possible to use peek:
* from a frozen application (e.g. packaged with PyInstaller)
* when the underlying source code has changed during execution

# Implementation details

Although not important for using the package, here are some implementation details:
* peek.py contains the complete source of the asttokens, executing and six packages, in
  order to offer the required source lookups, without any dependencies
* in order to support using peek() as a decorator and a context manager, peek caches the complete source of
  any source file that uses peek()

# Changelog

The changelog can be found here:

* https://github.com/salabim/peek/main/changelog.md or
* https://salabim.org/peek/changelog


# Acknowledgement

The **peek** package is inspired by the **IceCream** package, but is a 
nearly complete rewrite. See https://github.com/gruns/icecream

Many thanks to the author Ansgar Grunseid / grunseid.com / grunseid@gmail.com .

The peek package is a rebrand of the **ycecream** package, with enhancements.

# Differences with IceCream

The peek module was originally a fork of **IceCream**, but has many differences:

```
-------------------------------------------------------------------------------------------
characteristic                    peek                        IceCream
-------------------------------------------------------------------------------------------
default name                      peek                        ic
import method                     import peek                 from icecream import ic
dependencies                      none                        many
number of files                   1                           several
usable without installation       yes                         no
can be used as a decorator        yes                         no
can be used as a context manager  yes                         no
can show traceback                yes                         no
PEP8 (Pythonic) API               yes                         no
sorts dicts                       no by default, optional *)  yes
supports compact, indent,
and underscore_numbers
parameters of pprint              yes **)                     no
use from a REPL                   limited functionality       no
external configuration            via json file               no
observes line_length correctly    yes                         no
default line length               160                         80
benchmarking functionality        yes                         no
suppress f-strings at left hand   optional                    no
indentation                       4 blanks (overridable)      dependent on length of prefix
forking and cloning               yes                         no
test script                       pytest                      unittest
colourize                         no                          yes (can be disabled)
-------------------------------------------------------------------------------------------
*)  under Python <= 3.7, dicts are always sorted (regardless of the sort_dicts attribute
**) under Python <= 3.7, numbers are never underscored (regardless of the underscore_numnbers attribute


```
![PyPI](https://img.shields.io/pypi/v/peek) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/peek-python) ![PyPI - Implementation](https://img.shields.io/pypi/implementation/peek)

![PyPI - License](https://img.shields.io/pypi/l/peek) ![Black](https://img.shields.io/badge/code%20style-black-000000.svg) 
![GitHub last commit](https://img.shields.io/github/last-commit/salabim/peek)

