# semparl-data-transformation
Tools for gathering and formatting data for the Semantic Parliament dataservice and semantic portal.

**Be sure to check section [Maintenance](#maintenance) when one parliamentary session (valtiopäivät) ends and a new one starts!** 

---

## Contents
1. [General Pipeline](#general-pipeline)
2. [Data production](#data-production)
    1. [Preparation](#preparation)
    2. [Short version: Use Docker](#short-version-use-docker)
    3. [Long version: How it works under the hood](#long-version-how-it-works-under-the-hood)
    4. [Redo only RDF and/XML](#redo-only-rdf-andxml)
    5. [Government proposals](#government-proposals)
3. [Maintenance](#maintenance)

---

&nbsp;
## General Pipeline
1. Gather raw data
2. Extract relevant data to CSV
3. Create xml-file of data in [ParlaCLARIN-format](https://clarin-eric.github.io/parla-clarin/)
4. Create ttl-files of data in RDF-format

&nbsp;
The whole pipeline produces four files for each parliamentary session;
- The Parla-CLARIN version is in its entarity in file ```Speeches_<year>.xml``` 
- The RDF version is spread into three files: ```speeches_<year>.ttl, items_and_documents_<year>.ttl```  and ``` sessions_and_transcripts_<year>.ttl```. 
- (Also various mid-way CSV and txt files)

&nbsp;
 # Data production

 Apart from the scripts mentioned you will also need all the other files present in this repository's root to succesfully do the transformations. Be sure to keep them available. Folders ```fixed_title_txt-files``` and ```original_html``` mimic the source data folder structure and contain few examples for testing. Folder ```other_tools``` contains other useful scripts and files that are not used in the main data pipeline.

&nbsp;
 ## Preparation

 Whether you use Docker or perform the tasks manually, if you wish to run the whole transformation process, you need the source materials from [here](https://version.aalto.fi/gitlab/seco/semparl-speeches-source-backups) (access restricted).
- Copy the folders ```fixed_title_txt-files``` and ```original_html``` to this root folder. Don't
change the names or structure of these folders. (to make things easier you might want to first delete the identical example folders in this repository)

- Speaker information enrichment step uses SPARQL queries. For that you need to create file ```authorization.py``` to the root folder. File should contain row

    ```AUTHORIZATION_HEADER: = {'Authorization':"<password here>"}```


&nbsp;

 # Short version: Use DOCKER
- Install [Docker](https://docs.docker.com/engine/install/).

- Read the above section [Preparation](#preparation)

- If you only wish to update the newest year, you now got all you need!

- First build the Docker image:

    ```sudo docker build . -t pipeline``` (if you have already added yourself to docker group, you don't need 'sudo' now or later)

- Then you can either run the whole transformation process:

    ```sudo docker run --user $(id -u) -v "$(pwd)/results:/app/results" pipeline``` 

    Or update the newest year:

    ```sudo docker run --user $(id -u) -v "$(pwd)/results:/app/results" pipeline update``` 

- After the process is done, the result files will be available in newly made folder ```results```.

Please note that running the whole process might take a whole day or more.
 
 &nbsp;
 # Long version: How it works under the hood

Note: The scripts take either the path to file or a parliamentary session's year as a parameter. The latter can be of form ```YYYY``` (e.g. ```1945```) or ```YYYY_separator```, where the separator separates the different parliamentary sessions of the same year from each other (e.g. ```1975_II```, ```1917_XX```). The separator ```_XX``` occurs only in 1917.

**Start by reading the section [Preparation](#preparation)**

 &nbsp;
 ## PDF-based data 
 ___
 - until Valtiopäivät 1999
 - source: txt-files OCR'ed from pdf-files
 - **bash script** to cover these steps (also for whole period):: ```txt_to_rdf_xml.sh```

 &nbsp;

**Step 0: Manual step for pdf-based data**

As the first line of a transcript (Pöytäkirja) contained crucial metadata, i.e.:

```111. Maanantaina 16 päivänä joulukuuta 1991```

 All the txt-files were run through ```other_tools/print_session-titles.py```. The program printed all of these first lines that were intact. The missing first lines could be easily inferred from the print out and fixed in the txt-file (usually the line was split). This process made the following transformations remarkably easier and more reliable. Files ```PTK_1908_2.txt``` and ```PTK_1908_3.txt``` both included plenary sessions 24-28. The duplicates were manually removed from ```PTK_1908_2.txt```. Transcripts of 1932_II and 1935_II were exceptionally combined with other documents from those parliamentary sessions. The unrelevant section were manually deleted.
You can find the fixed txt-files [here](https://version.aalto.fi/gitlab/seco/semparl-speeches-source-backups).

&nbsp;

**Step 1: Form a CSV from fixed ocr'ed text files**

The text-files are gone over and with the use of regular expressions, the speeches and relevant details are first gathered in a raw, unrefined form into a CSV-format, one CSV-file per text file, one speech per row. Then these raw files are concatenated to form one CSV for one parliamentary session. This combination file
the goes through several clean-ups. Clustered data is split, additional data from other sources is added
and attemps to fix several problems, such as distorted speaker names and split speeches.
***There are several parallel scripts for gathering the raw data**, the correct one is chosen based on the time period. The exact period a script covers can be checked from the start of each script.


To form a CSV file for one parliamentary session: 
- First gather raw data from the individual files that together form one parliamentary session (with suitale script starting with 'txt_to_csv_'), e.g.:
    -  ```python3 txt_to_csv_20-30s.py path/to/txt_file``` --> produces e.g. ```PTK_1927_1_RAW.csv```
- Combine the individual raw data files to one file, e.g.:
    - ```cat path/to/raw_files/*.csv > desired_path/speeches_1927_RAW.csv```
- Clean and enrich data (most notably: speaker info):
    - ```python3 clean_raw_csv.py path/to/combined_file``` --> produces e.g. ```speeches_1927.csv```
- More cleaning operations (especially split speeches and known name issues):
    - ```python3 final_csv_cleaner.py <year>``` --> rewrites ```speeches_<year>.csv```
- Last effort fo fix speaker name and recognition issues:
    - ```python3 name_cleaner.py <year>``` --> rewrites ```speeches_<year>.csv```    


**Step 2: Create XML and RDF from CSV**

Both XML and RDF version are created from the cleaned up CSV. Run:
- ```python3 csv_to_xml.py <year>``` --> produces ```Speeches_<year>.xml```
- ```python3 create_rdf.py <year>``` --> produces ```speeches_<year>.ttl, items_and_documents_<year>.ttl```  and ``` sessions_and_transcripts_<year>.ttl``` 

*Special case: year 1999:*

Parliamentary session 1999's plenary sessions are available in HTML from 86/1999 onwards. For best results first half of 1999 is created from ocr'ed data and  the rest from html. These halfs are combined before creating final XML and RDF files. To do this first create cleaned CSV for start of 1999 as described above and another csv for the last half of 1999 as described below. Name these files   ```speeches_1999_a.csv``` and  ```speeches_1999_b.csv``` appropriately and run:
```python3 combine_1999.py```. After this you can create XML and RDF normally from the produced combined CSV-file.


&nbsp;
## HTML-based data
____ 
- Valtiopäivät 2000-2014
- source: html-data
- **bash script** to cover these steps (also for whole period): ```html_to_rdf_xml.sh```

&nbsp;

**Step 0: Produce the HTML data**

Data is spread on individual plenary session's main page and separate discussion pages, one topic per discussion page.
The HTML data can be scraped from eduskunta.fi web pages or the already gathered and pruned data from [here](https://version.aalto.fi/gitlab/seco/semparl-speeches-source-backups) (access restricted) can be used. This data was downloaded in May/June 2020 and pruned of unneeded source code (footers, nav bars., etc.). The scripts full functionality can be guaranteed only for that version of the data. In either case it is recommended to download the readied data to ensure ease of reuse as the downloading process from eduskunta.fi was very slow and there has been later changes to the html (different tags, etc.).

To scrape the data:

Run ```other_tools/ptk_links.py``` to gather main page html-content of one Valtiopäivät/Parliamentory year to one file and possible discussion page links to another. 

Run ```other_tools/download_content.py``` to gather the html-content from the discussion pages using the link file.

**Step 1: Form a CSV from from HTML files**

As the  main page and the discussions of each plenary session are in different html-files, they are first gathered into separate main page and discussion files, one of each per parliamentary session, one speech per row. At the same time a file 'related details' is created to connect separated bits of details
such as time details. These files are then combined to form a singular CSV-file containing all the speeches. Speaker information is further enriched after this step.

To perform this process run:
- Gather data from discussion pages:
    - ```python3 html_to_csv.py path/to/discussions_<year>.html``` --> produces ```discussions_<year>.csv```
- Gather data from main pages:  
    - ```python3 main_pages_to_csv.py path/to/main_pages_<year>.html``` --> produces ```main_page_speeches_<year>.csv, skt_times_<year>.csv, related_document_details_<year>.csv```. The last two documents store details that help combining the two speech files and in later metadata forming.
- Enrich speaker infromation:
    - ```python3 enrich_member_info.py <year>```  --> rewrites ```speeches_<year>.csv```
    


**Step 2: Create XML and RDF from CSV**

Both XML and RDF version are created from the combined CSV.
- ```python3 csv_to_xml.py <year>``` --> produces ```Speeches_<year>.xml```
- ```python3 create_rdf.py <year>``` --> produces ```speeches_<year>.ttl, items_and_documents_<year>.ttl```  and ``` sessions_and_transcripts_<year>.ttl``` 

 &nbsp;

## XML-based data
___
- Valtiopäivät 2015->
- source: xml-data
- **bash script** to cover these steps (also for whole period): ```xml_to_rdf_xml.sh all``` (note the parameter)

&nbsp;

**Step 1: Form a CSV from from XML**

The XML source data is quick to retrieve so it is gathered in the transformation process by the way of requests to Avoin eduskunta API. The API returns each plenary session in separate JSON-wrapped XML. The speeches are gathered to CSV-files, one parliamentary session per file, one speech per row. Speaker information is further enriched after this step.

- Gather data:
    - ```python3 xml_to_CSV.py <year>``` --> produces ```speeches_<year>.csv```
- Enrich speaker infromation:
   - ```python3 enrich_member_info.py <year>```  --> rewrites ```speeches_<year>.csv```

**Step 2: Create XML and RDF from CSV**

Both XML and RDF version are created from the CSV.

- ```python3 csv_to_xml.py <year>``` --> produces ```Speeches_<year>.xml```
- ```python3 create_rdf.py <year>``` --> produces ```speeches_<year>.ttl, items_and_documents_<year>.ttl```  and ``` sessions_and_transcripts_<year>.ttl``` 

&nbsp;

 ## Manually update the current year with new plenary sessions
 ___
 &nbsp;

 Run ```./xml_to_rdf_xml.sh update```, it repeates the steps described above for the current parliamentary year.

 &nbsp;

 ## Redo only RDF and/or XML
 ___
 &nbsp;
If you find yourself wanting to only tweak the RDF and XML formats, it might be more convenient to use the
ready-made CSV-files in the [source backup repo](https://version.aalto.fi/gitlab/seco/semparl-speeches-source-backups). Folder ```mid-way-files``` contains all the (already enriched) data in
 previously mentiond ```speeches_<year>.csv``` files plus some additional required text files (HTML-period). You can shortcut by using these files. Running  ```python3 csv_to_xml.py <year>``` and/or ```python3 create_rdf.py <year>```
with that year's files present in the root produces the final data files.
Using the readymade CSV's is notably quicker than redoing the whole process.

 &nbsp;

## Government proposals
___
Government proposals can be gathered and transformed to RDF with
   
    ```python3 other_tools/transform_gov_proposals.py```

This process can be run by using a presearched list of government ids and retrieving the documents based on that or by researching the ids and then doing the the rest of the transformation process. Choose the option by commenting out the appropriate rows (see code).

&nbsp;

# Maintenance
 Certain things need to be adjusted every time a parliamentary session (valtiopäivät) ends and a new one starts.

 - In ```parliamentary_session.csv```:
    - fill in the end date of the previous session ('Päättymispäivä')
    - add id for the new session (e.g. 2023) in the first column ('Valtiopäivien tunnus') in a new row
    - add start date for that session ('alkupäivä')
    - if electoral period has changed, add its URI ('Vaalikausi')
- In ```xml_to_rdf_xml.sh``` 
    - expand the for-loop's year limit to cover the new session
    - change the variable ```year``` in the ```else```-condition to the current year
- [Optional] In ```xml_to_CSV.py```
    - in dictionary ```session_count``` you can add a new key-value pair for the previous year. The value is the amount of sessions there were for the year. If such value exists, the script knows to stop quering documents after the last session (instead of after a set amount of queries that return nothing). Similar key-value can be set for current year as well, but the user needs to remember to update this value everytime they wish to update the current year.
