<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
    <img src="https://github.com/dave-lanigan/lambchop/assets/29602997/9c0826c8-b6b0-4ad7-84f4-85ff4b1e7c74" alt="Logo" width="250" height="250">

  <h3 align="center">lambchop</h3>

  <p align="center">
    A sidekick for your AWS Lambda
  <br/>

   ![](https://img.shields.io/badge/language-python-blue)
   ![version](https://img.shields.io/badge/version-1.2.3-green)
   ![](https://img.shields.io/badge/license-MIT-red)
   
  </p>
</div>

## Overview

`lambchop` is an Python package to make regular AWS Lambda functions asyncronous by allowing them to run background processes. 


## Installation
pypi:

```
pip install lambchop
```

github:

```
pip install git+ssh://git@github.com/dave-lanigan/lambchop.git
```
```
pip install git+https://git@github.com/dave-lanigan/lambchop.git
```

## Usage

```
import anyio
import time
from lambchop import SideKick

def long_running_process(x, y):
    print("Starting process.")
    time.sleep(x + y)
    print("Completed.")


async def main():
    sk = SideKick()
    await sk.process(long_running_process, x=5, y=3)
    print("Done sending.")

if __name__ == "__main__":
    anyio.run(main)
```
