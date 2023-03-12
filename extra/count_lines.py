import os

paths = list(os.walk("../"))

lines_count = 0
py_files_count = 0
for path in paths:
    start = path[0]
    files = path[2]
    if not start.count("venv"):
        for file in files:
            if file.endswith(".py"):
                py_files_count += 1

                with open(os.path.join(start, file), "r") as f:
                    lines_count += len(f.readlines())

print(lines_count)
print(py_files_count)
