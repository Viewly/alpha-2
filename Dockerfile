FROM python:3.6.1
MAINTAINER furion <_@furion.me>

# add our code
COPY . /project_root
WORKDIR /project_root

RUN pip install -r requirements.txt

ENV PRODUCTION yes
ENV IPFS_URL https://ipfs.view.ly

EXPOSE 5000

CMD ["gunicorn", "-w", "1", "-t", "60", "-b", "0.0.0.0:5000", "src.views:app"]
