### changelog | peek | like print, but easy.

For the full documentation, see www.salabim.org/peek .

#### version 25.0.7  2025-01-19
- Overhaul of color enable/disable functionality:
  `as_colored_str` parameter does not exist anymore. Just `as_str`, combined with `use_color = True` will do the job.
  "stdout_no_color" for output does not exist anymore. "stdout", combined with `use_color = False` will do the job.
  The new attribute `use_color` can be used to control whether ANSI escapes will be emitted. By default `use_color` is True, so given colors will be observed.

#### version 25.0.6  2025-01-18

- peek now offers direct access to ANSI color escape sequences with `peek.ANSI.black`, `peek.ANSI.white`, `peek.ANSI.red`, `peek.ANSI.green`, `peek.ANSI.blue`, `peek.ANSI.cyan`, `peek.ANSI.magenta`, `peek.ANSI.yellow`, `peek.ANSI.light_black`, `peek.ANSI.light_white`, `peek.ANSI.light_red`, `peek.ANSI.light_green`, `peek.ANSI.light_blue`, `peek.ANSI.light_cyan`, `peek.ANSI.light_magenta`, `peek.ANSI.light_yellow` and `peek.reset`.

  E.g.

  ```
  peek(repr(peek.ANSI.red))
  ```

  will show

  ```
  repr(peek.ANSI.red)='\x1b[1;31m'
  ```

#### version 25.0.5  2025-01-17

- peek is not supported on Python < 3.9 anymore. Updated the pyproject.toml file accordingly.
#### version 25.0.4  2025-01-17
- Bug when running under Pythonista fixed.
- Left over from an internal debug print removed.

#### version 25.0.3  2025-01-15
- peeking all local or all global variables with the functionality as introduced in 25.0.2 didn't work properly if peek was called directly (not via the PeekModule). Fixed by introducing an optional _via_module to peek.
- peek no longer issues 'No source' warnings as it now automatically falls back to printing only the value in case the source can't be found or has changed.
- peek now uses light colors for black, white, ..., yellow, to make the output easier to read. If you would like the 'normal' colors, use dark_black, dark_white, ..., dark_yellow. See the read.me for an overview of the colors.
- It is now also possible to return peek's output as a string with the embedded ANSI color escape string(s). This is done by setting the `as_colored_str` argument to True:

  ```
  hello = "world"
  s = peek(hello, color="red", color_value="green", as_colored_str=True)
  print(repr(s), end="")
  ```

  prints

  ```
  "\x1b[1;31mhello=\x1b[1;32m'world'\x1b[1;31m\n\x1b[0m"
  ```


#### version 25.0.2  2025-01-13
- Introduced the possibility to print all local or all global variables.
  
  To do that, just put `locals` or `globals` in the call to peek:
  
  ```
  peek(locals)
  ```
  will print all local variables, apart from those starting with `__`
  
  Likewise,
  ```
  peek(globals)
  ```
  will print all global variables, apart from those starting with `__`  
  
  > [!IMPORTANT]
  >
  > You should not add parentheses after `locals` or `globals` for peek to work properly!
#### version 25.0.1  2025-01-09

- Introduced the format  attribute:

  With the format attribute, it is possible to apply a format specifier to each of the values to be printed, like

  ```
  test_float = 1.3
  peek(test_float, format="06.3f")
  ```
  
  This will print

  ```
  test_float=01.300
  ```
  
  The format should be like the Python format specifiers, with or without the `:` prefix, like `"6.3f"`, `">10"`, `"06d"`, `:6.3d`.
  It is also possible to use the `!` format specifier: `"!r"`, `"!r:>10"`.
  
  If format is the null string (`""`) (the default), this functionality is skipped completely.

  It is also possible to use a list (or tuple) of format specifiers, which are tried in succession. If they all fail, the 'normal' serializer will be used.

  ```
  test_float = 1.3
  test_integer=10
  test_string = "test"
  test_dict=dict(one=1, two=2)
  peek(test_float, test_integer, test_string, test_dict, format=["04d", "06.3f", ">10"])
  ```
  
  will result in

  ```
  test_float=01.300, test_integer=0010, test_string=      test, test_dict={'one': 1, 'two': 2}
  ```
  
  Of course, format may be put in a peek.toml file.

#### version 25.0.0  2025-01-07

* internal reorganization: all methods and constants are now in the _Peek class.
  

#### version 24.0.5  2024-12-28

* peek has a new attribute: `print_like` (alias `print`), which is False by default. If true, peek behaves like `peek.print`.
  
  This makes it possible to use `peek` as were it `print` , but with colors, filtering, optional line numbers, timing info, and enabling/disabling.
  
  E.g. if we first set
  
  ```
  peek.print_like = True
  ```
  and then
  ```
  peek(12, f"{min(1, 2)=}", list(range(4))
  ```
  it will print
    ```1
  2 min(1, 2)=1 [0, 1, 2, 3]
    ```
  `sep` and `end` are supported, so after setting print_like to True:
  
  ```
  peek(12, f"{min(1, 2)=}", list(range(4), sep="|",end="!\n"))
  ```
  will print
  ```
  12|min(1, 2)=1|[0, 1, 2, 3]!
  ```
  
  
  It is possible to use `print_like` in a call to peek, like
  ```
  peek(12, 13, 14, print_like=True)
  ```
  , but  it might be more convenient to use
  ```
  peek.print(12, 13, 14)
  ```
  > [!TIP]
  >
  > Of course, `print_like` can be set in a **peek.toml** file.

* Internal only: `peek.print` now just delegates to` peek(print_like=True)` 

#### version 24.0.4  2024-12-26

* Introduced the `end` attribute, which works like the end parameter of print. By default, `end` is "\n".
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
  Note that `\r` does not work under Pythonista.
  
* Introduced `peek.print` which allows peek to be used as an alternative to print. Note that `peek.print` obeys the `color`, `filter`, `enabled` and `as_str` and `output`.
  
  So we can say
  ```
  peek.color = "red"
  peek.filter = "level==1"
  peek.print(f"{max(1, 2)=}")
  peek.print(f"{min(1, 2)=}", level=1)
  ```
  will print
    ```
  min(1, 2)=1
    ```
  in red.
  
  In order to behave similar to print, peek has an extra attribute, `separator_print` or `sepp`. This attribute (default " ") will be used when `peek.printing`.
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
  
* `enforce_line_length` attribute phased out because of limited use
#### version 24.0.3  2024-12-24

* When both `peek.color` and `peek.color_value` were "-" or "", ansi escape sequences were still emitted. From now on, peek will suppress these.
* From now on `peek.color` may also be "". It acts exactly as "-".
  Just for your information, if `peek color_value` is "" it means use the `peek.color`, wheras if `peek.color_value` is "-", it means switch back to no color.

#### version 24.0.2  2024-12-23

* Bug when using peek with an *istr* (see www.salabim.org/istr) and `quote_string = False`. Fixed.
* Some minor code cleanups.

#### version 24.0.1  2024-12-22

* Some more refactoring to avoid code duplication.

* Changed several TypeError and ValueError exception to the more logical and consistent AttributeError

* Implemented `repr` and `str`, where delta is the initial value (which required an alternative way to store delta)

* Added some more test in the PyTest script

#### version 24.0.0  2024-12-20

* Completely refactored the way peek defaults and arguments are handled, leading to much more compact and
  better maintainable code. Also errors are better captured.
  
* This change makes it also possible to check for incorrect assignment of peek's attribute, like `peek.colour = 'red'`

* The show_level and show_color methods are replaced by the generic filter attribute, allowing more sophisticated filtering. E.g.
  ```
  peek.filter('color not in blue' and level >= 2')
  ```
  It is even possible to get access to all peek attributes in the filter condition, e.g.
  ```
  peek.filter('delta > 2')
  ```
  Note that peek checks the validity of a filter expression at definition time.
  
* to_clipboard is not anymore just an argument of peek, but is now an attribute. As a consequence,
  the method `to_clipboard` has been renamed. It is now `copy_to_clipboard`.
  
* to_clipboard will now put the *last* value on the clipboard (was the *first*)

* Introduced the *quote_string* attribute. If this attribute is set to False, strings will be displayed without surrounding quotes
  (like str). When True (the default), strings will be displayed with surrounding quotes (like repr). E.g.

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
  
* provided phased out because of limited use

* assert_ phased out because of limited use

* peek.toml is now only read once upon importing peek, which is more efficient and stable

* changed to calendar versioning, so this is version 24.0.0 .


#### version 1.8.8 2024-12-14

* color_value may now be also the null string ("") to indicate to use the color for the values as well. This also the default now.

#### version 1.8.7 2024-12-13

* introduced `peek.show_color()`, which makes it possible to show only output of given color(s).
  It is also possible to exclude given color(s).
  This works similar to `peek.show_level()`, including as a context manager.
* changed the *no color* attribute from `""` to `"-"` (this change was necessary for `peek.show_color()` to also include *no color*). So, for instance, `peek.show_color("not -")` will only show colored output.
* `peek.output` may now be **"stdout_nocolor"**, which makes that colors are ignored (this is primarily useful for tests).
* micro optimization by not inserting any ansi escape sequences if neither color nor color_value is specified.
* the build process will now automatically insert the latest version for each of the requirements.

#### version 1.8.4  2024-12-11

* all required modules in the pyproject.toml file now have a mininal version number (all the latest as of now).
  This is rather important as particularly older versions of *executing* may not compatible with *peek*.
  (inspired by an issue reported by Kirby James)

#### version 1.8.3  2024-12-10

* added an alternative way to copy peek output to the clipboard.
  From now on a call to peek has an optional keyword argument, *to_clipboard*:
  
  - If to_clipboard==False (the default), nothing is copied to the clipboard.
  - If to_clipboard==True, the *value* of the the *first* parameter will be copied to the clipboard. The output itself is as usual.
  
  Examples:
  
  ```
  part1 = 200
  extra = "extra"
  peek(part1, extra, to_clipboard=True)
      # will print part1=200, extra='extra' and copy 200 to the clipboard
  peek(200, to_clipboard=True)\
      # will print 200 and copy 200 to the clipboard
  peek(to_clipboard=True)
      # will print #5 (or similar) and empty the clipboard
  ```
  
  Note that *to_clipboard* is not a peek attribute and can only be used when calling `peek`,
  If as_str==True, to_clipboard is ignored.

#### version 1.8.2  2024-12-10

* updated *pyproject.toml* to correct the project.url information
  (inspired by a comment by Erik OShaughnessy) 

  

#### version 1.8.1  2024-12-09

* introduced the possibility to copy peek output to the clipboard. 

  Therefore peek has now a method `to_clipboard` which accepts a value to be copied to the clipboard.
  So,
  
  ```
  part1 = 1234
  peek.to_clipboard(part1)
  ```
  will copy `1234` to the clipboard and write `copied to clipboard: 1234` to the console.
  If the confirmation message is not wanted, just add confirm=False, like
  
  ```
  peek.to_clipboard(part1, confirm=False)
  ```
  Implementation detail: this functionality uses pyperclip, apart from under Pythonista, whre the
  builtin clipboard module is used.
  
  This functionality is particularly useful for entering an answer of an *Advent of Code* solution to the site.
  
  (inspired by a comment by Geir Arne Hjelle) 

#### version 1.8.0  2024-12-09

* `show_level` is now a method
  
* `show_level` is called slightly different as it is a method with a number (usually 1) of arguments.
  
  Each parameter may be:
  
  * a float value or
  
  - a string with the format *from* - *to*
    , where both *from* and *to* are optional. If *from* is omitted, -1E30 is assumed. If *to* is omitted, 1E30 is assumed. 
    Negative values have to be parenthesized.
  
  Examples:
  - `peek.show_level (1)` ==> show level 1
  - `peek.show_level (1, -3)` ==> show level 1 and level -3
  - `peek.show_level ("1-2")` ==> show level between 1 and 2
  - `peek.show_level("-")` ==> show all levels
  - `peek.show_level("")` ==> show no levels
  - `peek.show_level("1-")`==> show all levels >= 1
  - `peek.show_level("-10.2")`==> show all levels <=10.2
  - `peek.show_level(1, 2, "5-7", "10-")` ==> show levels 1, 2, between 5 and 7 (inclusive) and >= 10
  - `peek.show_level((-3)-3")` ==> show levels between -3 and 3 (inclusive)
  - `peek.show_level()` ==> returns the current show_level
  
* show_level can also be called with a minimum and/or a maximum value, e.g.

  - `peek.show_level(min=1)` ==> show all levels >= 1
  - `peek.show_level(max=10.2)` ==> show all levels <= 10.2
  - `peek.show_level(min=1, max=10)` ==> show all levels between 1 and 10 (inclusive)
  
  Note that min or max cannot be combined with a specifier as above

* `show_level` can now be used as a context manager as well:

  ```
  with peek.show_level(1):
      peek(1, level=1)
      peek(2, level=2)
  ```

  This will print one line with`1` only.

* color_value introduced. When specified, this is the color with which values are presented, e.g.
  ```
  test="test"
  peek(test, color="red", color_value="blue")
  ```

* colors on Pythonista are now handled via an ansi table lookup, thus being more reliable

* performance of peek when level is not to be shown or enabled==False significantly improved.

#### version 1.7.0  2024-12-03

* `show_level` element may be a range now, like "3-5', "-5", "3-".
* if `level` is the null string now, output is always suppressed.
* from this version on, it is required to have the following modules installed: `asttokens`, `colorama`, `executing`, `six`, `tomli`. These packages are in the pyproject.toml's dependencies, so normally these will be auto installed.
  The reason for this change is that some (potential) users didn't like the encrypted module contents.

#### version 1.6.2  2024-12-02

* bug with Python < 3.13. Fixed.

#### version 1.6.1  2024-12-02

* peek now has an advanced level system, which can be very practical to enable and disable debug information.

  See the readme file (e.g. on www.salabim.peek/changelog) for details.

#### version 1.6.0  2024-11-29

* peek now supports coloring of peek lines. Therefore, the attribute 'color' has been added.
  
  The following colors are available:
  
  - black
  - red
  - green
  - blue
  - yellow
  - cyan
  - magenta
  - white

  So, for instance, `peek(message, color="red")` or `peek.color = "green"`
  
  The attribute color has an abbreviated form: `col`, so, for instance, `peek_green = peek.new(col = "green")`
  
  Resetting the color can be done with the null string: `peek.color = ""`.
  
  The color attribute can, of course, also be set in a peek.toml file.

* changed the style badge in the readme.md file from ![Black](https://img.shields.io/badge/code%20style-black-000000.svg)  to ![ruff](https://img.shields.io/badge/style-ruff-41B5BE?style=flat) .

#### version 1.5.2  2024-11-19

* peek now uses a peek.toml file for customization, instead of a peek.json file.
  Also, the directory hierarchy is now searched for rather than sys.path.

* default line length is (again) 80. This change was made because it is now very easy to change the default line length with a toml file.
  
 #### version 1.5.1  2024-11-17

* peek is now also added to builtins, which means that you can just import it anywhere and it will become available in all modules.

#### version 1.5.0  2024-11-14

* default line length is now 160 (was 80)

* removed the fast disable functionality as from now only peek() without positional arguments is allowed
  for decorator and context manager
  
* phased out decorator/d and context_manager/cm parameters, because of limited use.

* phased out fast disabling logic, as that is not relevant anymore

* for decorator and context manager, positional arguments are not allowed. Not obeying
  this will result in a -possibly quite cryptic- error message
  
* @peek without parentheses was always discouraged, and is not allowed anymore

* use as decorator or context manager is not allowed in the REPL anymore


#### version 1.4.5  2024-11-07

* finally managed to support the `import peek` functionality correctly.

#### version 1.4.4  2024-11-06

* the new method of importing with `import peek` didn't work properly. So it is required to use `from peek import peek`

#### version 1.4.3  2024-11-06

* Output of peek now goes to stdout by default.
* Source of pprint not included anymore.
  The only consequence is that under Pyton<=3.7:
  * dicts are always sorted under Python <=3.7 (regardless of the sort_dicts attribute)
  * numbers cannot be underscored under Python <= 3.7 (regardless of the underscore_numbers attribute)
* The default prefix is now "" (the null string) (was: "peek| ")
* The equals_separator is now "=" (was ": ")

#### version 1.4.2  2024-11-04

* Initial release.

* Rebrand of ycecream with several enhancement, particularly the `import peek` functionality.

