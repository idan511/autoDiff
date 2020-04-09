# file locations
REFERENCE = "~labcc2/www/ex1/school_solution"
coding_style = "~labcc2/www/codingStyleCheck"
pre_submit = "~labcc2/www/ex1/presubmit_ex1"
DEFAULT_SOURCE = "main.c"

# auto test settings
auto_tester_enabled = True
OVERFLOW_ABORT = 100  # 0 == off
PLACEHOLDER = "§§§±±±§§§"
AUTO_TESTER = ("best|merge|quick", "((([01]|111|11|1a)11111111,abcd AB-CD[4$]{0,1},(100|0|47|200|\-1),(100|0|47|200|\-1)(,abc\-\-AGC[ 4$]{0,1}D){1,2}\n){0,1}|(1111111111,bb,(100|0|47),(100|47),count,city\n){0,1}(1111111111,ac,(100|0|47),(100|47),count,city\n){0,1}(1111111111,(ba|dd),(100|0|47),(100|47),count,city\n){0,1}(1111111111,ab,(100|0|47),(100|47),count,city\n){0,1})q\n")

# compiler settings
TO_COMPILE = ('.c')
COMPILED_NAME = "compiled_test"
UNCOMPILED_NAME = "manageStudents.c"
TAR_NAME = "ex1.tar"

# Misc
FORCE_STRICT = False
PROGRESS_REPORT = 1000