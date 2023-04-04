aether-purrsist
===============

[Aether](https://getaether.net/) is a P2P application (peer-to-peer forums).
The content in *Aether* is ephemeral (6 months by default).

This is a Python tool designed to archive the content of *Aether*
communities (boards) in [IPFS](https://ipfs.tech).

It does not connect to the *Aether* network, but rather uses the
*Aether* SQLite database.
It produces a website that can be pinned to a remote IPFS pinning service.

See [a demo here](https://bafybeid3ee2vzhivgac62vkixqhgdlrntsto52ojh7hx4daqj5m4pxbtny.ipfs.dweb.link).

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
