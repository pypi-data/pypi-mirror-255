# gooey-quick

Turn type-hinted Python program into a GUI application with few additional lines of code

![gooey-quick title card](https://raw.githubusercontent.com/jacadzaca/gooey_quick/master/title_card.webp)

Table of contents
-----------------------------------------

- [gooey-quick](#gooey-quick)
- [Table of contents](#table-of-contents)
- [Quick Start](#quick-start)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Gooey global configuration](#gooey-global-configuration)
- [What is it?](#what-is-it-?)
- [Why is it?](#why-is-it-?)
- [Examples](#examples)
- [Packaging](#packaging)

-----------------------------------------


## Quick Start

### Installation

You can install gooey-quick via pip:
```bash
pip install gooey-quick
```

or by cloning the repository directly:
```bash
git clone https://github.com/jacadzaca/gooey_quick.git && ./setup.py
```

### Usage
You can integrate gooey-quick with your code as easily as so:
```python
import gooey_quick


def some_function_you_want_to_gooeyfiy(
    name: str,
    repeat_count: int,
):
    for _ in range(repeat_count):
        print(f'Hello {name}')


if __name__ == '__main__':
    gooey_quick.run_gooey(some_function_you_want_to_gooeyfiy)
```

### Gooey global configuration
You can set [Gooey's global options](https://github.com/chriskiehl/Gooey#global-configuration)
by setting them in the call to `gooey_quick.run_gooey` like so:

```python
import gooey_quick


def some_function_you_want_to_gooeyfiy(
    name: str,
    repeat_count: int,
):
    for _ in range(repeat_count):
        print(f'Hello {name}')


if __name__ == '__main__':
    gooey_quick.run_gooey(
        some_function_you_want_to_gooeyfiy,
        program_name='Simple demo program',
        program_description='A demo program using Gooey and gooey_quick',
    )
```


## What is it?
gooey-quick is a library that generates a [Gooey-based](https://github.com/chriskiehl/Gooey)
GUIs from methods' signatures.


## Why is it?
A lot of GUI programs that are written in an office setting are wrappers around
simple python code. Handcrafting GUIs can be cumbersome, while dealing with
argparse-like interface becomes more annoying as the program grows (e.g. you
have 6 tabs in your Advanced layout Gooey program). With gooey-quick you should
forget about the above and focus on the programs' features.


## How does it work?
gooey-quick uses python's built-in [typing](https://docs.python.org/3/library/typing.html)
and [introspection](https://docs.python.org/3/library/inspect.html) functionalities
to analyze objects' signatures and generate a fancy GUI using the amazing
[Gooey](https://github.com/chriskiehl/Gooey) by [chriskiehl](https://github.com/chriskiehl).


## Examples

Simple 'Flat layout' application
```python3
#!/usr/bin/env python3
from enum import Enum
from pathlib import Path
from datetime import date, time

import gooey_quick


class UploadMethod(Enum):
    SFTP = 'SFTP'
    HTTP = 'HTTP'


def upload_file(
    file: Path,
    new_filename: str,
    chunksize: int,
    lattency: float,
    upload_date: date,
    upload_time: time,
    upload_method: UploadMethod,
):
    assert type(upload_method) is UploadMethod
    return (
        f'{file} was uploaded via {upload_method.name} on {upload_date} at '
        f'{upload_time} in chunks of size {chunksize} and with lattency of '
        f'{lattency}'
    )


if __name__ == '__main__':
    # gooey_quick.run_gooey has the same return values as the wrapped function
    return_value = gooey_quick.run_gooey(
        # the first argument is the fucntion you'd like to be converted into a Gooey program
        upload_file,
        # gooey_quick.run_gooey can be used to set Gooey's global configuration
        # see https://github.com/chriskiehl/Gooey#global-configuration for possible options
        program_name='Simple upload program',
        program_description='A demo program using Gooey and gooey_quick',
    )
    print(return_value)
```

Start Gooey in Advanced mode with 3 different tabs:
```python3
#!/usr/bin/env python3
from pathlib import Path
from typing import Optional
from datetime import date, datetime

import gooey_quick


def search_history(
    history_file: Path,
    wanted_phrase: str,
    min_occure_date: Optional[date] = None,
    max_occure_date: Optional[date] = None,
) -> Optional[tuple[date, str]]:
    occurance_date = date(year=2002, month=7, day=22)
    the_phrase = "wow you have discovered my secret phrase!"
    occurance_in_range = True

    if min_occure_date is not None and max_occure_date is not None:
        print(f'Looking for {wanted_phrase} from {min_occure_date} to {max_occure_date}...')
        occurance_in_range = occurance_date in range(min_occure_date, max_occure_date)

    if wanted_phrase in the_phrase and occurance_in_range:
        return f'{occurance_date}: {the_phrase}'


def append_to_history(
    history_file: Path,
    phrase: str,
    occurance_date: date = datetime.now().date()
):
    return f'Appending {phrase} to {history_file} at {occurance_date}...'


def remove_from_history(
    history_file: Path,
    phrase: str,
):
    return f'Removing {phrase} from {history_file}...'


if __name__ == '__main__':
    # when passing a dict to gooey_quick.run_gooey, the keys become
    # the tabs descriptions, while the values are the function to
    # create the gui from
    return_value = gooey_quick.run_gooey(
        {
           'Add phrase': append_to_history,
           'Remove phrase': remove_from_history,
           'Search phrases': search_history,
        },
        # set Gooey's global config as per: https://github.com/chriskiehl/Gooey#layout-customization
        navigation='TABBED',
        program_name='Gooey subparser layout from function dict',
        program_description='Presents how to create a bundeled configuration with gooey_quick',
     )
    print(return_value)
```

For more see the `docs/examples/` directory.

## Packaging
Please refer to either the [official guide](https://github.com/chriskiehl/Gooey#packaging) 
or [this tutorial](https://medium.com/analytics-vidhya/how-to-create-a-gui-cli-standalone-app-in-python-with-gooey-and-pyinstaller-1a21d0914124)

