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

To resolve any hostname, you need host file add IP address / hostname pair.
host file is exists in current directory.

Example: 
```
127.0.0.1	localhost
127.0.0.1	test
```

## Licence
[MIT]()
