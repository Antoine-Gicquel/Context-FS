# Context-FS
Easily add context to your wordlists !

## Installation

```
sudo apt install libfuse-dev
sudo apt install pkg-config libfuse3-dev
pipx install git+https://github.com/Antoine-Gicquel/Context-FS.git
```

## Usage

```
$ ctxfs.py --help
usage: ctxfs.py [-h] origin mountpoint

positional arguments:
  origin      Folder to wrap with context
  mountpoint  Directory to mount the wrapping filesystem

options:
  -h, --help  show this help message and exit
```

## Example

TODO an example with SecLists

```
# With SecList cloned at /opt/SecLists
$ ctxfs.py /opt/SecLists /tmp/ctx-SecLists &
$ echo "company" > /tmp/ctx-SecLists/context
$ echo "company2024" > /tmp/ctx-SecLists/context
$ echo "appname" > /tmp/ctx-SecLists/context
$ echo "appname_company" > /tmp/ctx-SecLists/context
$ cat /tmp/ctx-SecLists/wrapped/Discovery/Web-Content/common.txt | head -n 10
company
company2024
appname
appname_company
.bash_history
.bashrc
.cache
.config
.cvs
.cvsignore
```
