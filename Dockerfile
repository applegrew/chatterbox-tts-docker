FROM python:3.11-bullseye

WORKDIR /app

RUN pip install "numpy==1.25" argparse
RUN pip install chatterbox-tts torch flask flask-cors

EXPOSE 9080

ARG OUTPUT_DIR
ARG DEBUG

ENV OUTPUT_DIR=${OUTPUT_DIR}
ENV DEBUG=${DEBUG}

# Copy the source code
COPY ./src /app/src
COPY ./voices /app/src/voices

# Create output directory
RUN mkdir -p ${OUTPUT_DIR}

CMD ["python", "-m", "src.main", "--host", "0.0.0.0", "--port", "9080"]
