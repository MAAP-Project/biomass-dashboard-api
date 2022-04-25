FROM lambci/lambda:build-python3.8
# or, if choosing to use a container pre-built with numpy:
# FROM AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/PROJECT-dashboard-api-base:TAG

WORKDIR /app

COPY README.md /app/README.md
COPY dashboard_api/ /app/dashboard_api/
COPY setup.py /app/setup.py

RUN pip install --upgrade pip && \
    pip install . mangum>=0.10.0 -t /asset --no-binary pydantic

RUN cd /asset && find . -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-[2-3][0-9]//'); cp $f $n; done;
RUN cd /asset && find . -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
RUN cd /asset && find . -type f -a -name '*.py' -print0 | xargs -0 rm -f
RUN rm -rdf /asset/numpy/doc/ /asset/boto3* /asset/botocore* /asset/bin /asset/geos_license /asset/Misc

RUN mkdir /asset/stack
#COPY stack/config.yml /asset/stack/config.yml
COPY lambda/handler.py /asset/handler.py

CMD ["echo", "hello world"]
