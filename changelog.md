### changelog | peek | like print, but easy.

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

