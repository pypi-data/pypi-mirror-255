---
author: Delhaye Adrien
year: 2023
---

# Iot Protocols

This package contains easy to use module for communication using various IIoT protocols.

## Install

```bash
pip install iot-protocols 
```

## Upload on Twine

### Upload pyporject.toml

> **More detailled informations on** <https://packaging.python.org/en/latest/tutorials/packaging-projects/>

Open the pyproject.toml file and update at least the _version_ field with your current verion following the template :

```bash
For alpha release : <version>.<subversion>.<fix>-a<i>
For beta release : <version>.<subversion>.<fix>-b<i>
For relase candidate release : <version>.<subversion>.<fix>-rc<i>
For final release : <version>.<subversion>.<fix>
```

### Save your changes

Save everything.

Test everyting.

Push the files on the gitlab repository with version associated TAG.

### Build the package

Ensure you have upgraded pip:

```bash
py -m pip install --upgrade pip
```

Then from the root directory where the **pyproject.toml** file belongs, execute :

```bash
py -m build
```

This will generate your package tar.gz and wheel files into the **build** folder.

### Upload the dist

First ensure you have twine updated:

```bash
py -m pip install --upgrade twine
```

Get your username and token from PyPi

Use the following command to upload and gives your username and token to authentify, with username as '\_\_token\_\_':

```bash
py -m twine upload dist/<package-file-to-update>
```

You can also, if the build package doesn't exists yet on the PyPi registry use :

```bash
py -m twine upload dist/*
```

## How to use

### CMD line test

You can use the command line interface to explicitely make request using one of the available protocol.
To to this, call the _main.py_ script and pass the disired and or required arguments to the command.

For exemple, using the modbus client:

### Modbus Client

### IEC62056 Client

### Snap-7 Client
