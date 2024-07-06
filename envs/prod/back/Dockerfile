FROM python:3.11.4-bookworm

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y postgresql-client vim supervisor

WORKDIR /code

# Ajoutez ces deux lignes pour créer un nouvel utilisateur et lui donner la propriété du répertoire de travail
RUN addgroup --gid 1000 groupcontainer
RUN useradd -ms /bin/bash --uid 1000 matcha
RUN chown -R starter:starter /code
RUN chmod -R 755 /tmp

ENV PYTHONPATH=/code/app
ENV EXPORT_PATH=/tmp/

COPY ./app/requirements.txt ./app/requirements.txt
COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN CPUCOUNT=1 pip install -r ./app/requirements.txt

EXPOSE 5001
USER matcha
ENTRYPOINT [ "bash", "-cl", "./envs/prod/back/back-start.sh" ]
# CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
