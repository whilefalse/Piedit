"""Module for the union-find functions for the piet interpreter"""

import sys

__author__ = "Steven Anderson"
__copyright__ = "Steven Anderson 2008"
__credits__ = ["Steven Anderson"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Steven Anderson"
__email__ = "steven.james.anderson@googlemail.com"
__status__ = "Production"

def union(parent,child):
    """Performs a union by attaching the root node of the smaller set to the
    root node of the larger set"""
    if parent.set_size < child.set_size:
        child, parent = parent, child
        
    parent_head = find(parent)
    child_head = find(child)
    
    if parent_head == child_head:
        return
    
    child_head.parent = parent_head
    child_head.set_label = parent_head.set_label
    parent_head.set_size = parent_head.set_size + child_head.set_size

def find(item):
    """Finds the root node of a given item, attaching it directly to its root node
    on the way up"""
    if item.parent == item:
        return item
    else:
        item.parent = find(item.parent)
        return item.parent