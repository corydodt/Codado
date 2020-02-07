"""
Invoke user's editor on a temp file and present the edited contents back to the invoking code
"""
from __future__ import print_function

import os
import pipes
import shlex
import subprocess
import tempfile


TEMP_EXT = '.hotedit'
EDITOR_FALLBACK = "vi"


class HoteditException(Exception):
    """
    Base for any hotedit exception
    """


class EditingException(HoteditException):
    """
    Raised to signal that the editor we invoked errored out for some reason
    """


class Unchanged(HoteditException):
    """
    Raised to signal that an edited file was left unchanged
    """


def determine_editor(fallback=EDITOR_FALLBACK):
    """
    Figure out which of many possible options is the editor, starting with:
    -- git config core.editor
    -- EDITOR
    -- VISUAL

    If none of these is a usable editor, return the value of `fallback'.

    If fallback=None, and none of these is a usable editor, raise OSError
    """
    try:
        ret = subprocess.check_output(shlex.split('git config core.editor'))
        return ret.strip()
    except subprocess.CalledProcessError:
        "git config core.editor didn't work, falling back to environment"

    if os.environ.get('EDITOR'):
        return os.environ['EDITOR']

    if os.environ.get('VISUAL'):
        return os.environ['VISUAL']

    if fallback:
        return fallback

    raise OSError("No editor found (checked git, $EDITOR and $VISUAL)")


_remove = os.remove


def hotedit(initial=None, validate_unchanged=False, delete_temp=True, find_editor=determine_editor):
    """
    Edit `initial' string as the contents of a temp file in a local editor

    With `validate_unchanged' == True, raise the Unchanged exception when the file is closed with no changes

    With `delete_temp' == False, leave the temp file alone after editing, otherwise remove it by default

    `find_editor' is a zero-argument callable that returns an editor string, using hotedit.determine_editor by default

    Exceptions while invoking the editor are re-raised

    @returns the string after editing.
    """
    path = None
    try:
        handle, path = tempfile.mkstemp(TEMP_EXT)
        with os.fdopen(handle, 'w') as f:
            f.write(initial)

        cmd = shlex.split(find_editor()) + [path]
        rc = subprocess.call(cmd)
        if rc != 0:
            quoted = " ".join([pipes.quote(x) for x in cmd])
            raise EditingException("Command '%s' returned non-zero exit status %s" % (quoted, rc))

        with open(path, 'r') as tmp:
            edited = tmp.read()

        if validate_unchanged and edited.strip() == initial.strip():
            raise Unchanged("No changes since editing started")

        return edited

    finally:
        if delete_temp and path and os.path.exists(path):
            _remove(path)
