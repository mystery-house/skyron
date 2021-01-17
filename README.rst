******************************
Skyron: A Python Gemini Server
******************************

Skyron is a straightforward `Gemini <https://gemini.circumlunar.space/>`_ 
Server that serves static files over a secure SSL/TLS connection.

The code in its current state was hacked together in a day, has not been 
 tested, is not multi-threaded, and is generally not recommended for use in 
 anything resembling a production environment.

Requirements
############

* Python 3.x
* An SSL Certificate. Officially, the Gemini client specification does not 
support connecting to servers using self-signed certificates, but as of 
early 2021 most clients are fairly lenient about it. If you go the self-signed
route you'll still need a Certificate Authority. `This guide <https://deliciousbrains.com/ssl-certificate-authority-for-local-https-development/>`_
will walk you through the entire process. If you already have a server with a 
domain pointed at it, you might consider just `using Letsencrypt <https://www.digitalocean.com/community/tutorials/how-to-use-certbot-standalone-mode-to-retrieve-let-s-encrypt-ssl-certificates-on-ubuntu-16-04>`
to get a real certificate. (And if you already have an SSL certificate for a
 web site on that server, you can just use that.)

Setup
#####
Until such time as a ``setup.py`` script is available, you can just grab a
copy of the code and run in-place. As of right now Skyron doesn't use
any third-party code, so you don't even have bother with a virtual 
environment.

1. Clone the repository::

    git clone https://github.com/tinpan-io/skyron.git

2. Make a copy of the settings file::

    cp example_settings.yaml settings.yaml

3. Customize your settings. Minimally you will need to change ``DOCUMENT_ROOT``
   (The directory that will contain your ``.gmi`` or ``.gemini`` Gemini markup
   files) and the three settings under SSL. 

.. important::
   The ``DOCUMENT_ROOT`` directory, its contents, and all three SSL files must be
   readable by whatever user will be running Skyron.

4. Add some content; have a look at `this overview <https://www.susa.net/wordpress/2020/06/gemini-protocol-markup/>`_ 
of Gemini markup, and make a page of your own in the directory you configured in
 ``DOCUMENT_ROOT``. Give it an extension of ``.gmi`` or ``.gemini``. As with
 most web servers, Skyron will look for an index file (``index.gmi``, or 
 whatever is configured in ``settings.yaml``) if a request URL points at a 
 directory instead of a specific file.

 5. If you intend to make the server accessible from the internet, you'll need
  to open port 1965 on your firewall to incoming requests.

Running Skyron
##############

From the top level of your checked out copy of the code, run::

    python server.py

You should see the message::

    Skyron 0.1 is now listening at 0.0.0.0:1965.

(Yours may be slightly different if you've changed your BIND or PORT settings.)
At this point you should be able to point a gemini client at 
``gemini://[hostname]`` (where ``[hostname]`` is the IP address or domain of
the server where you're running Skyron.

Etc.
####

I should reiterate again that this is not ready for prime time; use at your 
own risk and let me know if you find any glaring issues.

Skyron?
-------

Skyron is a nod to Monty Python's *Science Fiction* sketch, in which Blancmanges 
from planet Skyron in the Andromeda galaxy turn everyone on Earth into Scotsmen 
for the purpose of winning Wimbledon.