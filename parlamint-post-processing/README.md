# ParlaMint post-processing scripts

The changes done by these scripts should be incorporated into the ParlaMint data production pipeline. For the time being, these can be run to ParlaMint-FI data for quick fixes.

`fix-parlamint-fi.sh`: fixes to TEI files

`fix-parlamint-fi-linguistic.sh`: fixes to TEI.ana files

`fix-parlamint-fi-post-add-common-content.sh`: fixes to TEI files after add-common-content

For running the scripts, define the following environment variables:

`DIR`: the directory path where the TEI files are located

`SAMPLE` (true/false): when set to true, process only a "sample" set of TEI files:
- include only a sample set of 5 TEI/TEI.ana files in the corpus root file's xml:include's
- add the word "SAMPLE" in the corpus root file title