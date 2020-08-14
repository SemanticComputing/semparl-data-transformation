# semparl-data-transformation
Tools for gathering and formatting data for the Semantic Parliament dataservice and semantic portal.

## General Pipeline
1. Gather raw data
2. Extract relevant data to CSV
3. Create xml-file of data in [ParlaCLARIN-format](https://clarin-eric.github.io/parla-clarin/)
4. Create ttl-files of data

#### manual step for pdf-based data
As the first line of a Pöytäkirja contained crucial metadata
```
111. Maanantaina 16 päivänä joulukuuta 1991
```
 all the txt-files were run through ```print_session-titles.py```. The program printed all of these first lines that were intact. The missing first lines could be easily inferred from the print out and fixed in the txt-file (usually the line was splitted). This process for a whole decade took max. 1 hour and made the following processings remarkably easier.

## Valtiopäivät 1980-1988
- source: txt-files OCR'ed from pdf-files


## Valtiopäivät 1989-1994
- source: txt-files OCR'ed from pdf-files 


## Valtiopäivät 1985-1999
- source: txt-files OCR'ed from pdf-files 



## Valtiopäivät 2000-2014
- source: html-data

Data was spread on individual session's main page and separate discussion pages, one topic per discussion page.
```ptk_links.py``` was used to gather main page html-content of one Valtiopäivät/Parliamentory year to one file and possible discussion page links to another. ```download_content.py``` was used to gather the html-content from the discussion pages using the link file.

```main_pages_to_csv.py``` extracted relevant data from mainpage html-file and transformed it to csv. It also produced ```related_documents_details_XXXX.csv``` to be used to fill in related document info for discussion page speeches. 
```html_to_csv.py``` produces a csv-file from from discussion page html.
```combine_speeches``` comibines the two csvs to create final ```speeches_XXXX.csv``` containing all the scpeeches for Valtiopäivät XXXX.

```html_to_all_csv.sh```-script was used to slightly automate this process.

 ```csv_to_xml.py``` took  the final ```speeches_XXXX.csv```-file and transformed the data to ParlaClarin-xml format, ```Speeches_XXXX.xml```.
 Some mistakes were very easy to spot from the xml, e.g. party-related problems from the ```<orgList>```-element, there often was one or two per year, these were **manually** fixed in the source csv and the xml creator re-run as this step took only one or two minutes.

 ```create_rdf.py``` transformed the data from the csv to RDF and produced files ```speeches_XXXX.ttl, items_and_documents_XXXX.ttl```  and ``` sessions_and_transcripts_XXXX.ttl```. This program required a csv-file ```python_csv_parliamentMembers.csv``` containing parliament member info, e.g. personal URIs, parties, party URIs and so on, for semantic tagging.


## Valtiopäivät 2015-2020
- source: xml-data

```xml_to_CSV.py``` downloaded and converted xml data to ```speeches_XXXX.csv```, again, one Valtiopäivät per file.

XML and TTL created as above.
