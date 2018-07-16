#! /usr/bin/env python
"""
   Copyright 2016 The Trustees of University of Arizona

   Licensed under the Apache License, Version 2.0 (the "License" );
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os
import sys
import logging
import json
import grequests
import urlparse

logger = logging.getLogger('origin_server_setter.log')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
if os.path.exists('/var/log/squid3'):
    fh = logging.FileHandler('/var/log/squid3/origin_server_setter.log')
else:
    fh = logging.FileHandler('/tmp/origin_server_setter.log')
fh.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)


REPO_URL = "https://butler.opencloud.cs.arizona.edu/sdm/cdn_catalogue"


class RepositoryException(Exception):
    pass


class RepositoryEntryCDNSite(object):
    """
    repository entry - cdn site
    """
    def __init__(self, name, gps_loc, cdn_prefix):
        self.name = name
        self.gps_loc = gps_loc
        self.cdn_prefix = cdn_prefix

    @classmethod
    def from_dict(cls, ent):
        return RepositoryEntryCDNSite(
            ent["name"],
            ent["gps_loc"],
            ent["cdn_prefix"]
        )

    def to_json(self):
        return json.dumps({
            "name": self.name,
            "gps_loc": self.gps_loc,
            "cdn_prefix": self.cdn_prefix
        })

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "<RepositoryEntryCDNSite %s>" % \
            (self.name)


class RepositoryEntry(object):
    """
    repository entry
    """
    def __init__(self, dataset, ag_url, cdn_sites):
        self.dataset = dataset.strip().lower()
        self.ag_url = ag_url.strip()
        self.cdn_sites = cdn_sites

    @classmethod
    def from_json(cls, jsonstr):
        ent = json.loads(jsonstr)
        return cls.from_dict(ent)

    @classmethod
    def from_dict(cls, ent):
        cdn_sites = ent["cdn_sites"]
        cdn_sites_obj = []
        for cdn_site in cdn_sites:
            cdn_sites_obj.append(RepositoryEntryCDNSite.from_dict(cdn_site))

        return RepositoryEntry(
            ent["dataset"],
            ent["ag_url"],
            cdn_sites_obj
        )

    def to_json(self):
        return json.dumps({
            "dataset": self.dataset,
            "ag_url": self.ag_url,
            "cdn_sites": self.cdn_sites
        })

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "<RepositoryEntry %s %s>" % \
            (self.dataset, self.ag_url)


class Repository(object):
    """
    Manage CDN Repository
    """
    def __init__(self, url):
        self.table = {}

        if not url:
            raise RepositoryException("not a valid repository url : %s" % url)

        self.load_table(url)

    def load_table(self, url):
        self.table = {}
        try:
            req = [grequests.get(url)]
            res = grequests.map(set(req))[0]
            ent_arr = res.json()
            for ent in ent_arr:
                entry = RepositoryEntry.from_dict(ent)
                self.table[entry.dataset] = entry
        except Exception, e:
            raise RepositoryException("cannot retrieve repository entries : %s" % e)

    def get_entry(self, dataset):
        k = dataset.strip().lower()
        if k in self.table:
            return self.table[k]
        return None

    def list_entries(self):
        entries = []
        for k in self.table.keys():
            entries.append(self.table[k])
        return entries


def list_origin_servers():
    """
    List SDM origin servers (AGs)
    """
    repository = Repository(REPO_URL)
    entries = repository.list_entries()
    originservers = []
    for entry in entries:
        originservers.append((entry.dataset, entry.ag_url))

    return originservers


def make_nginx_conf():
    nginx_conf = []
    # origin servers
    originservers = list_origin_servers()
    for originserver in originservers:
        dataset, ag_url = originserver
        ag_url_parts = urlparse.urlparse(ag_url)
        ag_scheme = ag_url_parts.scheme
        ag_netloc = ag_url_parts.netloc
        nginx_conf.append("location /%s/ {" % (ag_netloc))
        nginx_conf.append("    rewrite ^/%s(/.*)$ $1 break;" % (ag_netloc))
        nginx_conf.append("    proxy_pass %s://%s;" % (ag_scheme, ag_netloc))
        nginx_conf.append("    proxy_set_header Host $http_host;")
        nginx_conf.append("    proxy_set_header X-Real-IP $remote_addr;")
        nginx_conf.append("    proxy_set_header X-Scheme $scheme;")
        # nginx_conf.append("    proxy_redirect off;")
        nginx_conf.append("}")

    return nginx_conf


def main(argv=None):
    nginx_conf = make_nginx_conf()
    for conf in nginx_conf:
        print conf


if __name__ == "__main__":
    main()
