To create and deploy a Python package on PyPI using Poetry with CI/CD on GitHub, follow these steps:

### 1. Install Poetry

First, ensure Poetry is installed on your system. You can install Poetry by running:

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

After installation, add Poetry to your PATH if it's not already done by the installer script.

### 2. Configure Your Package

Create a new directory for your package and navigate into it. Then, initialize a new Poetry project:

```bash
mkdir mypackage
cd mypackage
poetry init
```

Follow the prompts to define your package's dependencies and metadata.

### 3. Add Your Function

Create a directory for your module inside the project folder, and add your Python file with the function:

```bash
mkdir mypackage
touch mypackage/__init__.py  # make it a package
```

Edit `mypackage/__init__.py` to add your function:

```python
def my_function():
    return "I'm the output of your function"
```

### 4. Build Your Package

You can build your package with Poetry to ensure everything is set up correctly:

```bash
poetry build
```

### 5. Set Up GitHub Repository

- Create a new repository on GitHub and push your project there.
- Ensure you have a `.gitignore` file that includes the `dist/` directory and any other unnecessary files.

### 6. Configure CI/CD with GitHub Actions

Create a GitHub Actions workflow in your repository to automate testing, building, and publishing your package to PyPI. Under your repository, navigate to the "Actions" tab and set up a new workflow, or create a `.github/workflows/publish-to-pypi.yml` file with the following content:

```yaml
name: Publish Python Package

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.x"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build
      - name: Build package
        run: python -m build
      - name: Publish package to PyPI
        uses: pypa/gh-action-pypi-publish@v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

### 7. Configure PyPI API Token

- Generate a PyPI API token from your PyPI account.
- Add the token as a secret in your GitHub repository settings (`Settings > Secrets`). Name the secret `PYPI_API_TOKEN`.

### 8. Release Your Package

- When you're ready to release your package, create a new release in your GitHub repository.
- The GitHub Actions workflow you configured will automatically build and publish your package to PyPI when you publish the release.

This setup uses GitHub Actions for CI/CD, automating the process of testing, building, and publishing your Python package to PyPI. Make sure to adjust the workflow according to your project's specific needs, such as running tests before publishing.
