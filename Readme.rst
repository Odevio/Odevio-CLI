.. image:: https://odevio.com/static/img/logo__odevio.svg
    :align: center
    :height: 200px
    :width: 100%

.. image:: https://img.shields.io/badge/version-1.3.0-blue
    :target: https://github.com/Odevio/Odevio-CLI/

.. image:: https://img.shields.io/github/license/odevio/odevio-cli
    :target: https://github.com/Odevio/Odevio-CLI/blob/master/LICENSE

.. image:: https://img.shields.io/librariesio/release/pypi/odevio
    :target: https://pypi.org/project/odevio/

.. image:: https://img.shields.io/pypi/dm/odevio
    :target: https://pypi.org/project/odevio/

.. image:: https://img.shields.io/uptimerobot/ratio/m792431382-e51d8a06926b56c359afe3b7
    :target: https://stats.uptimerobot.com/QqN9MFXvw3
    :alt: UptimeRobot

.. image:: https://www.codefactor.io/repository/github/odevio/odevio-cli/badge
   :target: https://www.codefactor.io/repository/github/odevio/odevio-cli
   :alt: CodeFactor

======================================================================
Build and publish iOS apps with your AI agent — no Mac, no iOS jargon
======================================================================
Odevio lets an AI agent build and publish your iOS apps for you. It runs the build and signing on
remote Macs, so you need no Mac, no Xcode and no iOS knowledge. Claude Code is the first AI agent
supported.
Thanks for checking it out.

.. figure:: https://raw.githubusercontent.com/Odevio/Odevio-CLI/master/docs/img/odevio--demo.gif
    :align: center

    **A tool for developers by developers**

------------
Installation
------------
Odevio is a CLI utility developed in Python. It is easily installed with
pip.

.. code-block::

    pip install odevio

-------------------------
Use it with an AI agent
-------------------------
The way to use Odevio is to let your AI agent drive it. Install the skill once (this sets up Claude Code,
the first AI agent supported):

.. code-block::

    odevio skill install

Then, in your Flutter project, just ask your agent to put your app on your iPhone. It writes the code,
Odevio builds and signs it on a real Mac, fixes what breaks, and ships it to TestFlight. See the
`AI agent guide <https://odevio-cli.readthedocs.io/en/latest/ai_assistant/index.html>`_.

----------------------
Use the CLI yourself
----------------------
Prefer to drive Odevio directly? To start using Odevio simply run :code:`odevio` in your console.

Start by creating an account

.. code-block::

    odevio signup

Your Odevio account is now created and you can either start a build machine in configuration mode : to configure XCode or test your app in the iOS simulator.

.. code-block::

    odevio build start --build-type configuration


Or you can build an IPA or release your app by linking your Apple Developer Account to Odevio and creating an app identifier

.. code-block::

    odevio apple add --apple-id APPLE_TEAM_ID --name TEXT --key-id APPLE_KEY_ID --issuer-id APPLE_ISSUER_ID --private-key LOCATION_APPLE_PRIVATE_KEY
    odevio app mk --name MY_APP_NAME --bundle-id COM.COMPANY.APP_NAME

To create the IPA to install on a physical device for testing purposes

.. code-block::

    odevio build start --build-type ad-hoc
    odevio build ipa

To publish directly to the App Store

.. code-block::

    odevio build start --build-type publication

Your build failed ? No worries, you can check the logs with

.. code-block::

    odevio build logs

-------------
Documentation
-------------
All documentation is in the :code:`docs` directory and online at https://odevio-cli.readthedocs.io/.
If you are getting started this is how we recommend you use the docs :

* First read our `installation instructions <https://odevio.readthedocs.io/en/master/installation/index.html>`_.
* Next, check how to `setup your app with Odevio at and build your Flutter app to iOS <https://odevio.readthedocs.io/en/master/tutorial/index.html>`_ .
* Finally, if you want to know every option Odevio has to offer check our `reference guide <https://odevio.readthedocs.io/en/master/reference_guide/index.html>`_

-----
About
-----
**Our mission is to let anyone build and publish an iOS app through an AI agent, without owning a Mac
or knowing the iOS ecosystem.**

Odevio gives your AI agent the tools to build and ship iOS apps for you.

**What does Odevio do for you ?**

#. It lets an AI agent such as Claude Code drive the whole flow from plain-language requests.
#. It manages iOS specifics — certificates, devices, provisioning profiles, bundle IDs, Xcode configuration.
#. It builds your Flutter app on remote Macs, so you need no Mac of your own.
#. It fixes build failures, then hosts the app or ships it to TestFlight and the App Store.

------------
Contributing
------------
Thank you for considering contributing to Odevio. The main purpose of this repository is to continue evolving Odevio to make Flutter developer's lives easier.

Please report improvements, bugs and issues to Github's issue tracker.
Pull requests linked to open issues are even more appreciated.

Odevio's GitHub issue tracker is not intended to provide help or support.
For that, see the `documentation <https://odevio-cli.readthedocs.io/>`_.

We are also thrilled to receive a variety of other contributions including:

* Documentation updates, enhancements, designs, or bugfixes.
* Spelling or grammar fixes.
* Blogging, speaking about, or creating tutorials about Odevio.

**Giving Odevio a Github star is much appreciated by our team ! Sharing our project with other Flutter developers is too :)**
