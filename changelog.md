### changelog | peek | like print, but easy.

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

* peek now supports colouring of peek lines. Therefore, the attribute 'color' has been added.
  
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

* peek is now also added to builtins, which means that you can just import it anywhere and it will become available
  in all modules.

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

