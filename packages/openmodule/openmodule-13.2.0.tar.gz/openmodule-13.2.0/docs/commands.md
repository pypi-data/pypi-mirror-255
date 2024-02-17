# Openmodule Commands

[TOC]

We provide multiple commands that are helpful for developing openmodule services.

## Create new commands

Creating new commands is very simple:
1. Add a new function to `openmodule_commands/__init__.py`
2. Register the command in `openmodule_commands/setup.cfg`
  * The commands should start with `openmodule_`
  * e.g. `openmodule_<command_name>=openmodule_commands:<function>`

## Translations

Commands for creating translations, for more info see [here](translation.md)
* **openmodule_makemessage:** Creates the translation files and opens an editor for translating
* **openmodule_translate:** Opens an editor for translating
* **openmodule_checktranslation:** Checks if the translations are up-to-date and if any translations are empty