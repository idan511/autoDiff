# autoDiff
Automatically test many inputs to any 2 programs and compare them!

## How to install
Simply add this repository to your workspace and after running for the first time 'config.py' will be created where all options can be customized.

## How to run
Type into terminal `python3 autoDiff.py yourfile.c`

## FAQ
- **my program failed a test but I'm sure it's working!**<br>Some tests are set to strict, meaning they have one very specific output. If you think a test failed wrongly you can either fork with a fix or let me know & I'll fix it

### config.py
```
# file locations
REFERENCE - where reference app is locates (school colution)
coding_style - where coding app file is located
pre_submit - where presubmit app is located
DEFAULT_SOURCE - when no argument is given, run with this file

# auto test settings
auto_tester_enabled - will run autotests if all manual tests pass
OVERFLOW_ABORT - will abort testing after n failed tests (0=off)
PLACEHOLDER - a seperator string for regex
AUTO_TESTER - a regex pattern for possible inputs

# compiler settings
TO_COMPILE - list of compilable file types
COMPILED_NAME - name for temporary compiled app
UNCOMPILED_NAME - name for presubmission
TAR_NAME - tar name for presubmission

# Misc
FORCE_STRICT - will only evaluate tests strictly
PROGRESS_REPORT - will give a progress report every n tests
```
#### Known issues
- 
