import os
import sys
import subprocess as sp
import difflib as diff
from exrex import generate, count
import re
from tests import *
import shutil
import tempfile
import timeit
import statistics as st
from defaults import *

dir_path = os.path.dirname(os.path.realpath(__file__))

t_count = 0
if auto_tester_enabled:
	t_count = count(AUTO_TESTER)

DIR = "* = expected   - = actual\n"
DECODING = "ascii"


def run_tests(tests, source, reference, force_strict, leng=None):
	total_errors = []
	total_tested = 0
	for key, test_pool in tests.items():
		print("running", key, "tests..")
		errors = test_pool.run_tests(source, reference, force_strict, key, leng)
		l = len(errors)
		total_tested += len(test_pool)
		if l > 0:
			total_errors += errors
			if reinput(str(l) + " Errors detected, continue? (y/n) ", ('y', 'n')) == 'n':
				break
	return total_errors, total_tested


def count_errors(failed, total, label=""):
	if total == 0:
		return
	passed = total - failed
	score = passed / total
	if failed == 0:
		c_print("Passed all " + str(total) + " " + label + " tests!", 'G')
	else:
		print(c_str(str(failed) + " failed tests", 'R') +
			  " out of " + str(total) +
			  " (" + c_str(str(round(score * 100)) + "%", 'Y') + ")")


def c_str(str, c):
	# adds some color to the text!
	colors = {
		'Y': "\033[93m{}\033[00m",
		'B': "\033[96m{}\033[00m",
		'G': "\033[92m{}\033[00m",
		'R': "\033[91m{}\033[00m",
		'M': "\033[35m{}\033[00m"
	}
	if c not in colors.keys():
		return str
	return colors[c].format(str)


def c_print(str, color):
	# print colored text
	print(c_str(str, color))


def common_filter(str):
	# replace common strings with reader friendly text
	if str == "":
		return "[EMPTY]"
	if str == "\n":
		return "[NEW_LINE]"
	return str


class Test_pool:
	def __init__(self, strict=True, tests=None, overflow_abort=0):
		self.strict = strict
		self.overflow_abort = overflow_abort
		if tests == None:
			self.tests = []
		else:
			self.tests = tests

	def run_tests(self, source, reference, force_strict=False, label="", leng=None):
		if isinstance(self.tests, list):
			leng = len(self.tests)
		strict = True
		if not force_strict:
			strict = self.strict
		err_list = []
		for i, test in enumerate(self.tests):
			if isinstance(test, str):
				s = test.split(PLACEHOLDER)
				if len(s) > 2:
					raise ValueError(test + " -- " + str(len(s)))
				test = Test(args=s[0], input=s[1])
			result = test.run_test(source, reference, strict)
			if isinstance(result, Error):
				result.idd = i
				result.pool_name = label
				err_list.append(result)

			if leng is not None and (i + 1) % PROGRESS_REPORT == 0:
				print("Calculated", i + 1, "(" + str(round((i + 1) * 100.0 / leng, 2)) + "%) tests with", len(err_list), "fails.")

			if 0 < self.overflow_abort <= len(err_list):
				print("There are too many failed tests, aborting...")
				break

		return err_list

	def __len__(self):
		if isinstance(self.tests, list):
			return len(self.tests)
		else:
			return t_count


class Error:
	def __init__(self, test, type, desc, idd=0, pool_name="Unknown"):
		self.test = test
		self.type = type
		self.desc = desc
		self.idd = idd
		self.pool_name = pool_name

	def __str__(self):
		return c_str("──── " + self.pool_name.upper() + " ERROR " + str(self.idd) + " ────", 'R') + \
			   "\nErrType: " + self.type + "\n" + str(self.test) + "\nDescription:\n" + self.desc


class Test:
	def __init__(self, args="", input="", brief=None, expected_out=None, expected_err=None, expected_return=None):
		self.brief = brief
		self.args = args
		self.input = input
		self.expected_out = expected_out
		self.expected_err = expected_err
		self.expected_return = expected_return

	def __str__(self):
		out = ""
		if self.brief is not None:
			out += "brief: " + self.brief + "\n"
		out += "args:  " + self.args + "\ninput: " + self.input

		return out

	def run_test(self, src, reference, strict=True):
		if not strict and (self.expected_out is None or self.expected_err is None or self.expected_return is None):
			raise ValueError("test doesn't run strictly, but no expected out and err given\n" + str(self) + "\n" + str(self.expected_out)
							 + "\n" + str(self.expected_err) + "\n" + str(self.expected_return))


		with tempfile.NamedTemporaryFile(mode='w+t') as tempInput:
			tempInput.writelines(str(self.input))
			tempInput.seek(0)
			arg = tempInput.name + self.args
			if self.args == "n":
				arg = ""
			if self.args == "r":
				arg = "fef24r2fna"
			self.args = arg
			actual = sp.run(args=src + " " + self.args, capture_output=True, shell=True)
			if not os.path.isfile(relative("railway_planner_output.txt")):
				return Error(self, "no file error", "program didn't create 'railway_planner_output.txt'")
			with open("railway_planner_output.txt", 'r', encoding=DECODING) as output:
				actual_output = output.read()

				strict_expected = sp.run(args=reference + " " + self.args, capture_output=True, shell=True)

				strict_diff_file = "\n".join(
					diff.context_diff(strict_expected.stdout.decode(DECODING).splitlines(), actual_output.splitlines(), lineterm=""))
				strict_diff_out = "\n".join(
					diff.context_diff("", actual.stdout.decode(DECODING).splitlines(), lineterm=""))
				strict_diff_err = "\n".join(
					diff.context_diff(strict_expected.stderr.decode(DECODING).splitlines(), actual.stderr.decode(DECODING).splitlines(), lineterm=""))

				# return Error(self, "test error", str(strict_expected) + "\nOUT:\n" + strict_diff_out + "\nERR:\n" + strict_diff_err)

				if strict_diff_file != "":
					if strict:
						return Error(self, "output error", DIR + "\n".join(strict_diff_file.split("\n")[3:]))
					elif not bool(re.match(self.expected_out, actual.stdout, re.M)):
						return Error(self, "output error", "expected:\n" + self.expected_out + "\nactual:\n" + actual.stdout)
				if strict_diff_out != "":
					if strict:
						return Error(self, "stdout error", DIR + "\n".join(strict_diff_out.split("\n")[3:]))
					elif not bool(re.match(self.expected_out, actual.stdout, re.M)):
						return Error(self, "stdout error", "expected:\n" + self.expected_out + "\nactual:\n" + actual.stdout)
				if strict_diff_err != "":
					if strict:
						return Error(self, "stderr error", DIR + "\n".join(strict_diff_err.split("\n")[3:]))
					elif not bool(re.match(self.expected_err, actual.stderr, re.M)):
						return Error(self, "stderr error", "expected:\n" + self.expected_err + "\nactual:\n" + actual.stderr)
				if actual.returncode != strict_expected.returncode:
					if strict:
						return Error(self, "return code error", "expected: " + str(strict_expected.returncode) + "\nactual: " + str(actual.returncode))
					elif self.expected_return != actual.returncode:
						return Error(self, "return code error", "expected:\n" + str(self.expected_return) + "\nactual:\n" + str(actual.returncode))

def wrapper(func, *args, **kwargs):
	def wrapped():
		return func(*args, **kwargs)
	return wrapped

def runTimer(src, reference, pattern, prefix="", suffix="", n=100, time_limit=60):

	time_table = []
	expected_time = 0
	actual_time = 0
	while expected_time < time_limit and actual_time < time_limit:
		test = prefix + pattern * n + suffix
		with tempfile.NamedTemporaryFile(mode='w+t') as tempInput:
			tempInput.writelines(str(test))
			tempInput.seek(0)
			ex = wrapper(sp.run, args=reference + " " + tempInput.name, capture_output=True, shell=True)
			ac = wrapper(sp.run, args=src + " " + tempInput.name, capture_output=True, shell=True)
			expected_time = timeit.timeit(ex, setup="import subprocess as sp", number=15)
			actual_time = timeit.timeit(ac, setup="import subprocess as sp", number=15)
			ratio = expected_time/actual_time
			'{:<30}'.format('left aligned')
			print('{:<15}'.format("n = " + str(n)) +
				  '{:<24}'.format("expected(n) = " + str(round(expected_time, 4))) +
				  '{:<24}'.format("actual(n) = " + str(round(actual_time, 4))) +
				  '{:<22}'.format("(" + str(round(100*ratio)) + "% efficiency)"))
			time_table.append(ratio)
		n *= 2

	mean = round(100 * st.mean(time_table))
	ch = 'G'
	if mean < 50:
		ch = 'R'
	elif mean < 100:
		ch = 'Y'
	c_print("Average efficiency is " + str(mean) + "%", ch)
	med = round(100 * st.median(time_table))
	ch = 'G'
	if med < 50:
		ch = 'R'
	elif med < 100:
		ch = 'Y'
	c_print("Median efficiency is " + str(med) + "%", ch)


def reinput(q, answers):
	while True:
		a = input(q)
		if a in answers:
			return a


def relative(f):
	return dir_path + "/" + f


if __name__ == "__main__":
	source = DEFAULT_SOURCE
	if len(sys.argv) >= 2:
		source = sys.argv[1]
	if os.path.isfile(relative(source)):
		if source.endswith(TO_COMPILE):
			c_print("Running pre-submit tests", 'B')
			if relative(source) != relative(UNCOMPILED_NAME):
				shutil.copy2(relative(source), relative(UNCOMPILED_NAME))
			sp.call("tar -cvf " + TAR_NAME + " " + UNCOMPILED_NAME, shell=True)
			sp.call(pre_submit + " " + TAR_NAME, shell=True)
			c_print("Running coding style test", 'B')
			sp.call(coding_style + " " + source, shell=True)
			c_print("Compiling " + source + " as " + COMPILED_NAME, 'B')
			sp.call("gcc -Wall -Wvla -Wextra -std=c99 -lm " + source + " -o " + COMPILED_NAME, shell=True)
			c_print("Running memory leak test", 'B')
			sp.call("valgrind --leak-check=full " + COMPILED_NAME, shell=True)

		c_print("\n════════ Done with official tests! now running student tests ════════\n", 'M')

		errors, total = run_tests(TESTS, COMPILED_NAME, REFERENCE, FORCE_STRICT)

		count_errors(len(errors), total, "manual")
		for error in errors:
			print(error)

		if auto_tester_enabled and errors == []:
			c_print("autotester is calculating " + str(t_count) + " tests, please be patient!", 'B')
			auto_pool = Test_pool(strict=True, tests=generate(AUTO_TESTER))
			a_errors, a_total = run_tests({"automatic": auto_pool}, COMPILED_NAME, REFERENCE, True, t_count)
			count_errors(len(a_errors), a_total, "automatic")
			for error in a_errors:
				print(error)

		c_print("\n════════ Done with tests! now running time complexity analysis ════════\n", 'M')
		runTimer(COMPILED_NAME, REFERENCE, PATTERN, PREFIX, SUFFIX)

	else:
		c_print("Source file doesn't exist", 'R')
