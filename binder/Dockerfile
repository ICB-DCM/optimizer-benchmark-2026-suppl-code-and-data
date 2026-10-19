# Image for mybinder.org (built by repo2docker with the repository root as
# build context). Installs the environment pinned in data_analysis/uv.lock.
FROM python:3.13-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /uvx /bin/

ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER=${NB_USER} \
    HOME=/home/${NB_USER}
RUN useradd --create-home --uid ${NB_UID} ${NB_USER}

COPY --chown=${NB_UID} . ${HOME}
USER ${NB_USER}
WORKDIR ${HOME}

ENV UV_NO_CACHE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    PATH=${HOME}/data_analysis/.venv/bin:${PATH}
RUN uv sync --frozen --project data_analysis

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser"]
