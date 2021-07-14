FROM tensorflow/serving:latest
LABEL maintainer="Takumi Saito"

RUN apt-get update && apt-get install -y curl xz-utils

ENV MODEL_NAME=mnist_arcface

RUN curl -OL https://serving-mnist.s3.amazonaws.com/models.tar.xz \
  && tar -Jxvf models.tar.xz \
  && mkdir -p models/${MODEL_NAME} \
  && mv models/1 models/${MODEL_NAME}
