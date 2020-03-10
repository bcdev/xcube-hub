# xcube-gen

An [xcube plug-in](https://github.com/dcs4cop/xcube) that implements a data cube generation service

## Setup

```bash
cd xcube-gen
conda env create
conda activate xcube-gen
python setup.py develop
```
    
### Test:

    $ pytest

## Tools

Check xcube CLI extension added by `xcube_gen` plugin:

    $ xcube --help
    
`genserv` should now be in the list.    

Start the service: 

    $ xcube genserv start 

