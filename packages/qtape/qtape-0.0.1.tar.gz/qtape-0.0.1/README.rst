""""""""""""
qtape README
""""""""""""

.............................................................
A python package for (quantum) time adaptive phase estimation
.............................................................

There will be a preprint soon that explains the method! This package
provides a python API to an efficient C++ implementation. The python
API does not provide much documentation, it just exposes the
underlying C++ class methods in src/qtape/ctape.h and
src/qtape/ctape.cpp. Documentation for ctape.h is provided
therein. Doxygen documentation is available at:

https://polybox.ethz.ch/index.php/s/UdFEQB9JrQJD5en

To view the docs, download and unzip the file from the link, and then
open html/index.html in your browser.

============
Installation
============

``python3 -m pip install qtape``

=======
Example
=======

For a simple example see

examples/simple_ex.py
