# -*- coding: utf-8 -*-
import urllib
import urllib2
import re
#from lxml import html
#from xml.etree import ElementTree

def repl(m):
    return m.group().lower().encode('ascii', 'strict').decode('unicode-escape')

def fix_accents(s):
    return re.sub(r'\\u[0-9a-f]{4}', repl, s).replace("&#039;","\'")

def get_soup(url):
    req  = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0.1')           
    soup = urllib2.urlopen(req).read()
    #if (self.debug_mode):
    #    print str(soup)
    return soup

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
        
def build_heros_list():
    page = get_soup("http://www.zouzous.fr/")
    #tree = html.fromstring(page)

    #heros_ids = tree.xpath('//li[@class="Hero"]/@data-hero-id')
    #heros_icon = tree.xpath('//img[@class="Hero__Icon"]/@src')
    #heros_name = map(lambda x : fix_accents(x),tree.xpath('//img[@class="Hero__Icon"]/@title'))

    heros_ids = re.findall('data-hero-id="(.*)">',page)
    heros_icon, heros_name = zip(*re.findall('<img class="Hero__Icon" src="(.*)" alt="(.*)" title',page))
    heros_name = map(lambda x : fix_accents(x), heros_name)

    #print heros_ids
    #print heros_icon
    #print heros_name

    videos_list = {}

    for i in range(len(heros_ids)):
        hid = heros_ids[i]
        icon = heros_icon[i].replace("88x88","vignette")
        name = heros_name[i]
        videos_list[hid] = {'name': name, 'icon': icon, 'episodes': None}
        
    return videos_list

def build_episodes_list(hid):
    soup = get_soup("http://www.zouzous.fr/heros/%s/playlist?limit=100&offset=0"%hid)
    data = soup.replace("null","None").replace("false","False").replace("true","True")
    l = eval(data)
    return l["items"]

if __name__ == "__main__":

    get_heros_list()
