##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.11.2                                                             #
# Generated on 2024-02-08T21:32:40.906111                                        #
##################################################################################

from __future__ import annotations


def main(template, data = None, **kwargs):
    ...

def cli_main():
    """
    Render mustache templates using json files
    """
    ...

def render(template = "", data = {}, partials_path = ".", partials_ext = "mustache", partials_dict = {}, padding = "", def_ldel = "{{", def_rdel = "}}", scopes = None, warn = False, keep = False):
    """
    Render a mustache template.
    
    Renders a mustache template with a data scope and partial capability.
    Given the file structure...
    ╷
    ├─╼ main.py
    ├─╼ main.ms
    └─┮ partials
      └── part.ms
    
    then main.py would make the following call:
    
    render(open('main.ms', 'r'), {...}, 'partials', 'ms')
    
    
    Arguments:
    
    template      -- A file-like object or a string containing the template
    
    data          -- A python dictionary with your data scope
    
    partials_path -- The path to where your partials are stored
                     If set to None, then partials won't be loaded from the file system
                     (defaults to '.')
    
    partials_ext  -- The extension that you want the parser to look for
                     (defaults to 'mustache')
    
    partials_dict -- A python dictionary which will be search for partials
                     before the filesystem is. {'include': 'foo'} is the same
                     as a file called include.mustache
                     (defaults to {})
    
    padding       -- This is for padding partials, and shouldn't be used
                     (but can be if you really want to)
    
    def_ldel      -- The default left delimiter
                     ("{{" by default, as in spec compliant mustache)
    
    def_rdel      -- The default right delimiter
                     ("}}" by default, as in spec compliant mustache)
    
    scopes        -- The list of scopes that get_key will look through
    
    warn          -- Issue a warning to stderr when a template substitution isn't found in the data
    
    keep          -- Keep unreplaced tags when a template substitution isn't found in the data
    
    
    Returns:
    
    A string containing the rendered template.
    """
    ...

class ChevronError(SyntaxError, metaclass=type):
    ...

