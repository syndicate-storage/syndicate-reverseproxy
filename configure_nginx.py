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


def replace_origin_servers(base_conf, origin_server_conf):
    origin_server_conf_str = '\n'.join(origin_server_conf)

    new_conf = []
    for conf_line in base_conf:
        new_conf.append(conf_line.replace('$ORIGIN_SERVERS$', origin_server_conf_str))

    return new_conf


def main(argv):
    if len(argv) != 2:
        print "command : ./configure_nginx.py conf_template origin_server_conf"
    else:
        base_conf_path = argv[0]
        origin_server_conf_path = argv[1]

        base_conf = []
        with open(base_conf_path, 'r') as base_conf_file:
            for line in base_conf_file:
                base_conf.append(line.replace('\n', ''))

        origin_server_conf = []
        with open(origin_server_conf_path, 'r') as origin_server_conf_file:
            for line in origin_server_conf_file:
                origin_server_conf.append(line.replace('\n', ''))

        squid_conf = replace_origin_servers(base_conf, origin_server_conf)
        for conf_line in squid_conf:
            print conf_line


if __name__ == "__main__":
    main(sys.argv[1:])
