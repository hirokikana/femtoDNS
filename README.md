femtoDNS
==
femtoDNS is very small DNS server written in Python.

## Description
femtoDNS have no benefit because purpose in learn DNS protocol.
This implemented by RFC 1035

## Requirement
 - Python 3.7>

## Usage
Run DNS server localhost:9999
```
$ python start.py
```

Any request query to femtoDNS using dig
```
$ dig +short @127.0.0.1 localhost
127.0.0.1
```
**!!Resolve only localhost in currently!!**

## Licence
[MIT]()
