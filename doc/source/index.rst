..
      Copyright 2011 OpenStack, LLC.
      All Rights Reserved.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

Welcome to LBaaS's documentation!
===================================

LBaaS (Load Balancer as a Service) is a
service that allows to manage multiple hardware and software-based
load balancers in an OpenStack cloud environment using a RESTful API,
and to provide LB services to OpenStack tenants. It is designed specifically for
OpenStack, but can also be used as a standalone service to manage a set of
load balancers via a single unified API.

Using LBaaS
==============

Initial Setup
---------------

Create virtualenv that required for executing code and tests: ::

 # cd openstack-lbaas
 # ./run_tests -V -f

Note, virtualenv needs to be updated any time code dependencies are changed. Virtualenv is created in .venv folder

Initialize database: ::

 # ./.venv/bin/python bin/balancer-api --dbsync

The database is located in balancer.sqlite

Run and Test
---------------

Run LBaaS: ::

  # ./.venv/bin/python ./bin/balancer-api --config-file etc/balancer-api-paste.ini --debug

By default the server is started on port 8181

Developer Docs
==============

.. toctree::
   :maxdepth: 1

   devref/driver
   devref/api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

