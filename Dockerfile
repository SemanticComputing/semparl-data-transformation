FROM python:3.6

ENV RUNNING_IN_DOCKER_CONTAINER Yes

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

RUN chmod +x speech_transformation.sh
RUN chmod +x txt_to_rdf_xml.sh
RUN chmod +x html_to_rdf_xml.sh
RUN chmod +x xml_to_rdf_xml.sh

CMD ./speech_transformation.sh


# docker run -v "$(pwd)/results:/app/results" pipeline 


#Vajaa lista:
#clean_raw
#xml-kerääjä
#main_pages
#html_to_csv
#1907 kansio
# skriptit