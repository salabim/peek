### changelog | peek | like print, but easy.

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

