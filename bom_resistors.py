#
# Python script to generate a resistors only BOM from a KiCad generic netlist
# with sorting
#

"""@package
    Generate a text BOM list of resistors only.
    Components are sorted and grouped by value
    Fields are (if exist)
    Val, Quantity, Ref
    Command line:
    python "pathToFile/bom_resistors.py" netlist-file text-file [--todocs]
    If --todocs is used, replace path for output file with
    /project/path/Docs where /project/path is the specified or
    implicit directory or one at a higher level. If no such Docs
    directory is found, specified or implicit path is used instead.
    If --xxy is used, sort by 3-digit value (2 sig figs + # zeroes,
    e.g. 124 = 120k)
"""


from __future__ import print_function

# Import the KiCad python helper module and the csv formatter
import kicad_netlist_reader
import sys
import os.path

import re

xxy = False

def rkey(value):
    """Value to sorting key function
    Sorts by digits, then magnitude
    e.g.: 100R, 1k, 10k, 1M, 220, 3k, 4.7M, 680
    """

    if (value[-1] >= '0' and value[-1] <= '9'):
        valn = value
        valx = 'R'
    else:
        valn = value[:-1]
        valx = value[-1]
    while valn[0] == '0' and valn != "":
        valn = valn[1:]

    # Check if not standard format
    if valn[0] < '1' or valn[0] > '9' or re.search ("[^0-9RkM.]", valn):
        if xxy:
            return "zzzzzzzz"
        else:
            return 999999999

    dp = valn.find(".")
    if dp == -1:
        dig = valn
        mag = len(str(dig))-2
    else:
        dig = valn[:dp]+valn[dp+1:]
        mag = dp-2

    if len(dig) < 2:
        dig += '0'
    elif len(dig) > 2:
        dig = dig[:2]
        
    if valx == 'R':
        pass
    elif valx == 'k':
        mag += 3
    elif valx == 'M':
        mag += 6

    if xxy:
        return dig+str(mag)
    else:
        return int(dig) * 10**int(mag)

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
    
def myEqu(self, other):
    """myEqu is a more advanced equivalence function for components which is
    used by component grouping. Normal operation is to group components based
    on their Value and Footprint.
    In this example of a more advanced equivalency operator we also compare the
    custom fields Voltage, Tolerance and Manufacturer as well as the assigned
    footprint. If these fields are not used in some parts they will simply be
    ignored (they will match as both will be empty strings).
    """
    cfields = ["Tolerance", "Manufacturer", "Part", "Vendor", "SKU", "Voltage"]
    result = True
    if self.getValue() != other.getValue():
        result = False
    elif self.getPartName() != other.getPartName():
        result = False
    elif self.getFootprint() != other.getFootprint():
        result = False
    else:
        for cf in cfields:
            if self.getField(cf) != other.getField(cf):
                result = False
                break

    return result

# If -xxy specified sort by 3 digit value
if len(sys.argv) >= 4 and "--xxy" in sys.argv:
    xxy = True
    
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
if len(sys.argv) >= 4 and "--todocs" in sys.argv:
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

# Generate list

components = net.getInterestingComponents()

# Get all of the components in groups of matching parts + values
# (see kicad_netlist_reader.py)
grouped = net.groupComponents(components)

rows = []
ncomp = 0

for group in grouped:
    refs = ""

    # Add the reference of every component in the group and keep a reference
    # to the component so that the other data can be filled in once per group
    for component in group:
        r = component.getRef()
        if len(r) < 2 or r[0] != 'R' or (r[1] < '0' or r[1] > '9'):
            continue
        if len(refs) > 0:
            refs += ", "
        refs += r
        ncomp += 1
        c = component
    if len(refs) == 0:
        continue
    
    rows.append([refs, str(len(group)), c.getValue()])

for r in sorted (rows, key = lambda row: rkey(row[2])):
    print (r[2], "\t", r[1], "\t", r[0], file=f)
