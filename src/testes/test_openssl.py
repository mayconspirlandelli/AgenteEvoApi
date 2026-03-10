import ssl
import flask
import requests
print("SSL Version:", ssl.OPENSSL_VERSION)
print("Flask Version:", flask.__version__)
print("Requests Version:", requests.__version__)
print("OpenSSL Check OK")
