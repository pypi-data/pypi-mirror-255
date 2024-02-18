Bondzai Media Handler
=====================

Description
~~~~~~~~~~~

Bondzai Media Handler is a tool used to convert media data (audio,
image, video) file to a raw binary file. For the present, the file's
Mime accepted are the following:

-  Audio

   -  audio/x-wav
   -  audio/mpeg

-  Image

   -  image/jpeg
   -  image/png
   -  image/tiff

-  Video

   -  video/mp4
   -  video/quicktime
   -  video/webm

Installation
~~~~~~~~~~~~

ffmpeg
''''''

In order to work, this tool needs ``ffmpeg`` installed

Linux/Ubuntu

.. code:: bash

   apt-get install ffmpeg

MacOS (Homebrew)

.. code:: bash

   brew install ffmpeg
   

bondzai.media-handler
'''''''''''''''''''''

.. code:: bash

   pip install bondzai.media-handler

Usage
~~~~~

.. code:: python

   from bondzai.media_handler import get_raw_data, get_metadata, \
       save_binary, load_binary

   # Getting raw data from a media file
   data = get_raw_data("path/to/file.[mp3|mp4|wav|webm|jpg|png|...]")

   # Getting meta data from a media file
   meta = get_metadata("path/to/file.[mp3|mp4|wav|webm|jpg|png|...]")

   # Saving raw data in a binary file
   save_binary("path/to/file.bin", data)

   # Loading raw data from a binary file
   data = load_binary("path/to/file.bin")
