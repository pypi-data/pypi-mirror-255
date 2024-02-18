VERSION 0.7

source:
    ARG python

    FROM python:$python

    RUN pip install ruff==0.1.14 pytest==7.4.4
    WORKDIR /app
    COPY setup.py setup.cfg ampdata tests /app/
    RUN pip install -e .

test:
    ARG python
    FROM +source --python $python

    RUN pytest tests

test-matrix:
    BUILD +test --python 3.7
    BUILD +test --python 3.8
    BUILD +test --python 3.9
    BUILD +test --python 3.10
    BUILD +test --python 3.11
    BUILD +test --python 3.12

check:
    FROM +source --python 3.10

    RUN ruff check