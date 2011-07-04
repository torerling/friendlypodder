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

from xml.dom import minidom


def find_media(xml):
    """parses the xml file given and returns a list of urls to the podcasts"""

    urllist = []

    xmldoc = minidom.parse(xml)
    # podcast urls are located in the enclosure element
    enclosure_list = xmldoc.getElementsByTagName("enclosure")
    for element in enclosure_list:
        media = element.attributes['url']
        urllist.append(media.value)

    return urllist

if __name__ == "__main__":
    pass
    #xmlfile = "linuxoutlaws"
    #print find_media(xmlfile)
