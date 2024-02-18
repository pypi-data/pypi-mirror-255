[![License: AGPL-3](https://img.shields.io/badge/licence-AGPL--3-blue.png)](http://www.gnu.org/licenses/agpl-3.0-standalone.html)
[![Alpha](https://img.shields.io/badge/maturity-Mature-brightgreen.png)](https://odoo-community.org/page/development-status)

This project aims to be a odoo 12 addon that integrates a helpdesk for the main ODOO ERP's cooperatives according two their requirements.


### Installation

This package requires Odoo v12.0 installed.

You can install this module using `pip`:

```sh
$ pip install odoo12-addon-helpdesk-somitcoop
```

### DEVELOPMENT

#### Configure local development environment

First of all, to start to development, we need to create a virtualenv with python 3.7 in our local machine.

In your local environment, where you execute the `git commit ...` command, run:

1. Install `pyenv`
```sh
curl https://pyenv.run | bash
```
2. Build the Python version
```sh
pyenv install  3.8.13
```
3. Create a virtualenv
```sh
pyenv virtualenv 3.8.13 odoo-helpdesk
```
4. Activate the virtualenv
```sh
pyenv activate odoo-helpdesk
```
5. Install dependencies
```sh
pip install pre-commit
```
5. Install pre-commit hooks
```sh
pre-commit install
```

#### Set development enviornment (LXC Container)

Reuse a local odoo lxc container, or create a new one. Follow the [instructions](https://gitlab.com/coopdevs/odoo-somconnexio-inventory#requirements) in [odoo-somconnexio-inventory](https://gitlab.com/coopdevs/odoo-somconnexio-inventory).

To check our local lxc containers and their status, run:
```sh
$ sudo lxc-ls -f
```

Once we have decided where to put it, mount our development folder in it
```sh
lxc.mount.entry = /home/<user>/<path>/odoo-helpdesk/helpdesk_somitcoop /var/lib/lxc/<odoo-container>/rootfs/opt/odoo_modules/helpdesk_somitcoop none bind,create=dir 0.0
```

Once created, we can stop or start our lxc container as indicated here:
```sh
$ sudo systemctl start lxc@<odoo-container>
$ sudo systemctl stop lxc@<odoo-container>
```


#### Start the ODOO application

Enter to your local machine as the user `odoo`, activate the python enviornment first and run the odoo bin:
```sh
$ ssh odoo@<odoo-container>.local
$ pyenv activate odoo
$ cd /opt/odoo
$ set -a && source /etc/default/odoo && set +a
$ ./odoo-bin -c /etc/odoo/odoo.conf -u helpdesk_somitcoop -d odoo --workers 0
```

