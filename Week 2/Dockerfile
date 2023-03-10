FROM prefecthq/prefect:2.7.10-python3.10

COPY docker-requirements.txt .

RUN pip install -r docker-requirements.txt --trusted-host pypi.python.org --no-cache-dir

RUN mkdir -p /opt/prefect/data/
RUN mkdir -p /opt/prefect/data/yellow
RUN mkdir -p /opt/prefect/data/green
RUN mkdir -p /opt/prefect/flows/

COPY flows /opt/prefect/flows
