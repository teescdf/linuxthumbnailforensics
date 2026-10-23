# linuxthumbnailforensics

Project addressing forensic analysis of thumbnail images and related artefacts in Linux. More detail available at https://doi.org/10.1016/j.fsidi.2022.301498.

## thumbnailcollection.py

Parser for collecting the names of thumbnail files present within user accounts (typically located within $HOME/.cache/thumbnails). The script will collect the filenames and relevant subdirectory names (normal, large, x-large etc.) if present and store them in a text file.

Download the thumbnailcollection.py script and use as follows:

    python3 thumbnailcollection.py

Then specify the location of the thumbnail directory from which you wish to obtain the thumbnail filenames (e.g. /home/[user]/.cache/thumbnails).

The results will be collected into a text file named filenames.txt, in the same directory as where the script was run from. For multiple users it is recommended that you collect and rename before running the script again for other users. Note sudo may be required to collect thumbnail information from other user accounts, unless logging in as each account in turn is done.

## recentlyused.py

Parser for Linux recently-used.xbel files. For use in forensic investigations, and is designed to enable investigators to reconcile deleted carved images to metadata, using Linux thumbnail artefacts and the recently-used.xbel file. 

The short explanation is that Linux thumbnails are named according to the md5sum of the original file's URI. These thumbnails often persist after the original is deleted. Cross referencing data in the recently-used.xbel file against these thumbnails can provide useful intelligence and evidence about the original file, such as it's previous name and location, and dates and times of relevance. This script extracts the URI of each entry in the recently-used.xbel file, along with the corresponding dates and times, produces an MD5 hash of the URI, and stores it all in a CSV file. An investigator can then check off any matching thumbnails against the CSV. If the original file is recoverable using carving, it can also then subsequently be matched (manually) to the corresponding thumbnail using the PhotoDNA hash algorithm, or via visual comparison if PhotoDNA is not available.

Download the recentlyused.py script and use as follows:

    python3 recentlyused.py /path/to/recently-used.xbel

For ease of use, put the recently-used.xbel file in the same directory as the recentlyused.py script!

## .
