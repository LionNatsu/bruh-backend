FROM python:3.7-alpine
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

COPY ./requirements.txt /code/
COPY . /code/
COPY ./compose/web/*.sh /code/

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
