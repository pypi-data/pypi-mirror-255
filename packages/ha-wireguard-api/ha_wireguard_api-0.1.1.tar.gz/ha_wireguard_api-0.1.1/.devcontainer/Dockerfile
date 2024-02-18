FROM mcr.microsoft.com/vscode/devcontainers/python:0-3.11

# Uninstall pre-installed formatting and linting tools
# They would conflict with our pinned versions
RUN pipx uninstall pydocstyle \
    && pipx uninstall pycodestyle \
    && pipx uninstall mypy \
    && pipx uninstall pylint

# Install Python dependencies from requirements
COPY requirements.txt requirements.txt
COPY .devcontainer/requirements-dev.txt requirements-dev.txt
RUN python -m pip install --upgrade pip setuptools \
    && python -m pip install -r requirements.txt -r requirements-dev.txt \
    && rm requirements.txt requirements-dev.txt

# Set the default shell to bash instead of sh
ENV SHELL /bin/bash