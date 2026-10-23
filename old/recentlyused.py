# This script is designed to parse a recently-used.xbel file and extract each entry's URI, added, modified and visited date, and also produce the MD5 hash of the file URI
# The script should be run against a recently-used.xbel file, using the command line structure of 'python recentlyused.py /path/to/recently-used.xbel'. The data is then output into a CSV file called 'recent.csv'
# The hash of the file URI can be cross referenced against the files found in the relevant user's $HOME/.cache/thumbnails directory to find matches 
# When combined with file carving and PhotoDNA, the original file may be recovered, corroborated agianst the thumbnail image, and additional context and provneance given to it!
import csv
import hashlib
import sys
import xml.etree.ElementTree as ET

# Get the filename from the command line argument or produce error message
if len(sys.argv) < 2:
    print("Please specify the path to the recently-used.xbel file as a command line argument.")
    sys.exit(1)
filename = sys.argv[1]

# Parse the XML file
tree = ET.parse(filename)

# Get the root element
root = tree.getroot()

# Create a CSV file for the extracted data
with open('recent.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Write the coumn headers to the CSV file
    writer.writerow(['File Path', 'Added', 'Modified', 'Visited', 'MD5sum'])

    # Iterate over each bookmark element to look for the data required
    for bookmark in root.findall('./bookmark'):
        # Extract the data from the attributes
        href = bookmark.get('href')
        added = bookmark.get('added')
        modified = bookmark.get('modified')
        visited = bookmark.get('visited')

        # Calculate the MD5 hash of the href data
        md5 = hashlib.md5(href.encode()).hexdigest()

        # Write the data to the CSV file
        writer.writerow([href, added, modified, visited, md5])
