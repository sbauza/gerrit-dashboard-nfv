===============================
gerrit-dashboard-nfv
===============================

Gerrit automated dashboard for NFV subteam, scratching from a Wikipage.

* Free software: Apache license
* Documentation: TBD :-)
* Source: https://github.com/sbauza/gerrit-dashboard-nfv
* Bugs: https://github.com/sbauza/gerrit-dashboard-nfv/issues


Installation notes
------------------

- feel free to create a virtualenv
- Pip 1.4.1 or Pip 1.5 with --allow-external and --allow-unverified
- pip install -r requirements.txt
- python setup.py install


Configuration
-------------

A sample configuration can be found in etc/scrapnfving.conf.sample

Dashboard can be edited in etc/nfv.dash or you can create your own dash and
modify dashboard_name value in scrapnfving.conf

Usage
-----

nfvscraper --config-dir <location_of_repo>/etc

You can also copy files in etc/ into /etc/scrapnfving and only run :
nfvscraper


Features
--------

* TODO