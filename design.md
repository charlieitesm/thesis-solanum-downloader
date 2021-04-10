# Solanum downloader

Given a list of csv files the program should:

1. Filter out duplicated URLs so as to try them only once
   * Check duplicated urls in Gbif and see if they are in the same section (They are)
1. Create parent download folder
1. Download images
   1. If they en with an extension, download them directly
   1. If not, download the html and parse the img#src attribute
1. If there's a failure
   1. Log it
   1. Add it to a pandas DF for reporting (which should also be persisted to disk eventually)
1. Should detect if the image already exists on disk and if it does, skip it.
   1. Use the filename to detect duplicates.
   1. This will only work if there is 1 and only 1 picture per ID.
   1. These should only be logged
   
# Nice to have's
1. Downloading progress
1. Parallelized downloads
1. Add a CSV with the summary for the images for each section

    