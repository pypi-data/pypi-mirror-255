=========
societies
=========

Societies is a collection of abstract models for building django apps that deal with people, places, events and means of communication.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "societies" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "societies",
    ]


2. To use societies, import and subclass the relevant model classes.
3. Add extra model fields as needed.
4. subclass the Meta class as needed.
