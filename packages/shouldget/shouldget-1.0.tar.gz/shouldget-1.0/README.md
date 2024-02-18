
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![pipeline status](https://gitlab.bioinfo-diag.fr/vidjil/should/badges/dev/pipeline.svg)](https://gitlab.bioinfo-diag.fr/vidjil/should/commits/dev)
[![coverage report](https://gitlab.bioinfo-diag.fr/vidjil/should/badges/dev/coverage.svg)](https://gitlab.bioinfo-diag.fr/vidjil/should/commits/dev)

### `should` -- Test command-line applications through `.should` files


`should` is a single-file program to test command-line applications on Unix-like systems.
It checks the standard output, or possibly another file, and parses for exact or regular expressions,
possibly while counting them and checking their number of occurrences.
It also parses and tests JSON data.
`should` outputs reports in [`.tap` format](https://testanything.org/tap-specification.html)
and in JUnit-like XML.

`should` is written in Python with no external dependencies except from Python >= 3.4
and is intended to work on any command-line application
-- should your application outputs something, you can test it!


### Download

The archive [should-3.0.0.tar.gz](https://gitlab.bioinfo-diag.fr/vidjil/should/-/archive/3.0.0/should-3.0.0.tar.gz)
also includes this documentation with demo files.
In your projetcts, you only need the [should.py](https://gitlab.bioinfo-diag.fr/vidjil/should/raw/master/src/should.py) file.


### Basic usage


The [demo/hello.should](demo/hello.should) example covers the basic functionality :

```shell
# A .should file launches any command it encounters.
# Every line starting with a `#` is a comment.

echo "hello, world"

# Lines containing a `:` are test lines.
# The `test expression` is what is found at the right of the `:`.
# It should be found in the stdout, at least one time.

:world
:lo, wo


# What is at the left of the `:` are modifiers.
# One can specify the exact number of times the test expression has to appear.

1:hello
0:Bye-bye


# Lines beginning by `$` give a name to the following tests

$ Check space before world
1:, wo

$ Check misspellings
0:wrld
0:helo


# The `r` modifier triggers Python regular expressions

$ Two o´s
r: o.*o

$ A more flexible test
r: [Hh]ello,\s+world
```


The test is then run by calling `should` on the `.should` file:

```shell
> ./should demo/hello.should
$LAUNCHER=

demo/hello.should
**echo "hello, world"**
  stdout --> 1 lines
  stderr --> 0 lines

ok
ok
ok
ok
ok - Check space before world
ok - Check misspellings
ok - Check misspellings
ok - Two o´s
ok - A more flexible test
ok - Exit code is 0
==> ok - ok:10 total:10 tests

demo/hello.should
==> ok - ok:10 total:10 tests
```


`should` can be run on several `.should` files at once. In this case, it furthers shows statistics
on all tests. Here 39 out of 40 tests passed from 8 `.should` files.

```shell
> ./should demo/*.should
(...)

Summary ==> ok - ok:8 total:8 files
Summary ==> ok - ok:39 TODO:1 total:40 tests

```


### Documentation

The documentation is completed by the files in [demo/](demo/).

The [demo/cal.should](demo/cal.should) example shows
matching on several lines (`l`), counting inside lines (`w`),
ignoring whitespace differences (`b`), expecting a test to fail (`f`)
or allowing a test to fail (`a`),
requiring less than or more than a given number of expressions (`<`/`>`).

[demo/commands.should](demo/commands.should) shows that several commands can be used into a same `.should` file. Tests are flushed after each set of commands.

[demo/exit-codes.should](demo/exit-codes.should) shows how to require a particular exit code with `!EXIT_CODE`.

[demo/unicode.should](demo/unicode.should) shows that unicode characters can be put
in test comment and strings, provided that a UTF-8 locale has been set up.

[demo/variables.should](demo/variables.should) shows how to define and use variables.

[demo/launcher.should](demo/launcher.should) shows how to define a "launcher" that is appended before every command,
for example to launch tools like `valgrind` on a test set.
[demo/extra.should](demo/extra.should) show how to add an argument to every tested command.

[demo/json.should](demo/json.should) shows how to test JSON data (keys and values).git

**Options and modifiers**

```shell
usage: should [--cd PATH] [--cd-same] [--launcher CMD] [--extra ARG]
              [--mod MODIFIERS] [--var NAME=value] [--timeout TIMEOUT]
              [--shuffle] [--no-a] [--no-f] [--only-a] [--only-f]
              [--retry] [--retry-warned]
              [--log] [--tap] [--xml]
              [-v] [-q] [--fail-a]
              [-h] [--version]
              should-file [should-file ...]

Test command-line applications through .should files

positional arguments:
  should-file        input files (.should)

running tests (can also be set per test in !OPTIONS):
  --cd PATH          directory from which to run the test commands
  --cd-same          run the test commands from the same directory as the .should files
  --launcher CMD     launcher preceding each command (or replacing $LAUNCHER)
  --extra ARG        extra argument after the first word of each command (or replacing $EXTRA)
  --mod MODIFIERS    global modifiers (uppercase letters cancel previous modifiers)
                       f/F consider that the test should fail
                       a/A consider that the test is allowed to fail
                       r/R consider as a regular expression
                       w/W count all occurrences, even on a same line
                       i/I ignore case changes
                       b/B ignore whitespace differences as soon as there is at least one space. Implies 'r'
                       l/L search on all the output rather than on every line
                       z/Z keep leading and trailing spaces
                       j/J interpret json data. Implies 'lw'
                       >   requires that the expression occurs strictly more than the given number
                       <   requires that the expression occurs strictly less than the given number
  --var NAME=value   variable definition (then use $NAME in .should files)
  --timeout TIMEOUT  Delay (in seconds) after which the task is stopped (default: 120)

selecting tests to be run:
  --shuffle          shuffle the tests
  --no-a             do not launch 'a' tests
  --no-f             do not launch 'f' tests
  --only-a           launches only 'a' tests
  --only-f           launches only 'f' tests
  --retry            launches only the last failed tests
  --retry-warned     launches only the last failed or warned tests

controlling output:
  --log              stores the output into .log files
  --tap              outputs .tap files
  --xml              outputs JUnit-like XML into should.xml
  -v, --verbose      increase verbosity
  -q, --quiet        verbosity to zero
  --fail-a           fail on passing 'a' tests
  -h, --help         show this help message and exit
  --version          show program version number and exit
```

**Output.**
By default, `should` only writes to the standard output.
The `--log`, `--tap` and `--xml` options enable to store the actual output of the tested commands
as well as [`.tap` files](https://testanything.org/tap-specification.html)
and a JUnit `should.xml` file.

**Exit code.**
`should.py` returns `0` when all the tests passed (or have been skipped, or marked as `failed-with-ALLOW` with `a`).
As soon as one regular test fails, or as soon as a test marked with `TODO` pass,
`should.py` returns `1`.


### Alternatives

* Aruba: Testing with Cucumber, RSpec, Minitest -- https://github.com/cucumber/aruba
* Cram: It's test time -- https://bitheap.org/cram/
* Bats: Bash Automated Testing System -- https://github.com/sstephenson/bats
* Expect -- http://core.tcl.tk/expect
* Tush: Literate testing for command-line programs -- https://github.com/darius/tush

See also https://stackoverflow.com/questions/353198/best-way-to-test-command-line-tools.


### History

`should` is a refactor of an earlier shell script that was developed and heavily used since 2013
to test two bioinformatics programs,
[CRAC](http://crac.gforge.inria.fr/) (mapping of RNA sequences, discovery of transcriptomic and genomic variants),
[Vidjil-algo](http://www.vidjil.org/) (clustering and analysis of lymphocyte clusters from their DNA sequences,
contains [700+ `should` tests](https://gitlab.inria.fr/vidjil/vidjil/tree/dev/algo/tests/should-get-tests) in about 100 files).
