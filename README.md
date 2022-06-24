# KiCad BOM scripts

KiCad plugins for BOMs

Add the Python scripts to your KiCad scripting plugins and use them like any other BOM plugin...

In my Linux installation they go in `.local/share/kicad/6.0/scripting/plugins`. That folder must also contain a copy of (or contain a symlink to) `kicad_netlist_reader.py` which I find in `/usr/share/kicad/plugins`.

## bom_group_md

Grouped BOM in Markdown format

Components are sorted and grouped by value.
Fields included are (if existing) Refs, Quantity, Component, Description, Manufacturer, Part, Vendor, and SKU. Columns after "Description" are suppressed if empty for all components. Parts with "Config" field containing "dnf" are omitted. (In KiCad 6+, this isn't needed since there is an "exclude from BOM" check box.)

If there is a user-defined field named Description, its contents override the default description. This may be more convenient than going into the symbol editor to change the description.

Command line:
```
python "pathToFile/bom_group_md.py" netlist-file markdown-file [--todocs]
```
	
If --todocs is used, path for output file is replaced with `/project/path/Docs` where `/project/path` is the specified or implicit output directory or one at a higher level. If no such Docs directory is found, specified or implicit path is used instead.

## bom_resistors

Resistors only, sorted by value, in text format.

Command line:
```
python "pathToFile/bom_resistors.py" netlist-file text-file [--xxy] [--todocs]
```

If --xxy is used, values are internally converted to 3-digit representation (2 significant figures + number of zeroes, e.g. 124 for 120k) for sorting. Otherwise numerical value (e.g. 120000 for 120k) is used. Values not conforming to expected format are put last.

If --todocs is used, path for output file is replaced with `/project/path/Docs` where `/project/path` is the specified or implicit output directory or one at a higher level. If no such Docs directory is found, specified or implicit path is used instead.
