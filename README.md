aether-purrsist
===============

This is a Python tool designed to archive the content of *Aether*
communities (boards) in [IPFS](https://ipfs.tech).
[Aether](https://getaether.net/) is a peer-to-peer forums application.
The content in *Aether* is ephemeral (6 months by default).

It does not connect to the *Aether* network, but rather uses the
*Aether* SQLite database.
It produces a website that can be pinned to a remote IPFS pinning service,
as well as an Atom feed of all the Aether threads.

See [a demo here](https://bafybeiarckpnjohvpmpvmyivgvlzyme2fnmqh3nhcdske7lx6nxj5b7y7y.ipfs.dweb.link) ([Atom feed](https://bafybeiarckpnjohvpmpvmyivgvlzyme2fnmqh3nhcdske7lx6nxj5b7y7y.ipfs.dweb.link/atom.xml)) (sync date: *2023-06-25*).

Installation
------------

```sh
pip install .
```

Usage
-----

Copy the *config.yaml* file from the *examples* directory and
edit it if necessary. Then run it with the config path (otherwise
it will use the file named *config.yaml* in the current directory):

```sh
aether-purrsist -c config.yaml
```

Use *-v* to increase verbosity:

```sh
aether-purrsist -vv
```

The website's CID will be echoed after it's finished.

Configuration
-------------

The **ipfs.maddr** setting should be the multiaddr of your kubo's node
API endpoint.

The **ipfs.ipns_key** setting controls the name of the IPNS key
to which the website will be published.

To enable remote pinning, set *enabled* to *True* in the **ipfs.pinremote**
section of the YAML config file. The *service* setting should match the name
of the remote service as it's configured on your IPFS node. The *pin_name*
setting is passed to the remote pinning service as the pin name for the
archive.
