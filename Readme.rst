.. image:: https://odevio.com/static/img/logo__odevio.svg
    :align: center
    :height: 200px
    :width: 100%

.. image:: https://img.shields.io/badge/status-deprecated-red

⚠️ **This project is no longer maintained.**

Thank you for your support — it’s been a great journey!

.. image:: https://img.shields.io/badge/version-1.2.2-blue
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

.. image:: https://img.shields.io/discord/945256030869258280?logo=discord
    :target: https://discord.gg/sCVTTsXbvE
    :alt: Discord

=======================================================================================
The easy way to setup, build & release flutter apps for iOS on Linux, Windows and MacOS
=======================================================================================
Odevio is a tool to help developers setup and release their Flutter apps on iOS.
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

-----
Usage
-----
To start using Odevio simply run :code:`odevio` in your console.

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
**Our mission is to reduce the time it takes to setup, build and release Flutter
apps on iOS to the bare minimum.**

The tool allows developers working alone or in teams and on
multiple OS (Linux, Windows, MacOS) to build and publish their apps easily
to the app store.

**What can Odevio be used for ?**

#. It allows you to setup the XCode project on a remote MacOS machine if you do not own one.
#. It manages common iOS specific settings for your team : certificates, devices, provisioning profiles, bundle IDs, Xcode configuration files, ...
#. It builds your Flutter app on remote iOS machines.
#. It hosts the iOS app artifacts or publish them to the App Store.

------------
Contributing
------------
Thank you for considering contributing to Odevio. The main purpose of this repository is to continue evolving Odevio to make Flutter developer's lives easier.

Please report improvements, bugs and issues to Github's issue tracker.
Pull requests linked to open issues are even more appreciated.

Odevio's GitHub issue tracker is not intended to provide help or support.
For that check out our `discord <https://discord.gg/sCVTTsXbvE>`_.

We are also thrilled to receive a variety of other contributions including:

* Documentation updates, enhancements, designs, or bugfixes.
* Spelling or grammar fixes.
* Blogging, speaking about, or creating tutorials about Odevio.

**Giving Odevio a Github star is much appreciated by our team ! Sharing our project with other Flutter developers is too :)**
