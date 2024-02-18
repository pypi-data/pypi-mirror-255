# func-live

This package allows you to import and call functions available on https://func.live.

## Installation

```pip install func_live```

## Usage

There are many functions available on `func.live`. The below snippet is for using the `qrcode()` function. You can browse available functions on https://func.live/functions.

```py
from func_live import func_live

# Set your FUNC_TOKEN
import os
os.environ['FUNC_TOKEN'] = 'your_func_token'

# Using the qrcode() function
answer = func_live.qrcode('https://bbc.co.uk')
print({'answer': answer})
```

## FUNC_TOKEN

You can get yourself a FUNC_TOKEN by visiting https://tokens.wakeflow.io

## Available Functions

You can browse the functions that are available on https://func.live/functions

## Problems/Support/Feedback

Please don't hesitate to get in touch on andi@wakeflow.io
