#!/usr/bin/env python
# vim:fileencoding=utf8

# friendlypodder, a simple friendly podcatcher
# Got a lot of inspiration from bashpodder
# And some good help from some nice libs from Nadia Alramli
# The two scripts that I got from her: terminal.py and progressbar.py
# Are both under the BSD liscence
# The spinner library is from Pádraig Brady and is under the CC-BY-V3
# All the rest of the files are my work, and are under GPL v3
# See the liscence file for details

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

from downProgress import download_with_progressbar
from xmlparsing import find_media as parse
from terminal import render
from spinner import spinner
import os
import sys
import urllib2
import thread

#FIXME: I don't feel that my groups here are optimal, maybe reorder?
####   "GUI" Printing stuff


def print_tick():
    """Prints a green tick"""
    print render("%(GREEN)s✔%(NORMAL)s"),


def print_x():
    """Prints a red x-mark"""
    print render("%(RED)s✘%(NORMAL)s")


def make_title(text):
    """Make a markdown-ish header in bold blue"""
    string = "%(BLUE)s%(BOLD)s" + text + "%(NORMAL)s"
    print render(string)
    string = "%(BLUE)s%(BOLD)s" + "=" * len(text) + "%(NORMAL)s"
    print render(string)

#FIXME: Should probably group these better some time`
####    Workhorse big functions


def update_and_download():
    feeds = start_down_rss()
    download_new_episodes(feeds)


def update_and_catch_up():
    feeds = start_down_rss()
    catch_up(feeds)


def start_down_rss():
    """Starts downloading rss feeds from the config file, and returns a
    dictionary of new podcasts and names {podcast_name:list_of_rss}"""
    # Start with a blank line so that we get a bit away from the prompt
    print ''
    make_title('Downloading rss feeds')
    print ''

    new_media = {}

    feeds = read_config_file()

    # We have to sort the list with names that is short first to make_title
    # it look good
    feeddict = {}
    lenlist = [len(podcast[0]) for podcast in feeds]
    for i in range(len(feeds)):
        feeddict[lenlist[i]] = []
    for i in range(len(feeds)):
        feeddict[lenlist[i]].append(feeds[i])
    keys = feeddict.keys()
    keys.sort()

    sorted_feeds = []
    for i in keys:
        for j in feeddict[i]:
            sorted_feeds.append(j)

    feeds = sorted_feeds[:]

    for podcast in feeds:
        name = podcast[0]
        url = podcast[1]
        #FIXME: For some reason this gives me an updating one line print
        #       I don't have a clue why, but the effect is nice :)
        print '\r  Downloading the rss feed for %s' % name,
        media = download_and_parse_rss(url)
        media = not_in_logs(media, name)
        new_media[name] = media

    # Print number of new podcasts and a green tick
    print '\n',
    print_tick()
    num_new_files = 0
    if not new_media == {}:
        for key in new_media:
            num_new_files += len(new_media[key])
    # Add code to get rid of the (s) thing
    print '%d new file(s) to download' % num_new_files
    print ''

    return new_media


def catch_up(podcast_dict):
    """Adds the urls from the dictionary to the logs"""
    make_title('Adding all episodes to the logs')
    for name in podcast_dict:
        new = not_in_logs(podcast_dict[name], name)
        add_to_log(new, name)
    print '' #FIXME Needed to get rid of the spinner artifact
    print_tick()
    print 'Caught up with all podcasts'
    print ''

def download_new_episodes(podcast_dict):
    """Downloads the episodes from the dictionary and adds them to the
    logfile for that episode"""

    make_title('Downloading new episodes')

    for name in podcast_dict:
        for episode in podcast_dict[name]:
            download_file(episode, name)
            # add_to_log wants dict
            url = []
            url.append(episode)
            add_to_log(url, name)
    print ''
    print_tick()
    print 'Up to date on all episodes'
    print ''

#FIXME: Need to write a function to validate the config file

#FIXME: Write add function with reading from clipboard os.popen('xsel').read()


####    Things to do with the config file


def read_config_file():
    """Read in the config file and return a list of tuples"""
    beginpath = os.popen('pwd').read()
    config_path = beginpath.strip() + '/friendlypodder.conf'
    # use config path in working folder if it exists
    if os.path.exists(config_path):
        f = open("friendlypodder.conf")
    # if not use os.path.expanduser(~/.friendlypodder.conf)
    else:
        f = open(os.path.expanduser("~/.friendlypodder.conf"))
    lines = []
    for line in f.readlines():
        # The entries in the config file is written like this:
        # [title of podcast] rss://to.podcast.feed
        line = line.strip()
        strlist = line.split(']')
        strlist[0] = strlist[0][1:]
        strlist[1] = strlist[1].strip()
        tmplist = [strlist[0], strlist[1]]
        lines.append(tuple(tmplist))
    f.close()

    return lines


####    Logging


def make_log_path(podcast_name):
    """Makes a path for the log file"""
    path_without_dir = os.popen('pwd').read()
    path_without_dir = path_without_dir.strip()
    path = path_without_dir + '/logs/' + podcast_name

    return path


def add_to_log(urllist, podcast_name):
    """Makes a log entry in the file friendlypodder/logs/podcast_name"""
    ensure_dir('logs')
    path = make_log_path(podcast_name)
    if os.path.exists(path):
        f = open(path, 'a')
    else:
        f = open(path, 'w')
    for url in urllist:
        f.write('\n' + url)
    f.close()


def not_in_logs(urls, podcast_name):
    """Takes a list of urls and returns a list of the ones that are not in
    the logs"""
    ensure_dir('logs')
    path = make_log_path(podcast_name)
    # If there is no log file, return all the urls
    if not os.path.exists(path):
        return urls
    f = open(path, 'r')
    not_in_logs = []
    loglistpre = f.readlines()
    loglist = []
    for url in loglistpre:
        loglist.append(url.strip())
    for url in urls:
        if url not in loglist:
            not_in_logs.append(url)
    f.close()
    return not_in_logs


####    Downloading


def make_today_string():
    """Returns a string with YYYY-MM-DD"""
    import datetime
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d')


def download_file(url, podcast_name):
    """Downloads a file in a folder that are marked for today"""
    download_dir = make_today_string()
    ensure_dir(download_dir)
    download_with_progressbar(url, download_dir)
    # Need the two next because add_to_log wants a list as argument
    urllist = []
    urllist.append(url)
    add_to_log(urllist, podcast_name)


def ensure_dir(dirname):
    """makes sure that the dir dirname exists"""
    path_without_dir = os.popen('pwd').read()
    path_without_dir = path_without_dir.strip()
    path = path_without_dir + '/' + dirname
    if not os.path.exists(path):
        os.makedirs(dirname)


def download_rss(url):
    """Downloads the rss file and returns it as a list of strings"""
    return urllib2.urlopen(url)


def download_and_parse_rss(url):
    """Downloads the rss feed in the url and returns a list of podcast urls"""
    # Need to make a thread to have the spinner going while it downloads the
    # rss-feed
    thread.start_new_thread(spinner, ())
    rss = download_rss(url)
    medialist = parse(rss)
    # To get rid of the spinner
    return medialist



if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'catchup' or sys.argv == 'c':
            update_and_catch_up()
        elif sys.argv[1] == 'download' or sys.argv == 'd':
            update_and_download()
        else:
            print ''
            make_title('usage')
            print 'download (d) - Download new episodes'
            print 'catchup (c) - Catch up on episodes'
            print 'With no arguments download will be assumed'
            print ''
    else:
        update_and_download()
