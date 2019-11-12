Fairly flexible, yet simple and opinionated translator.

This is implemented mostly to resolve (or at least work around) a fair few issues and nuisances I've found with Red's built-in translator,
while also having a fair few helpful utilities I find to be useful during development, and generally be much nicer to translate
strings for.

This translator is also (in my opinion), much cleaner to use, turning the following snippet:

```py
>>> _("Hello, {}!").format("world")
'Hello, world!'
```

... into this:

```py
>>> # this assumes you have a locale file with an item with the key `hello` containing the value `Hello, {name}!`
>>> translate("hello", name="world")
'Hello, world!'
```

This has a few primary advantages over Red's built-in translator:

1. It forces the use of keyword arguments for formatting instead of ambiguous positional arguments,
   which could cause confusion for translators, and thereby lead to translation errors.
2. Output strings aren't bundled in the source code, but are placed in an entirely separate file, which in my experience
   helps me to not constantly tweak strings because I'm simply not satisfied with how they're worded, with the additional
   benefit of allowing users to customize the strings without having to either figure out how to use a translation program,
   or just outright figure out how gettext works.
3. Implementing plurality support in translated strings is significantly easier[*](#regarding-pluralization) than with Red's translator,
   where you have to special-case if/else `n == 1` - which *isn't portable between locales* - whereas this translator
   supports proper pluralization, primarily with ICU message formatting, but also with legacy support for Babel.

This translator also resolves a few nuisances and potential problems I've identified with Red's built-in translator (this list isn't exhaustive!):

- Updating translation stubs is largely a manual process; even with [a helper script](https://gitlab.com/odinair/Swift-Cogs/blob/master/.scripts/gen_locales.py)
  to automate the boring part of generating every cog's locale stubs. This - admittedly - isn't a even really an issue, but it does add up to be a small nuisance.
- Red's built-in translator keeps *EVERY* created translator in a global list, which are **never garbage collected.**
  This is also contributed to by cogs which create more than one translator instance, such as Mod,
  which as of Red 3.1.0, creates ***8 separate translator instances!***
- This translator only loads locales when required, which Red's translator doesn't do - it loads the locale files for
  **every known translator (even orphaned translator instances!)** when the locale is set with `[p]set locale`.
  Of course, this usually won't add up to be a noticeable issue, especially since if the machine you're
  running Red on can barely handle loading some locales, you're likely going to end up having larger issues
  when *using* your bot.

Additionally, this translator tries to make as little assumptions about your requirements as possible. If you want to use a different
file format for your translations than plain YAML, you can configure it to use a different loader. If you want to
handle strings slightly differently than just a simple `str.format`, you can configure it to use a different locale class type
(similarly to how `ICULocale` functions).

But of course, these probably aren't critical issues that immediately invalidate any reason to use Red's built-in translator.
It's definitely acceptable enough for use, and honestly I don't have all too much against it, this translator is just much nicer
to work with in my opinion, mostly on account of properly localized strings, and much cleaner string formatting.

## Regarding pluralization

Pluralization with Red's translator is nothing short of an absolute fucking nightmare.

While, yes - it is possible - you're going to have to re-invent the wheel to do it.

Or, of course, you could just assume every language uses English-like plurality rules. But that's not how languages work.

Take the following example with this translator w/ ICU message formatting:

```py
>>> from swift_libs.translations import Translations, MemoryLoader, ICULocale
>>> loader = MemoryLoader({'en': {'unread': 'You have {n, plural, =0 {no new messages} one {one unread message} other {# unread messages}}'}})
>>> translate = Translations(__file__, loader=loader, locale_type=ICULocale, default='en')
>>> translate('unread', n=0)
'You have no new messages'
>>> translate('unread', n=1)
'You have one new message'
>>> translate('unread', n=2)
'You have 2 new messages'
```

Now compare it to effectively the same example, but with Red's translator:

```py
>>> from redbot.core.i18n import Translator
>>> _ = Translator("are these names ever used?", __file__)
>>> def plural(n):
...   if n == 0:
...     return _('You have no new messages')
...   elif n == 1:
...     return _('You have one unread message')
...   else:
...     return _('You have {} new messages').format(n)
>>> plural(0)
'You have no new messages'
>>> ... # you should get the idea by now
```

With Red's translator, pluralization is entirely developer-influenced, unless you actively go out of your way
to handle localization for every potential locale; which, let's be honest - you're not about to subject yourself
to the absolute nightmare that'd be to implement.

It'd be easier to just use `thing(s)` to denote potential plurality and call it a day. Or, of course -
just assume every locale uses English plurality rules, and hard-code an if/else statement or two to switch
between strings. But, again - that's not even close to how languages actually work.
