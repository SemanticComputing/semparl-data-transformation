# semparl-data-transformation
Tools for gathering and formatting data for the Semantic Parliament dataservice and semantic portal.

## General Pipeline
1. Gather raw data
2. Extract relevant data to CSV
3. Create xml-file of data in [ParlaCLARIN-format](https://clarin-eric.github.io/parla-clarin/)
4. Create ttl-files of data in RDF-format

&nbsp;
 # Instructions

 ## Short version: Use DOCKER
Make folder 'results' at the root

Please note that running the whole process might take a whole day or more.
 ## Long version: How it's works under the hood

The whole pipeline produces four files for each parliamentary session;
- The Parla-CLARIN version is in its entarity in file ```Speeches_<year>.xml``` 
- The RDF version is spread into three files: ```speeches_<year>.ttl, items_and_documents_<year>.ttl```  and ``` sessions_and_transcripts_<year>.ttl```. 

The process requires csv-files:
 - ```python_csv_parliamentMembers.csv``` containing parliament member info, e.g. personal URIs, parties, party URIs and so on, for linking.
 - ```parliamentary_sessions.csv``` containing parliamentary seasons info for linking
 - The files can be found [here](https://version.aalto.fi/gitlab/seco/semparl-speeches-source-backups) (Access restricted) 


 &nbsp;


 ## PDF-based data 
 ___
 - until Valtiopäivät 1999
 - source: txt-files OCR'ed from pdf-files


**Step 0: Manual step for pdf-based data**

As the first line of a Pöytäkirja contained crucial metadata. I.e.:

```111. Maanantaina 16 päivänä joulukuuta 1991```

 All the txt-files were run through ```ocr_data/print_session-titles.py```. The program printed all of these first lines that were intact. The missing first lines could be easily inferred from the print out and fixed in the txt-file (usually the line was split). This process for  made the following tranformations remarkably easier and more reliable. Files ```PTK_1908_2.txt``` adn ```PTK_1908_3.txt``` both included plenary sessions 24-28, the duplicates were manuaylly removed from ```PTK_1908_2.txt```.

&nbsp;

**Step 1: Form a CSV from fixed ocr'ed text files and transform it to RDF and XML**

Create the following folders

???????


 or edit the paths in ```ocr_data/txt_to_rdf.sh``` and in the scripts run by it to suit your needs.

- For years 1907-1998:

    Run ```./ocr_data/txt_to_rdf.sh```

- For year 1999:

    Parliamentary session 1999's plenary sessions are available in HTML from 86/1999 onwards. For best results first half of 1999 is created from ocr'ed data and  the rest from html. These halfs are combined before creating final XML and RFD files.

    Run ```TBA```
....

&nbsp;
## HTML-based data
____ 
- Valtiopäivät 2000-2014
- source: html-data

**Step 0: Produce the HTML data**

Data is spread on individual plenary session's main page and separate discussion pages, one topic per discussion page.
Scrape the HTML data from Eduskunta.fi-web pages or use the already gathered and pruned data from [here](https://version.aalto.fi/gitlab/seco/semparl-speeches-source-backups) (Access restricted) This data was downloaded in May/June 2020 and pruned of unneeded source code (footers, nav bars., etc.). The scripts full functionality can be guaranteed only for that version of the data. In either case it is recommended to download the data to ensure ease of reuse as the downloading process from eduskunta.fi was very slow.

To scrape the data:

Run ```html_data/ptk_links.py``` to gather main page html-content of one Valtiopäivät/Parliamentory year to one file and possible discussion page links to another. 

Run ```html_data/download_content.py``` to gather the html-content from the discussion pages using the link file.

**Step 1: Form a CSV from from HTML files and transform it to RDF and XML**

Create 

??????

 or edit paths in ```html_to_all_csv.sh``` and in the scripts run by it to suit your needs.

Run ```./html_data/html_to_rdf_xml.sh```


 &nbsp;

## XML-based data
___
- Valtiopäivät 2015-2021
- source: xml-data

Run ```./xml_data/xml_to_rdf_xml.sh```

&nbsp;
 # Update with new plenary sessions

 Edit the loop range in ```./xml_data/xml_to_rdf_xml.sh``` to suit your needs to avoid redoing old years.

 Edit the amount of sessions to download for your desired year in ```./xml_data/xml_to_CSV.py```

 Run ```./xml_data/xml_to_rdf_xml.sh```


