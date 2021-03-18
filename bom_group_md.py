#
# Python script to generate a BOM from a KiCad generic netlist
# in Markdown format
#
# Sorted and Grouped Markdown BOM with advanced grouping
# same as version from KiCad install but without footprints
#
# Parts with "Config" field containing "dnf" are omitted.

"""@package
    Generate a Markdown BOM list.
    Components are sorted and grouped by value
    Fields are (if exist)
    Ref, Quantity, Value, Part, Description, Vendor
    Parts with "Config" field containing "dnf" are omitted.

    Command line:
    python "pathToFile/bom_group_md.py" netlist-file markdown-file [--todocs]

    If --todocs is used, replace path for output file with
    /project/path/Docs where /project/path is the specified or
    implicit directory or one at a higher level. If no such Docs
    directory is found, specified or implicit path is used instead.
"""


from __future__ import print_function

# Import the KiCad python helper module and the csv formatter
import kicad_netlist_reader
import sys
import os.path

def findDocs (path):
    """
    If path contains a directory named Docs, return relative path to
    that directory, otherwise recursively look in higher
    directories. If no such Docs directory is found return None.
    """

    if path == os.path.sep:
        return
    if path == "":
        path = os.getcwd()
    for p in os.listdir(path):
        if p == "Docs" and os.path.isdir(os.path.join(path, p)):
            return os.path.relpath(os.path.join(path, p))
    return findDocs (os.path.dirname(path))    
    
# Start with a basic md template
md = """# <!--SOURCE--> BOM

<!--DATE-->

Generated from schematic by <!--TOOL-->

<!--COMPCOUNT-->

<!--TABLEROW-->
    """

def myEqu(self, other):
    """myEqu is a more advanced equivalence function for components which is
    used by component grouping. Normal operation is to group components based
    on their Value and Footprint.

    In this example of a more advanced equivalency operator we also compare the
    custom fields Voltage, Tolerance and Manufacturer as well as the assigned
    footprint. If these fields are not used in some parts they will simply be
    ignored (they will match as both will be empty strings).

    """
    result = True
    if self.getValue() != other.getValue():
        result = False
    elif self.getPartName() != other.getPartName():
        result = False
    elif self.getFootprint() != other.getFootprint():
        result = False
    elif self.getField("Tolerance") != other.getField("Tolerance"):
        result = False
    elif self.getField("Manufacturer") != other.getField("Manufacturer"):
        result = False
    elif self.getField("Voltage") != other.getField("Voltage"):
        result = False

    return result

# Override the component equivalence operator - it is important to do this
# before loading the netlist, otherwise all components will have the original
# equivalency operator.
kicad_netlist_reader.comp.__eq__ = myEqu

# Generate an instance of a generic netlist, and load the netlist tree from
# <file>.tmp. If the file doesn't exist, execution will stop
net = kicad_netlist_reader.netlist(sys.argv[1])

# Open a file to write to, if the file cannot be opened output to stdout
# instead
if len(sys.argv) >= 3:
    fname = sys.argv[2]
else:
    fname = "bom.md"

# If --todocs specified try to find Docs directory and use that
if len(sys.argv) >= 4 and sys.argv[3] == "--todocs":
    fpath = findDocs(os.path.dirname(fname))
    if fpath == None:
        e = "No Docs directory found above " + os.path.dirname(fname)
        print(__file__, ":", e, file=sys.stderr)
    else:
        fname = os.path.join(fpath, os.path.basename(fname))

try:
    f = open(fname, 'w')
    e = "Writing to file " + fname
    print(__file__, ":", e, file=sys.stderr)
except IOError:
    e = "Can't open output file for writing: " + fname
    print(__file__, ":", e, file=sys.stderr)
    f = sys.stdout

# Output a set of rows for a header providing general information

md = md.replace('<!--SOURCE-->', os.path.basename(net.getSource()))
md = md.replace('<!--DATE-->', net.getDate())
md = md.replace('<!--TOOL-->', net.getTool())
md = md.replace('<!--COMPCOUNT-->', "**Component Count:** " + \
    str(len(net.components)))

row  = "| Value | Qty | Part | Description | Vendor |"

md = md.replace('<!--TABLEROW-->', row + "<!--TABLEROW-->")

row  = "\n| ----- | --- | ---- | ----------- | ------ |"

md = md.replace('<!--TABLEROW-->', row + "<!--TABLEROW-->")

components = net.getInterestingComponents()

# Get all of the components in groups of matching parts + values
# (see kicad_netlist_reader.py)
grouped = net.groupComponents(components)

# Output all of the component information
for group in grouped:
    refs = ""

    # Add the reference of every component in the group and keep a reference
    # to the component so that the other data can be filled in once per group
    for component in group:
        if component.getField("Config").casefold() == "dnf":
            continue
        if len(refs) > 0:
            refs += ", "
        refs += component.getRef()
        c = component
    if len(refs) == 0:
        continue
    
    row = "\n"
    row += "| " + refs +" | " + str(len(group))
    row += " | " + c.getValue() + " | "
#    row += c.getLibName() + ":"
    row += c.getDescription() + " | " + c.getField("Vendor")
    row += " |"

    md = md.replace('<!--TABLEROW-->', row + "<!--TABLEROW-->")

# Print the formatted md to output file
md = md.replace('<!--TABLEROW-->', "")
print(md, file=f)
