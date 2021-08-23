FROM python:3.6

ENV RUNNING_IN_DOCKER_CONTAINER Yes

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

RUN chmod a+r *
RUN chmod -R a+rwx ./original_html
RUN chmod -R a+rwx ./fixed_title_txt-files
RUN chmod a+rx *.sh
RUN chmod a+rx *.py
RUN chmod a+w .
RUN chmod a+w ./results

ENTRYPOINT [ "./speech_transformation.sh" ]
CMD [ "all" ] 


# Run with this to create all:
# docker run --user $(id -u) -v "$(pwd)/results:/app/results" pipeline 

# Run with this to update newest year:
# docker run --user $(id -u) -v "$(pwd)/results:/app/results" pipeline update