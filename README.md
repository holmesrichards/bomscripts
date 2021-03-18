# mdbom
KiCad plugin for grouped BOM in Markdown format

Add this to your KiCad 5.x plugins and use it like any other BOM plugin...

Generate a Markdown BOM list.
Components are sorted and grouped by value
Fields are (if exist)
Ref, Quantity, Value, Part, Description, Vendor
Parts with "Config" field containing "dnf" are omitted.

Command line:
```
python "pathToFile/bom_group_md.py" netlist-file markdown-file [--todocs]
```
	
If --todocs is used, replace path for output file with
/project/path/Docs where /project/path is the specified or implicit
directory or one at a higher level. If no such Docs directory is
found, specified or implicit path is used instead.
