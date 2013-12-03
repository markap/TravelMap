from __future__ import with_statement
from google.appengine.api import files

def write_blob(upload_file):
    file_name = files.blobstore.create(mime_type=upload_file.type)
    
    # Open the file and write to it
    with files.open(file_name, 'a') as f:
        f.write(upload_file.value)

    # Finalize the file. Do this before attempting to read it.
    files.finalize(file_name)

    # Get the file's blob key
    return str(files.blobstore.get_blob_key(file_name))