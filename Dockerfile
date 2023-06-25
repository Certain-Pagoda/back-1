FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
		jq \
		&& \
	rm -rf /var/lib/apt/lists/*

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
# https://stackoverflow.com/questions/59732335/is-there-any-disadvantage-in-using-pythondontwritebytecode-in-docker
# ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
	poetry install --no-dev

COPY . ./

#CMD exec gunicorn --bind :8080 --reload --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 app:app
CMD ["/app/run.sh"]
