FROM python:3.7 AS build
COPY ./requirements.txt ./requirements.txt
RUN pip3 install --user -r ./requirements.txt

FROM python:3.7
RUN useradd --create-home --shell /bin/bash app
USER app
COPY --from=build --chown=app:app /root/.local /home/app/.local
COPY --chown=app:app app /app
ENV PATH=/home/app/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
WORKDIR /app
CMD ["python3", "server.py"]