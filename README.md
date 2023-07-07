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

See [a demo here](https://bafybeibjnqcvir4ec2hjju3wjvy754vydaqfwzj3tyz2yxjt32xv57ig3i.ipfs.dweb.link) ([Atom feed](https://bafybeibjnqcvir4ec2hjju3wjvy754vydaqfwzj3tyz2yxjt32xv57ig3i.ipfs.dweb.link/atom.xml)) (sync date: *2023-07-07*).

# Installation

```sh
pip install .
```

# Usage

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

# Configuration

The **ipfs.maddr** setting should be the multiaddr of your kubo's node
API endpoint.

The **ipfs.ipns_key** setting controls the name of the IPNS key
to which the website will be published. If you change the IPNS key name,
you will **lose** any *Aether* threads that had already been previously
archived by *aether-purrsist*, therefore don't edit this setting unless
it's the first time you run it.

To enable remote pinning, set *enabled* to *True* in the **ipfs.pinremote**
section of the YAML config file. The *service* setting should match the name
of the remote service as it's configured on your IPFS node. The *pin_name*
setting is passed to the remote pinning service as the IPFS pin name for the
archive. Before pinning to the remote service, any previous archive with
this *pin_name* will be deleted (unpinned).

## Boards sync config

Each *Aether* board that you want to archive should be listed in the
*boards* section.

```yaml
boards:
  AskAether:
    threads_ignore_byname:
      - 'dead'
  music:
    fingerprint: 6b38e6d4ccd61cc8cbdb11465e9d45abf0db4cd502b7b1b987fe7d1e624772f9
```

Sync options:

- *max_threads*: Maximum number of threads to archive (integer, default is 0,
    unlimited)
- *threads_ignore_byname*: a list of regular expressions that will be matched
    against the *Name* of each thread of this sub. If one of the regexps
    matches, this thread won't be archived
- *fingerprint*: Specify the exact fingerprint of the sub. The reason for this
    option is that board names in *Aether* are not unique (only fingerprints
    are). If you know the board's fingerprint (can be found in the sub's *Info*
    in the UI), you can set it here.
