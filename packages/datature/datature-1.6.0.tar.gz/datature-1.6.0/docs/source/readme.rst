
Datature Python SDK V2
=============================================================

Official library to manage datasets along with
`Datature Nexus <https://www.datature.io/nexus>`_.

Get Started
=============================================================

Python >= 3.8, <=3.11.

Installation
----------------------

.. code-block::

   pip install datature


Authentication
----------------------
The first step that is essential to all requests is to ensure that you log on to the platform, access the relevant project, and store the project secret which can be found in API Management. For more detail on the project key and secret key, check out this link for more information.

Once you have the project secret, you will now be able to make API requests using the Python SDK by setting this:

.. code-block::

   from datature.nexus import Client
   client = Client("secret_key")


Set logging level:

.. code-block::
   
   import logging

   logging.basicConfig()
   logging.getLogger("nexus").setLevel(logging.DEBUG)

To see all possible functions as well view the required inputs and expected outputs, check our following documentation!
