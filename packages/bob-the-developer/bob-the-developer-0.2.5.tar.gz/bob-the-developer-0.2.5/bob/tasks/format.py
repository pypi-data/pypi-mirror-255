"""Module focussing on the `format` command.

Contains the task and helpers to format the codebase given a specific formatter.


# import pathlib
#
#
# def bob_format(options, cwd):
# 	folders = ['src', 'include']
# 	filetypes = ['*.c', '*.h', '*.cpp', '*.hpp']
#
# 	files = []
# 	for f in folders:
# 		base = cwd / f
# 		for type in filetypes:
# 			files += base.rglob(type)
#
# 	steps = []
# 	for file in files:
# 		steps.append(container_command(BuildTarget.Linux, cwd) + [
# 			"clang-format",
# 			"-style=file",
# 			"-i",
# 			"-fallback-style=none",
# 			str(pathlib.PurePosixPath(file.relative_to(cwd)))
# 		])
# 	return steps

"""
