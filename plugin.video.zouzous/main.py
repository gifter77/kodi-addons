# -*- coding: utf-8 -*-
# Module: default
# Author: Gifter
# Created on: 24.01.2016
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import urllib
import urllib2
import re
import itertools

def repl(m):
    return m.group().lower().encode('ascii', 'strict').decode('unicode-escape')

def fix_accents(s):
    return re.sub(r'\\u[0-9a-f]{4}', repl, s)

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

# Free sample videos are provided by www.vidsplay.com
# Here we use a fixed set of properties simply for demonstrating purposes
# In a "real life" plugin you will need to get info and links to video files/streams

VIDEOS = {}

def get_soup(url):
    req  = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0.1')           
    soup = urllib2.urlopen(req).read()
    #if (self.debug_mode):
    #    print str(soup)
    return soup

def get_episodes():
    soup = get_soup("http://www.zouzous.fr/videos")
    src   = re.findall("""jQuery.extend\(Drupal.settings, (.+?)\);""",soup)
    #print src[0]
    data = src[0].replace("null","None").replace("false","False").replace("true","True")
    #print data
    l = eval(data)
    #videos_list = sorted(l['videos_replay']['data'], key=lambda k: k['hero_title'])
    videos_list = sorted(l['videos_replay']['data'] + l['videos_bonus']['data'], key=lambda k: k['hero_title'])

    global VIDEOS

    for k, g in itertools.groupby(videos_list, lambda x: fix_accents(" ".join(x['hero_title'].split())).title()):
        VIDEOS[k] = list(g)

def get_url(id):
    #soup = get_soup("http://webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion={0}&catalogue=Pluzz&callback=webserviceCallback_{0}".format(id))

    soup = get_soup("http://sivideo.webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion={0}&catalogue=Zouzous_web&callback=_jsonp_loader_callback_request_0".format(id))
    #print soup
    #src   = re.findall("webserviceCallback_%d\((.+?)\)"%id,soup)
    src   = re.findall("_jsonp_loader_callback_request_0\((.+?)\)",soup)
    data = src[0].replace("null","None").replace("false","False").replace("true","True")
    l = eval(data)
    for e in l['videos']:
        if e['format'] == 'm3u8-download':
            return e['url'].replace("\\","")

def get_categories():
    """
    Get the list of video categories.
    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or server.

    :return: list
    """
    return VIDEOS.keys()


def get_videos(category):
    """
    Get the list of videofiles/streams.
    Here you can insert some parsing code that retrieves
    the list of videostreams in a given category from some site or server.

    :param category: str
    :return: list
    """
    #print category
    global VIDEOS
    return VIDEOS[category]


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Get video categories
    categories = get_categories()
    # Create a list for our items.
    listing = []
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category, thumbnailImage=VIDEOS[category][0]['image'])
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        print VIDEOS[category][0]['image']
        list_item.setArt({'thumb': VIDEOS[category][0]['image'].replace("\\",""),
                          'icon': VIDEOS[category][0]['image'].replace("\\",""),
                          'fanart': VIDEOS[category][0]['image'].replace("\\","")})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # http://mirrors.xbmc.org/docs/python-docs/15.x-isengard/xbmcgui.html#ListItem-setInfo
        list_item.setInfo('video', {'title': category, 'genre': category})
        # Create a URL for the plugin recursive callback.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = u'{0}?action=listing&category={1}'.format(_url, category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the listing as a 3-element tuple.
        listing.append((url, list_item, is_folder))
    # Add our listing to Kodi.
    # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
    # instead of adding one by ove via addDirectoryItem.
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: str
    """
    # Get the list of videos in the category.
    videos = get_videos(category)
    # Create a list for our items.
    listing = []
    # Iterate through videos.
    for video in videos:
        title = fix_accents(video['title'])
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=title)
        # Set additional info for the list item.
        list_item.setInfo('video', {'title': title})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['image'].replace("\\",""), 'icon': video['image'].replace("\\",""), 'fanart': video['image'].replace("\\","")})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for the plugin recursive callback.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
        #url = u'{0}?action=play&video={1}'.format(_url, get_url(video['id']))
        url = u'{0}?action=play&video={1}'.format(_url, video['id'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the listing as a 3-element tuple.
        listing.append((url, list_item, is_folder))
    # Add our listing to Kodi.
    # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
    # instead of adding one by ove via addDirectoryItem.
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring:
    """
    get_episodes()
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(get_url(params['video']))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        #print VIDEOS
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
