FROM python:3.11.4-alpine

ENV LANG=zh_CN.UTF-8 \
    SHELL=/bin/bash \
    WORK_DIR=/app

WORKDIR ${WORK_DIR}

COPY requirements.txt ${WORK_DIR}
COPY ariabot ${WORK_DIR}/ariabot

RUN set -x \
    && sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk update -f \
    && apk upgrade \
    && apk --no-cache add -f gcc \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r ${WORK_DIR}/requirements.txt \
    && apk del gcc \
    && rm -rf /var/cache/apk/* \
    && rm -rf /root/.cache

CMD ["python", "-m", "ariabot"]
