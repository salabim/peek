import base64
import zlib
from pathlib import Path
import sys
import os


def embed_package(infile, package, prefer_installed=False, py_files_only=True, outfile=None):
    """
    build outfile from infile with package(s) as mentioned in package embedded

    Arguments
    ---------
    infile : str or pathlib.Path
        input file

    package : str or tuple/list of str
        package(s) to be embedded

    prefer_installed : bool or tuple/list of bool
        if False (default), mark as to always use the embedded version (at run time)
        if True, mark as to try and use the installed version of package (at run time)
        if multiple packages are specified and prefer_installed is a scalar, the value will
            be applied for all packages

    py_files_only : bool or tuple/list of bool
        if True (default), embed only .py files
        if False, embed all files, which can be useful for certain data, fonts, etc, to be present
        if multiple packages are specified and py_files_only is a scalar, the value will
            be applied for all packages

    outfile : str or pathlib.Path
        output file
        if None, use infile with extension .embedded.py instead of .py

    Returns
    -------
    packages embedded : list
        when a package is not found or not embeddable, it is excluded from this list
    """
    infile = Path(infile)  # for API
    if outfile is None:
        outfile = infile.parent / (infile.stem + ".embedded" + infile.suffix)

    with open(infile, "r") as f:
        inlines = f.read().split("\n")

    inlines_iter = iter(inlines)
    inlines = []
    for line in inlines_iter:
        if line.startswith("def copy_contents("):
            while not line.startswith("del copy_contents"):
                line = next(inlines_iter)
        else:
            inlines.append(line)

    with open(outfile, "w") as out:
        if inlines[0].startswith("#!"):
            print(inlines.pop(0), file=out)
        for lineno, line in enumerate(reversed(inlines)):
            if line.startswith("from __future__ import"):
                for _ in range(lineno):
                    print(inlines.pop(0), file=out)
                    break

        packages = package if isinstance(package, (tuple, list)) else [package]
        n = len(packages)
        prefer_installeds = prefer_installed if isinstance(prefer_installed, (tuple, list)) else n * [prefer_installed]
        py_files_onlys = py_files_only if isinstance(py_files_only, (tuple, list)) else n * [py_files_only]
        if len(prefer_installeds) != n:
            raise ValueError(f"length of package != length of prefer_installed")
        if len(py_files_onlys) != n:
            raise ValueError(f"length of package != length of py_files_only")

        embedded_packages = [package for package in packages if _package_location(package)]

        for line in inlines:
            if line.startswith("import"):
                break
            print(line, file=out)

        print("def copy_contents(package, prefer_installed, filecontents):", file=out)
        print("    import tempfile", file=out)
        print("    import shutil", file=out)
        print("    import sys", file=out)
        print("    from pathlib import Path", file=out)
        print("    import zlib", file=out)
        print("    import base64", file=out)
        print("    if package in sys.modules:", file=out)
        print("        return", file=out)
        print("    if prefer_installed:", file=out)
        print("        for dir in sys.path:", file=out)
        print("            dir = Path(dir)", file=out)
        print("            if (dir / package).is_dir() and (dir / package / '__init__.py').is_file():", file=out)
        print("                return", file=out)
        print("            if (dir / (package + '.py')).is_file():", file=out)
        print("                return", file=out)
        print("    target_dir = Path(tempfile.gettempdir()) / ('embedded_' + package) ", file=out)
        print("    if target_dir.is_dir():", file=out)
        print("        shutil.rmtree(target_dir, ignore_errors=True)", file=out)
        print("    for file, contents in filecontents:", file=out)
        print("        ((target_dir / file).parent).mkdir(parents=True, exist_ok=True)", file=out)
        print("        with open(target_dir / file, 'wb') as f:", file=out)
        print("            f.write(zlib.decompress(base64.b64decode(contents)))", file=out)
        print("    sys.path.insert(prefer_installed * len(sys.path), str(target_dir))", file=out)

        for package, prefer_installed, py_files_only in zip(packages, prefer_installeds, py_files_onlys):
            dir = _package_location(package)

            if dir:
                print(f"copy_contents(package={repr(package)}, prefer_installed={repr(prefer_installed)}, filecontents=(", file=out)
                if dir.is_file():
                    files = [dir]
                else:
                    files = dir.rglob("*.py" if py_files_only else "*.*")
                for file in files:
                    if dir.is_file():
                        filerel = Path(file.name)
                    else:
                        filerel = file.relative_to(dir.parent)
                    if all(part != "__pycache__" for part in filerel.parts):
                        with open(file, "rb") as f:
                            fr = f.read()
                            print(f"    ({repr(filerel.as_posix())},{repr(base64.b64encode(zlib.compress(fr)))}),", file=out)
                print("))", file=out)

        print("del copy_contents", file=out)
        print(file=out)
        started = False
        for line in inlines:
            if not started:
                started = line.startswith("import")
            if started:
                print(line, file=out)
        return embedded_packages


def _package_location(package):
    for path in sys.path:
        path = Path(path)
        if (path.stem == "site-packages") or (path.resolve() == Path.cwd().resolve()):
            if (path / package).is_dir():
                if (path / package / "__init__.py").is_file():
                    return path / package
            if (path / (package + ".py")).is_file():
                return path / (package + ".py")
    return None


def main():
    file_folder = Path(__file__).parent
    os.chdir(file_folder / ".." / "peek")
    embed_package(
        infile="peek.py", package=["executing", "asttokens", "six", "tomli", "colorama"], prefer_installed=False, py_files_only=False, outfile="peek.py"
    )


if __name__ == "__main__":
    main()
    print("done")

