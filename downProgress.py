#This file is part of friendlypodder.
#
    #Friendlypodder is free software: you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
    #the Free Software Foundation, either version 3 of the License, or
    #(at your option) any later version.
#
    #Friendlypower is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.
#
    #You should have received a copy of the GNU General Public License
    #along with Friendlypodder.  If not, see <http://www.gnu.org/licenses/>.

# Copyright 2011 Tor Erling H. Opsahl

import urllib2
import os
from progressbar import ProgressBar


def ensure_dir(dirname):
    path_without_dir = os.popen('pwd').read()
    path_without_dir = path_without_dir.strip()
    path = path_without_dir + '/' + dirname
    if not os.path.exists(path):
        os.makedirs(dirname)


def download_with_progressbar(url, download_dir):
    """Downloads a file and shows a nice progress bar"""
    # Find the file name to show, and to save file under
    file_name = url.split('/')[-1]
    # Make the path where it should go
    file_path = download_dir + '/' + file_name
    # Open the url and the file
    u = urllib2.urlopen(url)
    f = open(file_path, 'wb')
    # Finding file length for the progress bar
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    # Deviding the filesize to get it in Mb
    file_size2 = file_size / 1000000.
    print "Downloading: %s  %s Mb" % (file_name, file_size2)

    # Here comes the call to the progress bar
    file_size_dl = 0
    block_sz = 8192

    # Style for the progressbar, you can change everything Here
    # For more information check progressBar.py
    p = ProgressBar('yellow')

    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        # Write the chunk to a file_size_dl
        f.write(buffer)
        file_size_dl += block_sz
        # Find out how many % we have downloaded
        i = int(file_size_dl * 100. / file_size)
        # The call for the progress bar
        p.render(i, '%s' % i)

    f.close()

# Test function
if __name__ == "__main__":

    url = "http://traffic.libsyn.com/linuxoutlaws/linuxoutlaws215.mp3"
    ensure_dir('tmp')
    path = os.popen('pwd').read()
    path = path.strip()
    download_dir = path + '/tmp'
    download_with_progressbar(url, download_dir)
