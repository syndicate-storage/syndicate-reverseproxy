#! /bin/bash
#   Copyright 2016 The Trustees of University of Arizona
#
#   Licensed under the Apache License, Version 2.0 (the "License" );
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

NGINX_CONF_ORIGIN_SERVER=/tmp/nginx_conf_origin_server
NGINX_CONF_SDM_TEMPLATE=/tmp/sdm_reverseproxy.conf.template
NGINX_CONF_SDM_AVAILABLE=/etc/nginx/sites-available/sdm_reverseproxy.conf
NGINX_CONF_SDM_ENABLED=/etc/nginx/sites-enabled/sdm_reverseproxy.conf

origin_server_setter.py > ${NGINX_CONF_ORIGIN_SERVER}
configure_nginx.py ${NGINX_CONF_SDM_TEMPLATE} ${NGINX_CONF_ORIGIN_SERVER} >| ${NGINX_CONF_SDM_AVAILABLE}
ln -s ${NGINX_CONF_SDM_AVAILABLE} ${NGINX_CONF_SDM_ENABLED}

echo "Run nginx..."
nginx -g 'daemon off;'
