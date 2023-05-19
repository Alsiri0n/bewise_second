FROM python:3.11
RUN useradd bewise
RUN apt-get -y update
RUN apt-get install -y ffmpeg
RUN mkdir -p /usr/src/app/bewise_second
WORKDIR /usr/src/app/bewise_second
COPY . /usr/src/app/bewise_second/
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --without dev --no-root
RUN chmod +x /usr/src/app/bewise_second/boot.sh
ENTRYPOINT ["./boot.sh"]
EXPOSE 8000