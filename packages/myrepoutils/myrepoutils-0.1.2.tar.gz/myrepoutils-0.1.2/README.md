To deploy and manage a Python package on PyPI, with your code hosted on GitHub, follow these refined steps:

### 1. Install Poetry

Poetry is a Python dependency management and packaging tool. Begin by installing it via your terminal:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Ensure Poetry's path is included in your system's PATH to use it globally.

### 2. Initialize and Configure Poetry

- **Initialize Poetry**: In your project's root directory (e.g., `/home/sam/github/myrepoutils`), run the following to create a `pyproject.toml` file. This file is essential for Poetry to recognize and manage your project.

  ```bash
  cd /home/sam/github/myrepoutils
  poetry init
  ```

- **Configure `pyproject.toml`**: Edit the `pyproject.toml` to include your package's details, like name, version, description, authors, and dependencies. Here's an example configuration:

  ```toml
  [tool.poetry]
  name = "myrepoutils"
  version = "0.1.0"
  description = "A brief description of your package"
  authors = ["Your Name <you@example.com>"]

  [tool.poetry.dependencies]
  python = "^3.11"

  [tool.poetry.dev-dependencies]
  pytest = "^6.2.4"
  ```

### 3. Version Your Package

Adhere to Semantic Versioning (SemVer), which uses a `MAJOR.MINOR.PATCH` format:

- Increment the `MAJOR` version for incompatible API changes.
- Increment the `MINOR` version for new, backward-compatible functionalities.
- Increment the `PATCH` version for backward-compatible bug fixes.

Based on your changes, update your version accordingly in the `pyproject.toml` file.

### 4. Build Your Package

With your `pyproject.toml` set up, build your package using Poetry:

```bash
poetry build
```

This command creates a distributable package in the `dist` folder.

### 5. Publish Your Package to PyPI

- **Create a PyPI Account**: Ensure you have an account on [PyPI](https://pypi.org/).
- **Publish**: Use Poetry to publish your package to PyPI. When prompted, enter your PyPI credentials:

  ```bash
  poetry publish
  ```

### 6. Update Your Package

To release new versions:

1. Update the version in `pyproject.toml` as per semantic versioning.
2. Rebuild and republish your package:

   ```bash
   poetry version patch  # Use `minor` or `major` for significant updates.
   poetry build
   poetry publish
   ```

### Additional Tips:

- Verify your package name is unique on PyPI.
- Test your package locally before publishing.
- Consider implementing a CI/CD pipeline for automated testing and deployment.

This streamlined guide facilitates the creation and publication of a Python package using Poetry on platforms like Ubuntu, ensuring adherence to best practices in the Python community.
