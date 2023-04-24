import os
import ast
import pygraphviz as pgv


def analyze_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        file_contents = file.read()
    try:
        tree = ast.parse(file_contents)
        return tree
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None


def analyze_directory(directory_path):
    functions = {}
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                tree = analyze_file(file_path)
                if tree:
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            functions[node.name] = {
                                "file": file_path,
                                "lineno": node.lineno,
                            }
    return functions


def visualize(functions, output_file="workflow.png"):
    graph = pgv.AGraph(directed=True)

    for function_name, details in functions.items():
        graph.add_node(
            function_name,
            label=f"{function_name}\n{details['file']}:{details['lineno']}",
        )

    for function_name, details in functions.items():
        tree = analyze_file(details["file"])
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    for attr in ast.walk(node.func):
                        if isinstance(attr, ast.Name) and attr.id in functions:
                            graph.add_edge(function_name, attr.id)

    graph.layout(prog="dot")
    graph.draw(output_file)
    print(f"Workflow visualization saved to {output_file}")


if __name__ == "__main__":
    directory_path = "src/"
    functions = analyze_directory(directory_path)
    visualize(functions)
