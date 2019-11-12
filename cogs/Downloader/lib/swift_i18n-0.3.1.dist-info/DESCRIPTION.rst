# swift_i18n

Simple yet configurable translator based on ICU message formatting.

This requires at least Python 3.7.

## Basic Usage

```python
from swift_i18n import Translator

translate = Translator(__file__)

# This assumes you have a `locales/en-US.toml` file in the current scripts parent directory containing
# the following line:
#  hello = 'Hello, {name}'
print(translate('hello', name='world'))  # This should result in 'Hello, world'
```


