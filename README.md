# linuxthumbnailforensics

Project addressing forensic analysis of thumbnail images and related artefacts in Linux.

# recentlyused.py

Parser for Linux recently-used.xbel files. For use in forensic investigations, and designed to enable investigators to reconcile deleted carved images to metadata, using Linux thumbnail artefacts and the recently-used.xbel file. More detail available at https://doi.org/10.1016/j.fsidi.2022.301498.

The short explanation is that Linux thumbnails are named according to the md5sum of the original file's URI. These thumbnails often persist after the original is deleted. Cross referencing data in the recently-used.xbel file against these thumbnails can provide useful intelligence and evidence about the original file, such as it's previous name and location, and dates and times of relevance. This script extracts the URI of each entry in the recnetly-used.xbel file, along with the corresponding dates and times, produces an MD5 hash of of the URI, and stores it all in a CSV file. An investigator can then check off any matching thumbnails against the CSV. If the original file is recoverable using carving, it can also then subsequently be matched (manually) to the corresponding thumbnail using the PhotoDNA hash algorithm, or via visual comparsion if PhotoDNA is not available.

Download the recentlyused.py script and use as follows:

    python3 recentlyused.py /path/to/recently-used.xbel

For ease of use, put the recently-used.xbel file in the same directory as the recentlyused.py script!

# .
