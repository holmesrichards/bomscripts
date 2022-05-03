# mdbom
KiCad plugin for grouped BOM in Markdown format

Add this to your KiCad scripting plugins and use it like any other BOM plugin...

In my Linux installation it goes in `.local/share/kicad/6.0/scripting/plugins`. That folder must also contain a copy of (or contain a symlink to) `kicad_netlist_reader.py` which I find in `/usr/share/kicad/plugins`.

Components are sorted and grouped by value.
Fields included are (if existing) Refs, Quantity, Component, Description, Manufacturer, Part, Vendor, and SKU. Columns after "Description" are suppressed if empty for all components. Parts with "Config" field containing "dnf" are omitted. (In KiCad 6+, this isn't needed since there is an "exclude from BOM" check box.)

If there is a user-defined field named Description, its contents override the default description. This may be more convenient than going into the symbol editor to change the description.

Command line:
```
python "pathToFile/bom_group_md.py" netlist-file markdown-file [--todocs]
```
	
If --todocs is used, path for output file is replaced with `/project/path/Docs` where `/project/path` is the specified or implicit output directory or one at a higher level. If no such Docs directory is found, specified or implicit path is used instead.
