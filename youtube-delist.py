#!/usr/bin/python3
# -*- coding: utf-8 -*-
''' Extract video urls from short Youtube playlist, save to videolist.txt at current directory (CANNOT scroll down for more)
    Required playstlist format: (https://www.)youtube.com/playlist?list=listID
    There is currently no way to validate a correctly formmated url based Google API, so the user should make sure the link points to the right video list.

    Required packages: requests, BeautifulSoup

    Copyright: The MIT License
    Author: knightReigh, May 2018
'''

import requests
from bs4 import BeautifulSoup
import re
import sys
import json
import os

def clean_script_string(unprocessed):
    start_strip = re.compile("window\[\"ytInitialData\"\] =")
    post_strip = re.compile("window\[\"ytInitialPlayerResponse\"\]")

    re1 = start_strip.split(unprocessed)[1]
    re2 = post_strip.split(re1)[0]
    re2 = re2.strip()[:-1]

    return re2

def api_request(uri):
    headers = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}

    try:
        r = requests.get(uri, headers=headers)

        if r.status_code != 200:
            print("Url request error: status_code " + r.status_code)
            print("Please make sure the url is a valid youtube playlist.")

        html = BeautifulSoup(r.text, "html5lib")
    except requests.ConnectTimeout as e:
        print(e)
        sys.exit(1)

    return html

def format_playlist_url(url):
    if "youtube.com/playlist?list=" not in url:
        print("Not a valid Youtube playlist url: " + url)
        print("Required format: www.youtube.com/playlist?list=listID")
        sys.exit(0)

    if url.startswith("www.youtube.com"):
        url = "https://" + url
    elif url.startswith("youtube.com"):
        url = "https://www." + url

    print("Re-formatted playlist url: " + url)
    return url

def main():
    # make html requests to grab html
    uri = input("Please enter Youtube playlist url: ")
    print()
    url = format_playlist_url(uri)
    html = api_request(url)

    # extract <script> initialData section
    scripts = html.findAll("script")
    found = None
    for _script in scripts:
        if "window[\"ytInitialData\"]" in _script.text:
            found = _script.text

    if not found:
        print("Something is wrong with the playlist. There is no video data in HTML. Please check the url.")
        sys.exit(1)

    # process html to json
    d = json.loads(clean_script_string(found))
    videolist = (d["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]
                    ["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]
                    ["itemSectionRenderer"]["contents"][0]
                    ["playlistVideoListRenderer"]["contents"])

    # output list
    f = open("videolist.txt", "w", encoding="UTF-8")
    index = 1
    for video in videolist:
        if "Deleted video" in str(video["playlistVideoRenderer"]["title"]):
            print("Video deleted")
            continue
        title = video["playlistVideoRenderer"]["title"]["simpleText"]
        full_url = video["playlistVideoRenderer"]["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"]
        matches = re.split(r"&", full_url)
        short_url = "https://www.youtube.com" + matches[0] + "&" + matches[1]
        f.write(short_url + os.linesep)
        print(str(index) + ", " + title + ": " + short_url)
        index += 1
    print()
    print("Extracted %s videos" % len(videolist))
    print("File written to videolist.txt @ " + os.getcwd())
    f.close()

if __name__ == "__main__":
    main()
