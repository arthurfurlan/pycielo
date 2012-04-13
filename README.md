PyCielo
=======

Python library to consume Cielo's WebService


Usage
-----

First of all, check the Cielo's Documentation (portuguese only): http://va.mu/Twoa

    c = Cielo('<vendor-num>', '<vendor-key>')
    c.request_transaction_id()
    a = c.request_customer_authorization()
    ## to be done
