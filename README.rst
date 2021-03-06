``pufsim``
##########

``pufsim`` is a simulator frontend for ``puflib``. All Python 3.

Contributing
############

Email gschmi4@uic.edu if you want to contribute. You must only contribute code
that you have authored or otherwise hold the copyright to, and you must
make any contributions to this project available under the MIT license.

To collaborators: don't push using the ``--force`` option.

Dev Quickstart
##############

First clone, the repository into a location of your choosing:

.. code-block::

    $ git clone https://github.com/gregschmit/django-pufsim

Then you can go into the ``django-pufsim`` directory and do the initial
migrations and run the server (you may need to type ``python3`` rather than
``python``):

.. code-block::

    $ cd django-pufsim
    $ python manage.py makemigrations pufsim
    $ python manage.py migrate
    $ python manage.py runserver

The server should now be hosted at ``http://pufsim.schmit.net``.
