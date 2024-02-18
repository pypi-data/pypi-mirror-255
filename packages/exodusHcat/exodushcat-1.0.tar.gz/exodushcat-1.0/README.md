# ExodusHcat
[![N|Solid](https://cldup.com/dTxpPi9lDf.thumb.png)](https://nodesource.com/products/nsolid)

![](https://img.shields.io/github/stars/pandao/editor.md.svg) ![](https://img.shields.io/github/forks/pandao/editor.md.svg) ![](https://img.shields.io/github/tag/pandao/editor.md.svg) ![](https://img.shields.io/github/release/pandao/editor.md.svg) ![](https://img.shields.io/github/issues/pandao/editor.md.svg) ![](https://img.shields.io/bower/v/editor.md.svg)

Convertor .seco file from Exodus Wallet, seco to hashcat string

## Installation
Python requires [Python.org](https://www.python.org/) v3,7+ to run.
Install the dependencies and devDependencies and start the server.
```sh
python -m pip install pip
python -m pip install --upgrade pip
pip install Exodushcat
```

## Using
```Python
from Exodushcat import extractHashcat
hashcat = extractHashcat(r"C:\Users\Administrator\Desktop\seed.seco")
print(hashcat)
```
######Output:
```
EXODUS:16384:8:1:tKHsGN1+vypJCD8weCMAzh4TJ2gvpFQsLCz3DU3RI18=:xCH6jPc2YoSx94oM:9a3nb9oOKhp3z2pgAFE0y3HNBKkKXFnyk90oNMunEqE=:CAgoIaKpjc+nkGUu5rGdIA==
```

------------



## License
MIT
**Encode Cipherbcrypt group**