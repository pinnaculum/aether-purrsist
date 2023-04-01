aether-purrsist
===============

[Aether](https://getaether.net/) is a P2P application (peer-to-peer forums).
The content in *Aether* is ephemeral (6 months by default).

This is a Python tool designed to archive the content of *Aether*
communities (boards) in [IPFS](https://ipfs.tech).

It does not connect to the *Aether* network, but rather uses the
*Aether* SQLite database.
It produces a website that can be pinned to a remote IPFS pinning service.

See [a demo here](https://bafybeicf4e3pegkyakiirhjhonczuiwm4u5slmgput7qnghmebrz7gyr5u.ipfs.dweb.link/bfa2ec06014ddd3a1a57e4ef5df2f102d28497ad0b3368d4887dd391768ee355/).

Installation
------------

```sh
pip install .
```

Usage
-----

Copy the *config.yaml* file from the *examples* directory and
edit it if necessary. Then run it with the config path:

```sh
aether-purrsist -c config.yaml
```

The website's CID will be echoed after it's finished.
