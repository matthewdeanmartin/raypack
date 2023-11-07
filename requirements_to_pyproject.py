from tomlkit import document, table, string


def read_requirements_txt(file_path):
    with open(file_path) as requirements_file:
        return requirements_file.read().strip().split("\n")


def write_pyproject_toml(file_path, pyproject):
    with open(file_path, "w") as pyproject_file:
        pyproject_file.write(pyproject.as_string())


def parse_requirement(requirement):
    parts = requirement.strip().split("==")
    if len(parts) == 1:
        name, version = parts[0], ""
    elif len(parts) == 2:  # noqa
        name, version = parts
    else:
        raise ValueError(f"Invalid requirement format: {requirement}")
    return name, version


def convert_requirements_to_pyproject(requirements_txt_path, pyproject_toml_path):
    requirements = read_requirements_txt(requirements_txt_path)

    # Create a pyproject.toml document
    pyproject_doc = document()

    # Create a [tool] section
    tool_table = table()
    pyproject_doc["tool"] = tool_table

    # Create a [tool.poetry] section within [tool]
    poetry_table = table()
    tool_table["poetry"] = poetry_table

    # Fill in the [tool.poetry.dependencies] section
    dependencies_table = table()
    for requirement in requirements:
        name, version = parse_requirement(requirement)
        dependencies_table[name] = "==" + string(version)
        # dep_table['optional'] = False
        # dependencies_table[name] = dep_table
    poetry_table["dependencies"] = dependencies_table

    # Write the pyproject.toml file
    write_pyproject_toml(pyproject_toml_path, pyproject_doc)

    print("pyproject.toml created successfully.")


if __name__ == "__main__":
    requirements_txt_path = "requirements_in_glue_2023_11_7.txt"
    pyproject_toml_path = "pyproject_template.toml"
    convert_requirements_to_pyproject(requirements_txt_path, pyproject_toml_path)
