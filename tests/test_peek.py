from __future__ import print_function
from __future__ import division

import sys
import datetime
import time
import pytest
import os
from pathlib import Path


file_folder = os.path.dirname(__file__)
os.chdir(file_folder)
sys.path.insert(0, file_folder + "/../peek")

import peek


peek = peek.new(ignore_toml=True, output="stdout_nocolor")


class g:
    pass


context_start = "#"

Pythonista = sys.platform == "ios"

FAKE_TIME = datetime.datetime(2021, 1, 1, 0, 0, 0)


@pytest.fixture
def patch_datetime_now(monkeypatch):
    class mydatetime:
        @classmethod
        def now(cls):
            return FAKE_TIME

    monkeypatch.setattr(datetime, "datetime", mydatetime)


def test_time(patch_datetime_now):
    hello = "world"
    s = peek(hello, show_time=True, as_str=True)
    assert s == "@ 00:00:00.000000 ==> hello='world'\n"


def test_no_arguments(capsys):
    result = peek()
    out, err = capsys.readouterr()
    assert out.startswith(context_start)
    assert out.endswith(" in test_no_arguments()\n")
    assert result is None


def test_one_arguments(capsys):
    hello = "world"
    result = peek(hello)
    peek(hello)
    out, err = capsys.readouterr()
    assert (
        out
        == """\
hello='world'
hello='world'
"""
    )
    assert result == hello


def test_illegal_assignment():
    with pytest.raises(AttributeError):
        peek.colour = "red"


def test_two_arguments(capsys):
    hello = "world"
    ll = [1, 2, 3]
    result = peek(hello, ll)
    out, err = capsys.readouterr()
    assert out == "hello='world', ll=[1, 2, 3]\n"
    assert result == (hello, ll)


def test_in_function(capsys):
    def hello(val):
        peek(val, show_line_number=True)

    hello("world")
    out, err = capsys.readouterr()
    assert out.startswith(context_start)
    assert out.endswith(" in test_in_function.hello() ==> val='world'\n")


def test_in_function_no_parent(capsys):
    def hello(val):
        peek(val, show_line_number="n")

    hello("world")
    out, err = capsys.readouterr()
    assert out.startswith(context_start)
    assert not out.endswith(" in test_in_function_no_parent.hello() ==> val='world'\n")


def test_prefix(capsys):
    hello = "world"
    peek(hello, prefix="==> ")
    out, err = capsys.readouterr()
    assert out == "==> hello='world'\n"


def test_time_delta():
    sdelta0 = peek(1, show_delta=True, as_str=True)
    stime0 = peek(1, show_time=True, as_str=True)
    time.sleep(0.001)
    sdelta1 = peek(1, show_delta=True, as_str=True)
    stime1 = peek(1, show_time=True, as_str=True)
    assert sdelta0 != sdelta1
    assert stime0 != stime1
    peek.delta = 10
    time.sleep(0.1)
    assert 10.05 < peek.delta < 11


def test_dynamic_prefix(capsys):
    g.i = 0

    def prefix():
        g.i += 1
        return str(g.i) + ")"

    hello = "world"
    peek(hello, prefix=prefix)
    peek(hello, prefix=prefix)
    out, err = capsys.readouterr()
    assert out == "1)hello='world'\n2)hello='world'\n"


def test_values_only():
    with peek.preserve():
        peek.configure(values_only=True)
        hello = "world"
        s = peek(hello, as_str=True)
        assert s == "'world'\n"


def test_calls():
    with pytest.raises(AttributeError):
        peek.new(a=1)
    with pytest.raises(AttributeError):
        peek.clone(a=1)
    with pytest.raises(AttributeError):
        peek.configure(a=1)
    with pytest.raises(AttributeError):
        peek(12, a=1)
    with pytest.raises(AttributeError):
        peek(a=1)


def test_repr_and_str(capsys):
    print(str(peek))
    out, err = capsys.readouterr()
    assert out.startswith("peek with attributes:")
    assert out.endswith(")\n")

    print(repr(peek))
    out, err = capsys.readouterr()
    assert out.startswith("peek.new(")
    assert out.endswith(")\n")

def test_output(capsys, tmpdir):
    g.result = ""

    def my_output(s):
        g.result += s

    hello = "world"
    peek(hello, output=print)
    out, err = capsys.readouterr()
    assert out == "hello='world'\n"

    peek(hello, output=sys.stdout)
    out, err = capsys.readouterr()
    assert out == "hello='world'\n"

    peek(hello, output="stdout_nocolor")
    out, err = capsys.readouterr()
    assert out == "hello='world'\n"

    peek(hello, output="")
    out, err = capsys.readouterr()
    assert out == ""

    peek(hello, output="null")
    out, err = capsys.readouterr()
    assert out == ""

    peek(hello, output=print)
    out, err = capsys.readouterr()
    assert out == "hello='world'\n"

    path = Path(tmpdir) / "x0"
    peek(hello, output=path)
    out, err = capsys.readouterr()
    assert out == ""

    with path.open("r") as f:
        assert f.read() == "hello='world'\n"

    path = Path(tmpdir) / "x1"
    peek(hello, output=path)
    out, err = capsys.readouterr()
    assert out == ""

    with path.open("r") as f:
        assert f.read() == "hello='world'\n"

    path = Path(tmpdir) / "x2"
    with path.open("a+") as f:
        peek(hello, output=f)

    with pytest.raises(AttributeError):  # closed file
        peek(hello, output=f)
    out, err = capsys.readouterr()
    assert out == ""

    with path.open("r") as f:
        assert f.read() == "hello='world'\n"

    with pytest.raises(AttributeError):
        peek(hello, output=1)

    peek(hello, output=my_output)
    peek(1, output=my_output)
    out, err = capsys.readouterr()
    assert out == ""
    assert out == ""
    assert g.result == "hello='world'\n1\n"

    def test_serialize(capsys):
        def serialize(s):
            return repr(s) + " [len=" + str(len(s)) + "]"

        hello = "world"
        peek(hello, serialize=serialize)
        out, err = capsys.readouterr()
        assert out == "hello='world' [len=5]\n"


def test_show_time(capsys):
    hello = "world"
    peek(hello, show_time=True)
    out, err = capsys.readouterr()
    assert out.endswith("hello='world'\n")
    assert "@ " in out


def test_show_delta(capsys):
    hello = "world"
    peek(hello, show_delta=True)
    out, err = capsys.readouterr()
    assert out.endswith("hello='world'\n")
    assert "delta=" in out


def test_as_str(capsys):
    hello = "world"
    s = peek(hello, as_str=True)
    peek(hello)
    out, err = capsys.readouterr()
    assert out == s

    with pytest.raises(TypeError):

        @peek(as_str=True)
        def add2(x):
            return x + 2

    with pytest.raises(TypeError):
        with peek(as_str=True):
            pass


def test_print(capsys):
    peek.print(*range(4))
    peek.print(*range(4), sep="|")
    peek.print(*range(4), end="END\n")
    peek.filter = "1<=level<=2"
    for i in range(4):
        peek.print(i, level=i)
    out, err = capsys.readouterr()
    peek.filter = ""
    assert (
        out
        == """\
0 1 2 3
0|1|2|3
0 1 2 3END
1
2
"""
    )
    result=peek.print(1,2,as_str=True)
    assert result=="1 2\n"

    result=peek.print(1,2)
    assert result is None


    with pytest.raises(AttributeError):
        peek.print(sep="|", sepp="/")   

    with pytest.raises(AttributeError):
        peek.print(line_length=120)   

    with pytest.raises(AttributeError):
        peek.print(line_length=120)   


def test_clone():
    hello = "world"
    z = peek.clone()
    z.configure(prefix="z| ")
    sy = peek(hello, as_str=True)
    with peek.preserve():
        peek.configure(show_line_number=True)
        sz = z(hello, as_str=True)
        assert sz.replace("z| ", "") == sy


def test_sort_dicts():
    world = {"EN": "world", "NL": "wereld", "FR": "monde", "DE": "Welt"}
    s0 = peek(world, as_str=True)
    s1 = peek(world, sort_dicts=False, as_str=True)
    s2 = peek(world, sort_dicts=True, as_str=True)
    if sys.version_info >= (3, 8):
        assert s0 == "world={'EN': 'world', 'NL': 'wereld', 'FR': 'monde', 'DE': 'Welt'}\n"
        assert s1 == "world={'EN': 'world', 'NL': 'wereld', 'FR': 'monde', 'DE': 'Welt'}\n"
        assert s2 == "world={'DE': 'Welt', 'EN': 'world', 'FR': 'monde', 'NL': 'wereld'}\n"
    else:
        assert s0 == s1 == s2 == "world={'DE': 'Welt', 'EN': 'world', 'FR': 'monde', 'NL': 'wereld'}\n"


def test_underscore_numbers():
    numbers = dict(x1=1, x2=1000, x3=1000000, x4=1234567890)
    s0 = peek(numbers, as_str=True)
    s1 = peek(numbers, underscore_numbers=True, as_str=True)
    s2 = peek(numbers, un=False, as_str=True)

    if sys.version_info >= (3, 8):
        assert s0 == s2 == "numbers={'x1': 1, 'x2': 1000, 'x3': 1000000, 'x4': 1234567890}\n"
        assert s1 == "numbers={'x1': 1, 'x2': 1_000, 'x3': 1_000_000, 'x4': 1_234_567_890}\n"
    else:
        assert s0 == s1 == s2 == "numbers={'x1': 1, 'x2': 1000, 'x3': 1000000, 'x4': 1234567890}\n"


@pytest.mark.skipif(Pythonista, reason="Pythonista problem")
def test_multiline():
    a = 1
    b = 2
    ll = list(range(15))
    # fmt: off
    s = peek((a, b),
        [ll,
        ll], as_str=True, line_length=80)
    # fmt: on
    assert (
        s
        == """\
(a, b)=(1, 2)
[ll,
ll]=
    [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
     [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]]
"""
    )

    lines = "\n".join("line{i}".format(i=i) for i in range(4))
    result = peek(lines, as_str=True)
    assert (
        result
        == """\
lines=
    'line0
    line1
    line2
    line3'
"""
    )


def test_filter(capsys):
    def gen():
        for level, color in enumerate("- blue red green blue".split()):
            peek(level, level=level, color=color)

    peek.filter = "True"
    gen()
    peek.filter = "level >=2"
    gen()
    peek.filter = "level >=2"
    gen()
    peek.filter = "level >=2 and color=='blue'"
    gen()
    peek.filter = ""
    gen()

    out, err = capsys.readouterr()
    assert (
        out
        == """\
level=0
level=1
level=2
level=3
level=4
level=2
level=3
level=4
level=2
level=3
level=4
level=4
level=0
level=1
level=2
level=3
level=4
"""
    )


@pytest.mark.skipif(Pythonista, reason="Pythonista does not generate ansi codes")
def test_color(capsys):
    peek(10 * 10, output="stdout")
    peek(10 * 10, color="red", output="stdout")
    out, err = capsys.readouterr()
    assert out == "10 * 10=100\n\x1b[0;31m10 * 10=100\n\x1b[0m"


def test_incorrect_filter():
    with pytest.raises(AttributeError):
        peek.filter = "color='blue'"

    with pytest.raises(AttributeError):
        peek.filter = "colour=='blue'"


def test_decorator(capsys):
    peek.fix_perf_counter(0)

    @peek()
    def div(x, y):
        return x / y

    @peek(show_enter=False)
    def add(x, y):
        return x + y

    @peek(show_exit=False)
    def sub(x, y):
        return x - y

    @peek(show_enter=False, show_exit=False)
    def pos(x, y):
        return x**y

    assert div(10, 2) == 10 / 2
    assert add(2, 3) == 2 + 3
    assert sub(10, 2) == 10 - 2
    assert pow(10, 2) == 10**2
    out, err = capsys.readouterr()
    assert (
        out
        == """\
called div(10, 2)
returned 5.0 from div(10, 2) in 0.000000 seconds
returned 5 from add(2, 3) in 0.000000 seconds
called sub(10, 2)
"""
    )
    peek.fix_perf_counter(None)


def test_decorator_edge_cases(capsys):
    peek.fix_perf_counter(0)

    @peek()
    def mul(x, y, factor=1):
        return x * y * factor

    assert mul(5, 6) == 30
    assert mul(5, 6, 10) == 300
    assert mul(5, 6, factor=10) == 300
    out, err = capsys.readouterr()
    assert (
        out
        == """\
called mul(5, 6)
returned 30 from mul(5, 6) in 0.000000 seconds
called mul(5, 6, 10)
returned 300 from mul(5, 6, 10) in 0.000000 seconds
called mul(5, 6, factor=10)
returned 300 from mul(5, 6, factor=10) in 0.000000 seconds
"""
    )
    peek.fix_perf_counter(None)


def test_decorator_with_methods(capsys):
    class Number:
        def __init__(self, value):
            self.value = value

        @peek(show_exit=False)
        def __mul__(self, other):
            if isinstance(other, Number):
                return self.value * other.value
            else:
                return self.value * other

        def __repr__(self):
            return self.__class__.__name__ + "(" + str(self.value) + ")"

    with peek.preserve():
        peek.output = "stderr"
        a = Number(2)
        b = Number(3)
        print(a * 2)
        print(a * b)
        out, err = capsys.readouterr()
        assert (
            err
            == """\
called __mul__(Number(2), 2)
called __mul__(Number(2), Number(3))
"""
        )
        assert (
            out
            == """4
6
"""
        )


@pytest.mark.skipif(Pythonista, reason="Pythonista problem")
def test_context_manager(capsys):
    peek.fix_perf_counter(0)
    with peek():
        peek(3)
    out, err = capsys.readouterr()
    assert (
        out
        == """\
enter
3
exit in 0.000000 seconds
"""
    )
    peek.fix_perf_counter(None)


def test_return_none(capsys):
    a = 2
    result = peek(a, a)
    assert result == (a, a)
    result = peek(a, a, return_none=True)
    assert result is None
    out, err = capsys.readouterr()
    assert (
        out
        == """\
a=2, a=2
a=2, a=2
"""
    )


@pytest.mark.skipif(Pythonista, reason="Pythonista problem")
def test_wrapping(capsys):
    l0 = "".join("         {c}".format(c=c) for c in "12345678") + "\n" + "".join(".........0" for c in "12345678")

    print(l0)
    ccc = cccc = 3 * ["12345678123456789012"]
    ccc0 = [cccc[0] + "0"] + cccc[1:]
    with peek.preserve():
        peek.prefix = "peek| "
        peek.line_length = 80
        peek(ccc)
        peek(cccc)
        peek(ccc0)

    out, err = capsys.readouterr()
    assert (
        out
        == """\
         1         2         3         4         5         6         7         8
.........0.........0.........0.........0.........0.........0.........0.........0
peek|
    ccc=['12345678123456789012', '12345678123456789012', '12345678123456789012']
peek|
    cccc=
        ['12345678123456789012', '12345678123456789012', '12345678123456789012']
peek|
    ccc0=
        ['123456781234567890120',
         '12345678123456789012',
         '12345678123456789012']
"""
    )
    a = "1234"
    b = bb = 9 * ["123"]
    print(l0)
    with peek.preserve():
        peek.prefix = "peek| "
        peek.line_length = 80
        peek(a, b)
        peek(a, bb)
    out, err = capsys.readouterr()
    assert (
        out
        == """\
         1         2         3         4         5         6         7         8
.........0.........0.........0.........0.........0.........0.........0.........0
peek|
    a='1234'
    b=['123', '123', '123', '123', '123', '123', '123', '123', '123']
peek|
    a='1234'
    bb=['123', '123', '123', '123', '123', '123', '123', '123', '123']
"""
    )
    dddd = 10 * ["123"]
    dddd = ddddd = 10 * ["123"]
    e = "a\nb"
    print(l0)
    with peek.preserve():
        peek.prefix = "peek| "
        peek.line_length = 80
        peek(a, dddd)
        peek(a, ddddd)
        peek(e)
    out, err = capsys.readouterr()
    assert (
        out
        == """\
         1         2         3         4         5         6         7         8
.........0.........0.........0.........0.........0.........0.........0.........0
peek|
    a='1234'
    dddd=['123', '123', '123', '123', '123', '123', '123', '123', '123', '123']
peek|
    a='1234'
    ddddd=['123', '123', '123', '123', '123', '123', '123', '123', '123', '123']
peek|
    e=
        'a
        b'
"""
    )
    a = aa = 2 * ["0123456789ABC"]
    print(l0)
    with peek.preserve():
        peek.prefix = "peek| "
        peek(a, line_length=40)
        peek(aa, line_length=40)
        peek(aa, line_length=41)
    out, err = capsys.readouterr()
    assert (
        out
        == """\
         1         2         3         4         5         6         7         8
.........0.........0.........0.........0.........0.........0.........0.........0
peek|
    a=['0123456789ABC', '0123456789ABC']
peek|
    aa=
        ['0123456789ABC',
         '0123456789ABC']
peek|
    aa=['0123456789ABC', '0123456789ABC']
"""
    )


def test_compact(capsys):
    a = 9 * ["0123456789"]
    peek(a, ll=80)
    peek(a, compact=True, ll=80)
    out, err = capsys.readouterr()
    assert (
        out
        == """\
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
"""
    )


def test_depth_indent(capsys):
    s = "=============================================="
    a = [s + "1", [s + "2", [s + "3", [s + "4"]]], s + "1"]
    peek(a, indent=4, ll=80)
    peek(a, depth=2, indent=4, ll=80)
    out, err = capsys.readouterr()
    assert (
        out
        == """\
a=
    [   '==============================================1',
        [   '==============================================2',
            [   '==============================================3',
                ['==============================================4']]],
        '==============================================1']
a=
    [   '==============================================1',
        ['==============================================2', [...]],
        '==============================================1']
"""
    )


def test_enabled(capsys):
    with peek.preserve():
        peek("One")
        peek.configure(enabled=False)
        peek("Two")
        s = peek("Two", as_str=True)
        assert s == ""
        peek.configure(enabled=True)
        peek("Three")

    out, err = capsys.readouterr()
    assert (
        out
        == """\
'One'
'Three'
"""
    )


def test_enabled2(capsys):
    with peek.preserve():
        peek.configure(enabled=False)
        line0 = peek("line0")
        noline0 = peek(prefix="no0")
        pair0 = peek("p0", "p0")
        s0 = peek("s0", as_str=True)
        peek.configure(enabled=[])
        line1 = peek("line1")
        noline1 = peek(prefix="no1")
        pair1 = peek("p1", "p1")
        s1 = peek("s1", as_str=True)
        peek.configure(enabled=True)
        line2 = peek("line2")
        noline2 = peek(prefix="no2")
        pair2 = peek("p2", "p2")
        s2 = peek("s2", as_str=True)
        out, err = capsys.readouterr()
        assert "line0" not in out and "p0" not in out and "no0" not in out
        assert "line1" not in out and "p1" not in out and "no1" not in out
        assert "line2" in out and "p2" in out and "no2" in out
        assert line0 == "line0"
        assert line1 == "line1"
        assert line2 == "line2"
        assert noline0 is None
        assert noline1 is None
        assert noline2 is None
        assert pair0 == ("p0", "p0")
        assert pair1 == ("p1", "p1")
        assert pair2 == ("p2", "p2")
        assert s0 == ""
        assert s1 == ""
        assert s2 == "'s2'\n"


def test_wrap_indent():
    s = 4 * ["*******************"]
    with peek.preserve():
        peek.prefix = "peek| "
        peek.line_length = 80
        res = peek(s, compact=True, as_str=True)
        assert res.splitlines()[1].startswith("    s")
        res = peek(s, compact=True, as_str=True, wrap_indent="....")
        assert res.splitlines()[1].startswith("....s")
        res = peek(s, compact=True, as_str=True, wrap_indent=2)
        assert res.splitlines()[1].startswith("  s")


def test_traceback(capsys):
    with peek.preserve():
        peek.show_traceback = True
        peek()
        out, err = capsys.readouterr()
        assert out.count("traceback") == 2

        @peek()
        def p():
            pass

        p()
        out, err = capsys.readouterr()
        assert out.count("traceback") == 2
        with peek():
            pass
        out, err = capsys.readouterr()
        assert out.count("traceback") == 2


def test_check_output(capsys, tmpdir):
    """special Pythonista code, as that does not reload x1 and x2"""
    if "x1" in sys.modules:
        del sys.modules["x1"]
    if "x2" in sys.modules:
        del sys.modules["x2"]
    del sys.modules["peek"]
    import peek

    """ end of special Pythonista code """
    with peek.preserve():
        x1_file = tmpdir / "x1.py"
        with open(str(x1_file), "w") as f:
            print(
                """\
def check_output():
    import x2

    peek.configure(show_line_number=True, show_exit= False,output="stdout_nocolor")
    x2.test()
    peek(1)
    peek(
    1
    )
    with peek(prefix="==>"):
        peek()

    with peek(



        prefix="==>"

        ):
        peek()

    @peek()
    def x(a, b=1):
        pass
    x(2)

    @peek()




    def x(


    ):
        pass

    x()
""",
                file=f,
            )

        x2_file = tmpdir / "x2.py"
        with open(str(x2_file), "w") as f:
            print(
                """\

def test():
    @peek()
    def myself(x):
        peek(x)
        return x

    myself(6)
    with peek():
        pass
""",
                file=f,
            )
        sys.path = [str(tmpdir)] + sys.path
        import x1

        x1.check_output()
        sys.path.pop(0)
    out, err = capsys.readouterr()
    assert (
        out
        == """\
#4[x2.py] in test() ==> called myself(6)
#5[x2.py] in test.myself() ==> x=6
#9[x2.py] in test() ==> enter
#6[x1.py] in check_output() ==> 1
#7[x1.py] in check_output() ==> 1
==>#10[x1.py] in check_output() ==> enter
#11[x1.py] in check_output()
==>#13[x1.py] in check_output() ==> enter
#20[x1.py] in check_output()
#23[x1.py] in check_output() ==> called x(2)
#32[x1.py] in check_output() ==> called x()
"""
    )


def test_prefix_variants(capsys):
    n = 1
    peek.prefix = lambda: f"{n:<2d}"
    peek(10 * 10)
    n = 2
    peek(10 * 10)
    peek.prefix = 1
    peek(10 * 10)
    out, err = capsys.readouterr()
    assert (
        out
        == """\
1 10 * 10=100
2 10 * 10=100
110 * 10=100
"""
    )
    peek.prefix = ""


def test_propagation():
    with peek.preserve():
        y0 = peek.fork()
        y1 = y0.fork()
        peek.prefix = "x"
        y2 = peek.clone()

        assert peek.prefix == "x"
        assert y0.prefix == "x"
        assert y1.prefix == "x"
        assert y2.prefix == "x"

        y1.prefix = "xx"
        assert peek.prefix == "x"
        assert y0.prefix == "x"
        assert y1.prefix == "xx"
        assert y2.prefix == "x"

        y1.prefix = None
        assert peek.prefix == "x"
        assert y0.prefix == "x"
        assert y1.prefix == "x"
        assert y2.prefix == "x"

        peek.prefix = None
        assert peek.prefix == ""
        assert y0.prefix == ""
        assert y1.prefix == ""
        assert y2.prefix == "x"


def test_delta_propagation():
    with peek.preserve():
        y_delta_start = peek.delta
        y0 = peek.fork()
        y1 = y0.fork()
        peek.delta = 100
        y2 = peek.clone()

        assert 100 < peek.delta < 110
        assert 100 < y0.delta < 110
        assert 100 < y1.delta < 110
        assert 100 < y2.delta < 110

        y1.delta = 200
        assert 100 < peek.delta < 110
        assert 100 < y0.delta < 110
        assert 200 < y1.delta < 210
        assert 100 < y2.delta < 110

        y1.delta = None
        assert 100 < peek.delta < 110
        assert 100 < y0.delta < 110
        assert 100 < y1.delta < 110
        assert 100 < y2.delta < 110

        peek.delta = None
        assert 0 < peek.delta < y_delta_start + 10
        assert 0 < y0.delta < y_delta_start + 10
        assert 0 < y1.delta < y_delta_start + 10
        assert 100 < y2.delta < 110


def test_end(capsys):
    a = 12
    b = 4 * ["test"]
    c = 1
    peek(a, end=" ")
    peek(b, end=" ")
    peek(c)
    out, err = capsys.readouterr()
    assert (
        out
        == """\
a=12 b=['test', 'test', 'test', 'test'] c=1
"""
    )


def test_separator(capsys):
    a = 12
    b = 4 * ["test"]
    peek(a, b)
    peek(a, b, sep="")
    peek(a, separator="")
    out, err = capsys.readouterr()
    assert (
        out
        == """\
a=12, b=['test', 'test', 'test', 'test']
a=12
b=['test', 'test', 'test', 'test']
a=12
"""
    )


def test_equals_separator(capsys):
    a = 12
    b = 4 * ["test"]
    peek(a, b)
    peek(a, b, equals_separator=" ==> ")
    peek(a, b, equals_separator=" = ")

    out, err = capsys.readouterr()
    assert (
        out
        == """\
a=12, b=['test', 'test', 'test', 'test']
a ==> 12, b ==> ['test', 'test', 'test', 'test']
a = 12, b = ['test', 'test', 'test', 'test']
"""
    )


def test_context_separator(capsys):
    a = 12
    b = 2 * ["test"]
    peek(a, b, show_line_number=True)
    peek(a, b, sln=1, context_separator=" ... ")

    out, err = capsys.readouterr()
    lines = out.split("\n")
    assert lines[0].endswith(" ==> a=12, b=['test', 'test']")
    assert lines[1].endswith(" ... a=12, b=['test', 'test']")


def test_wrap_indent1(capsys):
    with peek.preserve():
        peek.separator = ""
        peek(1, 2)
        peek(1, 2, prefix="p| ")
        peek(1, 2, prefix="my")
        peek.wrap_indent = "...."
        peek(1, 2, prefix="p| ")
        peek(1, 2, prefix="my")
    out, err = capsys.readouterr()
    assert (
        out
        == """\
1
2
p|  1
    2
my  1
    2
p|  1
....2
my  1
....2
"""
    )


def test_fstrings(capsys):
    hello = "world"

    with peek.preserve():
        peek("hello, world")
        peek(hello)
        peek(f"hello={hello}")

    with peek.preserve():
        peek.values_only = True
        peek("hello, world")
        peek(hello)
        peek(f"hello={hello}")

    with peek.preserve():
        peek.values_only_for_fstrings = True
        peek("hello, world")
        peek(hello)
        peek(f"hello={hello}")

    with peek.preserve():
        peek.voff = True
        peek.vo = True
        peek("hello, world")
        peek(hello)
        peek(f"hello={hello}")

    out, err = capsys.readouterr()
    assert (
        out
        == """\
'hello, world'
hello='world'
f"hello={hello}"='hello=world'
'hello, world'
'world'
'hello=world'
'hello, world'
hello='world'
'hello=world'
'hello, world'
'world'
'hello=world'
"""
    )


if __name__ == "__main__":
    pytest.main(["-vv", "-s", "-x", __file__])
