FROM python:3.6

ENV RUNNING_IN_DOCKER_CONTAINER Yes

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

RUN chmod a+r *
RUN chmod a+rx *.sh
RUN chmod a+rx *.py
RUN chmod a+w .
RUN chmod a+w ./results

ENTRYPOINT [ "./speech_transformation.sh" ]
CMD [ "all" ] 
# update



# docker run --user $(id -u) -v "$(pwd)/results:/app/results" pipeline 


#Vajaa lista:
#clean_raw
#xml-kerääjä
#main_pages
#html_to_csv
#1907 kansio
# skriptit