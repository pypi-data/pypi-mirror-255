# File Signature Collectors

Project focused on obtaining, processing and storing information related to "magic numbers" from the files.


You can save the data in a normal file (`file_signatures` - default) or in a sqlite file (`file_signatures.sqlite` - default).


# Install

```bash
pip install filesignaturecollectors
```

# How to use - Python

```python
from filesignaturecollectors import Controller

# Initializes the counter.
c = Controller()

# gets data from source.
data1 = c.get_data_wiki()
data2 = c.get_data_gck()

# filters and concatenates the elements into a single list.
c.consolidate_data(data1, data2)

# gets the list of formatted items for storage.
data_formatted = c.get_dict_data()

# saves to normal file.
c.to_file(data=data_formatted)

# saves to sqlite file.
c.to_db(data=data_formatted)
```

# How to use - CLI

```bash
$ collectfilesignatures -h
usage: collectfilesignatures [-h] [-a] [-w] [-g] [-f] [-db]

Collect file signatures from sources.

options:
  -h, --help     show this help message and exit
  -a, --all      Gets data from all collectors.
  -w, --wiki     Gets data from all collectors.
  -g, --gck      Gets data from all collectors.
  -f, --to_file  Save the data into a file.
  -db, --to_db   Save the data into a sqlite db.

An easy way to get file signatures.
```


# Sources

> * [GCK page - File Signatures](https://www.garykessler.net/library/file_sigs.html)
> * [Wikipedia - File Signatures](https://en.wikipedia.org/wiki/List_of_file_signatures)
