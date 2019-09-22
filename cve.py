# coding: utf-8
'''this script is originally from https://gist.github.com/mountainstorm/d6baecf3cd4c500cdcc6
Thanks to the author.

This is a simple script to download an NVD CVE feed, extract interesting bits
from the XML and import/update a mongo db - or optionally print it to screen

warning the xml file that this script uses will be deprecated by NVD on October2019'''
from __future__ import unicode_literals, print_function

import zipfile
import urllib2
import argparse
import cStringIO
import xml.etree.ElementTree as ET
import pprint


NVD_FEEDS = {
    'recent': 'https://nvd.nist.gov/feeds/xml/cve/nvdcve-2.0-Recent.xml.zip',
    'modified': 'https://nvd.nist.gov/feeds/xml/cve/nvdcve-2.0-Modified.xml.zip',
    'year': 'https://nvd.nist.gov/feeds/xml/cve/nvdcve-2.0-%s.xml.zip'
}


NAMESPACE = '{http://scap.nist.gov/schema/feed/vulnerability/2.0}'
VULN = '{http://scap.nist.gov/schema/vulnerability/0.4}'
CVSS = '{http://scap.nist.gov/schema/cvss-v2/0.2}'


def download_nvd_feed(req_feed):
    retval = None
    # download the feed
    feed = None
    if req_feed in NVD_FEEDS and req_feed != 'year':
        feed = NVD_FEEDS[req_feed]
    else:
        try:
            feed = NVD_FEEDS['year'] % int(req_feed)
        except ValueError:
            pass # not a number
    if feed is not None:
        print('info: downloading %s' % feed)
        retval = cStringIO.StringIO(urllib2.urlopen(feed).read())
    return retval


def get_nvd_feed_xml(req_feed, callback):
    retval = {}
    try:
        feed = download_nvd_feed(req_feed)
        try:
            zip = zipfile.ZipFile(feed)
            names = zip.namelist()
            for name in names:
                try:
                    f = zip.open(name)
                    retval.update(callback(f))
                finally:
                    f.close()
        finally:
            zip.close()
    finally:
        if feed:
            feed.close()
    return retval


def process_nvd_20_xml(xml):
    retval = {}
    tree = ET.parse(xml)
    root = tree.getroot()
    for entry in root.findall(NAMESPACE + 'entry'):
        cveid = entry.attrib['id']
        if cveid not in retval:
            cve = { '_id': cveid }
            summary = entry.find(VULN + 'summary')
            if summary is not None and summary.text:
                cve['summary'] = summary.text

            cve['published'] = entry.find(VULN + 'published-datetime').text
            cve['modified'] = entry.find(VULN + 'last-modified-datetime').text
            
            vsw = entry.find(VULN + 'vulnerable-software-list')
            if vsw is not None:
                products = []
                for sw in vsw.iter(VULN + 'product'):
                    products.append(sw.text)
                cve['products'] = products

            try:
                cvss = entry.find(VULN + 'cvss')
                base_metrics = cvss.find(CVSS + 'base_metrics')
                cve['cvss_score'] = base_metrics.find(CVSS + 'score').text
            except AttributeError:
                pass

            references = []
            for refs in entry.iter(VULN + 'references'):
                ref = refs.find(VULN + 'reference')
                if ref is not None and 'href' in ref.attrib:
                    href = ref.attrib['href'] 
                    text = ref.text
                    if href is not None:
                        if text is None:
                            text = href
                        references.append({ 'href': href, 'description': text })
            if len(references):
                cve['references'] = references
            retval[cveid] = cve
    return retval


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Download and process VND feeds')
    parser.add_argument('--feed', default='recent',
        help='"recent" the default, "modified" or a year e.g. 2015'
    )
    parser.add_argument('--debug', default=False, action="store_true",
        help='display parsed records, rather than import into mongo'
    )
    parser.add_argument('--dbaddr', default='localhost:27017',
        help='address of mongodb in format: "127.0.0.1:27017"'
    )
    parser.add_argument('--dbname', default='nvd',
        help='name of mongo database, default: "nvd"'
    )
    parser.add_argument('--dbcollection', default='cves',
        help='name of mongo collection, default: "cves"'
    )
    args = parser.parse_args()

    cves = get_nvd_feed_xml(args.feed, process_nvd_20_xml)
    if args.debug:
        pprint.pprint(cves)
    else:
        # try:
        from pymongo import MongoClient
        host, port = args.dbaddr.split(':')
        client = MongoClient(host, int(port))
        cves_collection = client[args.dbname][args.dbcollection]
        for cve in cves.values():
            cves_collection.update_one(
                { '_id': cve['_id'] }, { '$set': cve }, True
            )
        # except ImportError:
        #     pass