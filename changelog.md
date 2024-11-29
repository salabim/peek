### changelog | peek | like print, but easy.

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

