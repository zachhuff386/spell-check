spell_check
===========

Build
-----

C extension must be built before running.

.. code-block:: bash

    $ python2 setup.py build

Test
----

Spell check words from input.

.. code-block:: bash

    $ python2 test.py
    > sheeeeep
    run_time: 0.01638412
    matches: ['sheep', 'sheenie', 'sheeneys']

Test Google
-----------

Spell check words and compare with google from input.

.. code-block:: bash

    $ python2 test_google.py
    > cunsperricy
    run_time: 0.03902698
    matches: ['conspiracy']
    google_match: conspiracy

Test Server
-----------

Run test server to spell check words from web interface.

.. code-block:: bash

    $ python2 test_server.py
    Serving HTTP on 0.0.0.0 port 8500...
    # Open http://localhost:8500/
