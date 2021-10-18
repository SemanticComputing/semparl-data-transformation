# semparl-data-transformation
Tools for gathering and formatting data for the Semantic Parliament dataservice and semantic portal.

## General Pipeline
1. Gather raw data
2. Extract relevant data to CSV
3. Create xml-file of data in [ParlaCLARIN-format](https://clarin-eric.github.io/parla-clarin/)
4. Create ttl-files of data in RDF-format

&nbsp;
The whole pipeline produces four files for each parliamentary session;
- The Parla-CLARIN version is in its entarity in file ```Speeches_<year>.xml``` 
- The RDF version is spread into three files: ```speeches_<year>.ttl, items_and_documents_<year>.ttl```  and ``` sessions_and_transcripts_<year>.ttl```. 
 # Instructions

 ## Short version: Use DOCKER
- Install [Docker](https://docs.docker.com/engine/install/).

- Speaker information enrichment step uses SPARQL queries. For that you need to create file ```authorization.py``` to the root folder. File should contain row

    ```AUTHORIZATION_HEADER: = {'Authorization':"<password here>"}```

- If you only wish to update the newest year, you now got all you need!

    If you wish to run the whole transformation process, you need the source materials from [here](https://version.aalto.fi/gitlab/seco/semparl-speeches-source-backups) (access restricted).
    Copy the folders ```fixed_title_txt-files``` and ```original_html``` to this root folder. Don't
    change the names or structure of these folders.


- First build the Docker image:

    ```sudo docker build . -t pipeline``` (if you have already added yourself to docker group, you don't need 'sudo' now or later)

- Then you can either run the whole transformation process:

    ```sudo docker run --user $(id -u) -v "$(pwd)/results:/app/results" pipeline``` 

    Or update the newest year:

    ```sudo docker run --user $(id -u) -v "$(pwd)/results:/app/results" pipeline update``` 

- After the process is done, the result files will be available in newly made folder ```results```.

Please note that running the whole process might take a whole day or more.
 
 &nbsp;
 ## Long version: How it works under the hood



 ### PDF-based data 
 ___
 - until Valtiopäivät 1999
 - source: txt-files OCR'ed from pdf-files


**Step 0: Manual step for pdf-based data**

As the first line of a Pöytäkirja contained crucial metadata. I.e.:

```111. Maanantaina 16 päivänä joulukuuta 1991```

 All the txt-files were run through ```other_tools/print_session-titles.py```. The program printed all of these first lines that were intact. The missing first lines could be easily inferred from the print out and fixed in the txt-file (usually the line was split). This process made the following transformations remarkably easier and more reliable. Files ```PTK_1908_2.txt``` and ```PTK_1908_3.txt``` both included plenary sessions 24-28. The duplicates were manually removed from ```PTK_1908_2.txt```.
You can find the fixed txt-files [here](https://version.aalto.fi/gitlab/seco/semparl-speeches-source-backups).
&nbsp;

**Step 1: Form a CSV from fixed ocr'ed text files**

The text-files are gone over and with the use of regular expressions, the speeches and relevant details are first gathered in a raw, unrefined form into a CSV-format, one CSV-file per text file, one speech per row. Then these raw files are concatenated to form one CSV for one parliamentary session. This combination file
the goes through several clean-ups. Clustered data is split, additional data from other sources is added
and attemps to fix several problems, such as distorted speaker names and split speeches.

**Step 2: Create XML and RDF from CSV**

Both XML and RDF version are created from the cleaned up CSV.

*Special case: year 1999:*

Parliamentary session 1999's plenary sessions are available in HTML from 86/1999 onwards. For best results first half of 1999 is created from ocr'ed data and  the rest from html. These halfs are combined before creating final XML and RFD files.


&nbsp;
### HTML-based data
____ 
- Valtiopäivät 2000-2014
- source: html-data

**Step 0: Produce the HTML data**

Data is spread on individual plenary session's main page and separate discussion pages, one topic per discussion page.
The HTML data can be scraped from eduskunta.fi web pages or the already gathered and pruned data from [here](https://version.aalto.fi/gitlab/seco/semparl-speeches-source-backups) (access restricted) can be used. This data was downloaded in May/June 2020 and pruned of unneeded source code (footers, nav bars., etc.). The scripts full functionality can be guaranteed only for that version of the data. In either case it is recommended to download the readied data to ensure ease of reuse as the downloading process from eduskunta.fi was very slow.

To scrape the data:

Run ```other_tools/ptk_links.py``` to gather main page html-content of one Valtiopäivät/Parliamentory year to one file and possible discussion page links to another. 

Run ```other_tools/download_content.py``` to gather the html-content from the discussion pages using the link file.

**Step 1: Form a CSV from from HTML files**

As the  main page and the discussions of each plenary session are in different html-files, they are first gathered into separate main page and discussion files, one of each per parliamentary session, one speech per row. At the same time a file 'related details' is created to connect separated bits of details
such as time details. These files are then combined to form a singular CSV-file containing all the speeches. peaker information is further enriched after this step.

**Step 2: Create XML and RDF from CSV**

Both XML and RDF version are created from the combined CSV.


 &nbsp;

### XML-based data
___
- Valtiopäivät 2015->
- source: xml-data

**Step 1: Form a CSV from from XML**

The XML source data is quick to retrieve so it is gathered in the transformation process by the way of requests to Avoin eduskunta API. The API returns each plenary session in separate JSON-wrapped XML. The speeches are again gathered to one CSV, one parliamentary session per file, one speech per row. Speaker information is further enriched after this step.

**Step 2: Create XML and RDF from CSV**

Both XML and RDF version are created from the CSV.

&nbsp;
 ## Manually update the newest year with new plenary sessions

 Update the amount of held sessions for the current year in dict ```session_count``` in ```xml_to_CSV.py```

 Run ```./xml_to_rdf_xml.sh update```

 &nbsp;


# Government proposals

Government proposals can be gathered and transformed to RDF with
   
    ```python transform_gov_proposals.py```

This process can be run by using a presearched list of government ids and retrieving the documents based on that or by researching the ids and then doing the the rest of the transformation process. Choose the option by commenting out the appropriate rows (see code).