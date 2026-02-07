
# ==========================================
# SMART PROJECT INSPECTOR
# Advanced Error Scanner
# ==========================================

# This tool will:
# 1. Ask project folder
# 2. Scan only that folder
# 3. Count Python files
# 4. Count total lines
# 5. Detect syntax errors
# 6. Detect undefined names (typos like lprint)
# 7. Show file + line info


import os
import py_compile
import ast


# ==========================================
# GET PROJECT PATH
# ==========================================

def get_project_path():
    """
    Ask user for project path
    and fix common Windows mistakes
    """

    path = input("📂 Enter project folder path: ").strip()

    # Remove quotes if pasted
    if path.startswith('"') and path.endswith('"'):
        path = path[1:-1]

    # Convert backslashes
    path = path.replace("\\", "/")

    if not os.path.exists(path):
        print("\n❌ Path does not exist!")
        exit()

    return path


# ==========================================
# FIND PY FILES
# ==========================================

def get_python_files(folder):
    """
    Recursively find .py files
    """

    py_files = []

    for root, dirs, files in os.walk(folder):

        for file in files:

            if file.endswith(".py"):

                full = os.path.join(root, file)
                py_files.append(full)

    return py_files


# ==========================================
# COUNT LINES
# ==========================================

def count_lines(file_path):
    """
    Count number of lines in file
    """

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return len(f.readlines())

    except:
        return 0


# ==========================================
# CHECK SYNTAX
# ==========================================

def check_syntax(file_path):
    """
    Compile file to find syntax errors
    """

    try:
        py_compile.compile(file_path, doraise=True)
        return None

    except py_compile.PyCompileError as e:

        err = e.exc_value

        return {
            "file": file_path,
            "line": err.lineno,
            "message": err.msg
        }


# ==========================================
# FIND UNDEFINED NAMES
# ==========================================

def find_undefined_names(file_path):
    """
    Find variables/functions used but not defined
    Example: lprint, datta, pritn
    """

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    try:
        tree = ast.parse(code)
    except:
        return []


    defined = set()
    used = set()


    class Analyzer(ast.NodeVisitor):

        def visit_FunctionDef(self, node):
            defined.add(node.name)
            self.generic_visit(node)

        def visit_Assign(self, node):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    defined.add(t.id)
            self.generic_visit(node)

        def visit_Import(self, node):
            for n in node.names:
                defined.add(n.name.split(".")[0])

        def visit_ImportFrom(self, node):
            for n in node.names:
                defined.add(n.name)

        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Load):
                used.add(node.id)


    Analyzer().visit(tree)


    undefined = []

    for name in used:

        # Ignore Python built-ins
        if name not in defined and name not in dir(__builtins__):

            # Ignore common keywords
            if not name.startswith("__"):
                undefined.append(name)

    return undefined


# ==========================================
# ANALYZE SINGLE FILE
# ==========================================

def analyze_file(file_path):

    results = []

    # Check syntax
    syntax = check_syntax(file_path)

    if syntax:
        results.append(syntax)
        return results


    # Check undefined names
    undefined = find_undefined_names(file_path)

    if undefined:

        results.append({
            "file": file_path,
            "line": "?",
            "message": f"Undefined names: {undefined}"
        })

    return results


# ==========================================
# MAIN FUNCTION
# ==========================================

def main():

    print("\n===== 🔍 SMART PROJECT INSPECTOR =====\n")

    # Step 1: Ask path
    project_path = get_project_path()

    print("\n📖 Scanning:", project_path, "\n")


    # Step 2: Find files
    files = get_python_files(project_path)

    if not files:
        print("❌ No Python files found.")
        return


    # Step 3: Count files + lines
    total_files = len(files)
    total_lines = 0


    for file in files:
        total_lines += count_lines(file)


    # Step 4: Analyze files
    errors = []


    for file in files:

        problems = analyze_file(file)

        for p in problems:
            errors.append(p)


    # Step 5: Show summary
    print("📂 Python Files :", total_files)
    print("📄 Total Lines  :", total_lines)
    print("🚨 Issues Found :", len(errors))
    print()


    # Step 6: Show details
    if errors:

        print("===== ❌ ISSUE DETAILS =====\n")

        for i, err in enumerate(errors, 1):

            print(f"Issue {i}")
            print("File   :", err["file"])
            print("Line   :", err["line"])
            print("Reason :", err["message"])
            print("----------------------------")

    else:

        print("✅ No syntax or name errors. Project is clean!")


    print("\n===== ✔ Scan Complete =====\n")


# ==========================================
# START PROGRAM
# ==========================================

if __name__ == "__main__":
    main()
