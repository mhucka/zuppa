'''
findercomment.py: write Zotero URI into the macOS Finder comments for a file

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020 by Michael Hucka and the California Institute of Technology.
This code is open-source software released under a 3-clause BSD license.
Please see the file "LICENSE" for more information.
'''

import applescript
from   bun import inform, warn
from   commonpy.string_utils import antiformat
import re

if __debug__:
    from sidetrack import log

from .base import WriterMethod


# Constants.
# .............................................................................

# The following code is based in part on code from Python package "osxmetadata"
# version 0.99.10 of 2020-09-01, Copyright (c) 2020 Rhet Turnbull.
# https://github.com/RhetTbull/osxmetadata/blob/master/osxmetadata/findercomments.py

_FINDER_SCRIPTS = applescript.AppleScript('''
on get_comments{f}
    tell application "Finder"
        return comment of (POSIX file f as alias)
    end tell
end run

on set_comments{f, c}
    tell application "Finder"
        set comment of (POSIX file f as alias) to c as Unicode text
    end tell
end run

on clear_comments{f}
    tell application "Finder"
        set c to missing value
        set comment of (POSIX file f as alias) to c
    end tell
end run
''')


# Class definitions.
# .............................................................................

class FinderComment(WriterMethod):
    '''Implements writing Zotero URI into the macOS Finder comments for a file.'''

    @classmethod
    def name(self):
        return 'findercomment'


    @classmethod
    def description(self):
        return ('Prepends the Zotero select link to the Finder comments for the'
                + ' file. Zuppa tries to be careful how it does this: if it'
                + ' finds a Zotero URI as the first thing in the comments, it'
                + ' replaces that URI instead of prepending a new one.'
                + ' However, Finder comments are notorious for being easy to'
                + ' damage or lose, so beware that Zuppa may irretrievably'
                + ' corrupt any existing Finder comments on the file.')


    def write_uri(self, file, uri, dry_run, overwrite):
        '''Writes the "uri" into the Finder comments of file "file".

        If there's an existing comment, read it.  If there's a Zotero URI
        as the first thing in the comment, replace that URI with this one,
        under the assumption that this was a URI written by a prior run of
        this program; otherwise, prepend the Zotero URI to the finder
        comments.  In either case, write the results back.
        '''

        path = antiformat(f'[grey89]{file}[/]')
        if not overwrite:
            if __debug__: log(f'reading Finder comments of file {file}')
            comments = _FINDER_SCRIPTS.call('get_comments', file)
            if comments and uri in comments:
                inform(f'Zotero URI already present in Finder comments of {path}')
                return
            elif comments and 'zotero://select' in comments:
                warn(f'Replacing existing Zotero URI in Finder comments of {path}')
                if __debug__: log(f'overwriting existing Zotero URI with {uri}')
                comments = re.sub('(zotero://\S+)', uri, comments)
            else:
                inform(f'Writing Zotero URI into Finder comments of {path}')
                comments = uri
        else:
            if not dry_run:
                if __debug__: log(f'invoking AS function to clear comment on {file}')
                _FINDER_SCRIPTS.call('clear_comments', file)
            inform(f'Ovewriting Finder comments with Zotero URI in {path}')
            comments = uri

        if not dry_run:
            if __debug__: log(f'invoking AS function to set comment on {file}')
            _FINDER_SCRIPTS.call('set_comments', file, comments)
