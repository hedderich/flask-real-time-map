FROM tiangolo/uwsgi-nginx-flask:python3.6

ENV STATIC_PATH /usr/local/lib/python3.6/site-packages/real_time_map/static/
ENV LIVEMAP_SETTINGS /app/example_settings.cfg

COPY . /app
RUN pip install .
