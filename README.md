# NCD

Pure python library for reading the ncd file format. See the NCD rust package for details and tools to build NCD files.

https://github.com/ens-ds23/ncd

NCD is a format for doing occasional, one-off lookups of a bdm-like format over the network and without a server. It is
very much optimised for latency not bandwidth and so focuses on issuing the minimum _number_ of at-least vaguely 
sensibly sized requests, The files are built offline as one-off operations and are not designed for dynamic update.
Applications include lookup and identifier resolution for large network-served datasets, but the exact combination
of requirements for which NCD is optimal are probably rather niche.

NCD expands to Netword Constant Database as the design was heavily influenced bj Dan Bernstein's Constant Database (cdb).

Install this package with

pip install git+https://github.com/ens-ds23/ncd-python.git

Note that you will need a recent version of pip to install this package.
