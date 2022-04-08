import logging
import re
from pathlib import Path
import shutil
import sys

from utils.TerminalColors import TC
from utils.TraceToLine import TraceToLine, open_utf8

FILE_SHOW_LINES = 50
REPO_URL = "https://raw.githubusercontent.com/xicodomingues/francinette/master/"

logger = logging.getLogger("utils")


def show_banner(project):
	columns = shutil.get_terminal_size((80, 23)).columns
	#print(columns)
	message = f"{TC.BLUE}Welcome to {TC.B_PURPLE}Francinette{TC.BLUE}, a 42 tester framework!"
	submessage = f"{project}"
	project_message = f"{TC.B_YELLOW}{project}{TC.CYAN}"
	size = 30 - len(submessage)
	project_message = " " * (size - (size // 2)) + project_message + " " * (size // 2)
	print(f"{TC.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗")
	print(f"{TC.CYAN}║                {message}                {TC.CYAN}║")
	print(f"{TC.CYAN}╚═══════════════════════╦══════════════════════════════╦═══════════════════════╝")
	print(f"{TC.CYAN}                        ║{project_message}║")
	print(f"{TC.CYAN}                        ╚══════════════════════════════╝{TC.NC}")


def intersection(lst1, lst2):
	lst3 = [value for value in lst1 if value in lst2]
	return lst3


ansi_columns = re.compile(r'\x1B(?:\[[0-?]*G)')
ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def remove_ansi_colors(text):
	return ansi_escape.sub('', ansi_columns.sub(' ', text))


def open_ascii(file, mode='r'):
	return open(file, mode, encoding='ascii', errors="backslashreplace")


def decode_ascii(bytes):
	return bytes.decode('ascii', errors="backslashreplace")


def show_errors_file(temp_dir: Path, errors_color, errors_log, n_lines=FILE_SHOW_LINES):
	trace_to_line = TraceToLine(temp_dir, errors_color)
	lines = trace_to_line.parse_stack_traces()

	print(f"{TC.B_RED}Errors found{TC.NC}:")
	[print(line, end='') for line in list(filter(lambda x: x != '', lines[:n_lines * 4]))[:n_lines]]
	if len(lines) > n_lines:
		dest = (temp_dir / errors_log).resolve()
		with open_utf8(dest, "w") as log:
			log.writelines([remove_ansi_colors(line) for line in lines])
		print(f"...\n\nFile too large. To see full report open: {TC.PURPLE}{dest}{TC.NC}")
	print()


def show_errors_str(errors: str, temp_dir: Path, n_lines=FILE_SHOW_LINES):
	with open('error_color.log', 'w', encoding='utf-8') as f:
		f.write(errors)
	show_errors_file(temp_dir, "error_color.log", "errors.log", n_lines)


def is_makefile_project(current_path, project_name, project_class):
	make_path = current_path / "Makefile"
	name_matcher = re.compile(rf"^\s*NAME\s*:?=\s*{project_name}\s*$")
	logger.info(f"Makefile path: {make_path.resolve()}")
	if not make_path.exists():
		return False
	with open(make_path, "r") as mk:
		for line in mk.readlines():
			if name_matcher.match(line):
				return project_class

	return False


def is_linux():
	return sys.platform.startswith("linux")


def is_mac():
	return not is_linux()


def escape_str(string):
	temp = re.sub(r"\\(?!x)", r"\\\\", string)
	return temp.replace('"', r'\"') \
		.replace('\t', r'\t') \
		.replace('\n', r'\n') \
		.replace('\f', r'\f') \
		.replace('\v', r'\v') \
		.replace('\r', r'\r')