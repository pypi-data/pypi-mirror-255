### This repo is just an experiment to test out poetry

Key things:
easyily turn program.py to `poetryexp` runnable program that can be installed with `pip install poetry-experiment`
or other available pypi package name

In a new project folder (package-root):
1. run `git init` or `git clone` beforehand
2. create README.md if missing
3. propper py package
    - put program.py in package folder poetry-experiment/
    - create __init__.py (import program) inside, in poetry-experiment/
4. poetry init
5. add script to toml
6. poetry build
7. poetry config pypi-token.pypi your-api-token
8. poetry publish


```
package-root/
	README.md
	poetry.toml (fix name)
	poetry-experiment/
		__init__.py #import program inside
		program.py 
	.git/
```


To accomplish this, you can follow these steps:

1. **Create a `pyproject.toml` file**: Make sure you have a `pyproject.toml` file in your project directory. Poetry uses this file to manage project dependencies and settings.

2. **Add metadata to `pyproject.toml`**: You'll need to define metadata such as the project name, version, and description in the `pyproject.toml` file.

3. **Define entry points**: In your `pyproject.toml`, you can define entry points for your command-line interface (CLI) using the `[tool.poetry.scripts]` section. This will allow users to run your program using a specified name.

4. **Write your `program.py`**: Write the Python script that you want to publish.

5. **Build your package**: Use Poetry to build your package. This will generate a distributable package that can be uploaded to PyPI.

6. **Publish to PyPI**: Once your package is built, you can publish it to PyPI using Poetry's `publish` command.

Here's a step-by-step guide:

1. Create a `pyproject.toml` file if you don't already have one. It should look something like this:

```toml
[tool.poetry]
name = "poetry_experiment"
version = "1.0.0"
description = "A description of your program"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.8"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.scripts]
poetryexp = "program:main"
```

2. Write your `program.py`. Make sure it has a function named `main`, which will be called when users run your program.

```python
def main():
    print("Hello, world!")
```

3. Once you've written your script and configured your `pyproject.toml`, you can use Poetry to build your package:

```bash
poetry build
```

4. After the build is successful, you can publish your package to PyPI:

```bash
poetry publish --build
```

5. After publishing, users can install your package using pip:

```bash
pip install poetry_experiment
```

6. Once installed, users can run your program using the specified entry point:

```bash
poetryexp
```

This will execute the `main()` function defined in your `program.py`.
