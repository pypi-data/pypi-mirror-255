# Translation

[TOC]

We now support a translation framework for openmodule.
Currently only the 2 langauges `en` and `de` are suppported in the framework.

## Setup

For translation you need to specify the directory `LOCALE_DIR` where the translation files are. 
The default language `LANGUAGE` is also relevant, as all marked strings will be automatically translated into this language.


## Handling translations

### Simple translation

If you want to create_translation a certain string, you have to mark it for translation. This happens with the provided method `_`.
This method also automatically translates the string in the default language (settings.LANGUAGE).

```python
from openmodule.utils.translation import _

text = _("translate me") # -> text = "translated"
```

### Simple marking

If you want to mark a string for translation, but need the untranslated string for further processing, you can use the provided method `___`.
E.g. you want to save a string in da database and translate it later in various languages.

```python
from openmodule.utils.translation import ___, _

text = ___("translate me") # -> text = "translate me"
translated = _(text) # -> translated = "translated"
```


### Handling message kwargs

It is also possible to create translation strings with message kwargs. For this you need to design the message with format kwargs.
Keep in mind, that you then may also need to translate the kwargs. There is also an example for how to translate enum.

```python
from openmodule.utils.translation import _

text = _("The gate is {gate}").format(gate="gate1")
text = _("The gate type is: {gate}").format(gate=_("entry"))

class SomeEnum(str, Enum):
    some_value1 = ___("some_value1")
    some_value2 = ___("some_value2")

text = _("Enum value is: {value}").format(value=_(SomeEnum.some_value1))
```

### Plural

It is also possible to translate messages with plural forms in them. For this use the provided method `__`. This only works with a **single** value in plural form. 
For the translation, the singular form will only be taken if the number **equals 1** or we do not have the translation, else the plural will be taken.
```python
from openmodule.utils.translation import __

def print_text(num):
    print(__("I have {num} apple", "I have {num} apples", num).format(num=num))

print_text(1) # I have 1 apple
print_text(2) # I have 2 apples
```


### Translating in different languages

You can also create_translation the string in any desired language, given the translation for this language exists. Here you need to take care, because you always need to translate the english text.


```python
from openmodule.utils.translation import _, ___, translate

text = translate("translate me", "en") # may differ if translated (e.g. fix typo only in translation)

# take care of language
text = translate(___("translate me"), "en") # working
text = translate(_("translate me"), "en") # not working, _() may return german text
```


## Creating the translation files

The openmodule framework provides an easy method to create translation files and translate them.

### Requirements
* poedit
* gettext

### Creation

If you have installed an openmodule version with translations, you can use the command `openmodule_makemessages`.
This will by default create translation files from the folder `src` and output it to `docker/translation`.
It further assumes that you are in the root directory of your service (a `src` folder and a `docker` folder are present).
You can change every settings, see `openmodule_makemessages --help`

```bash
openmodule_makemessages 
# commit changes
openmodule_checktranslation
```


The framework will also provide 2 special keywords for translation: 
* `__READABLE_NAME`: A readable name of the openmodule service
* `__DESCRIPTION`: A description of the openmodule service

These 2 strings **must** be translated in **all** languages. All other strings can only be translated in non-english languages.

**Note:** for some projects, e.g hardware info package without code, you may need to specify the options `--force-dir --files` (skip directory check and do not take any files for translation)


During the creation of translation files, a translation program `poedit` will be automatically opened for every language.
Here you can translate your strings and save them. The program will only continue if you close poedit.
Afterwards your translations will be merged to the corresponding files and you are finished

**Note:** The english translation will always be last, here you only need to translate the special keywords.


#### Special case hardware

If you have hardware packages, that only function as data storage, you can use the `--hardware` flag for both `openmodule_makemessages` and `openmodule_checktranslation` commands.
Differences
* Additional keyword `__MODEL`
* No check for `src` directory
* Only the keywords are translated and checked

```bash
openmodule_makemessages --hardware
```

#### Special case libraries

If you import libraries with translations you can add the with `--packages <library1> <library2>`. Translations already
done in the library can be used if those are located at <pip package path of library>/translation. Those always override
the current translation, so changes in the library are automatically applied to the translation of the service if you
run `openmodule_makemessages`. However you can override them again manually in the editor.

### Translation

If you need to change some translations after creation, you can directly edit them with the command `openmodule_translate --lang <language>`.
This again opens `poedit` for translation and merges the changes afterwards.


### Check translation

You can also check your translation with the `openmodule_checktranslation` command. This command will check if your 
translated strings are up to date and will also check if any language (except english) has non translated strings.
Check translation works with `git diff`, so you have to commit any changes before the commmand
