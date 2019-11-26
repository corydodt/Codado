"""
Test hotedit, the tool for invoking a local editor on a temp file
"""
import os
import subprocess

from mock import ANY, patch

from pytest import raises

from codado import hotedit


def test_determine_editor():
    """
    Do I figure out the right editor based on the running environment?
    """
    with patch.object(subprocess, 'check_output', return_value='giteditor'):
        assert hotedit.determine_editor() == 'giteditor'

    pCheckOutput = patch.object(subprocess, 'check_output',
        side_effect=subprocess.CalledProcessError('ohh', 'noo'))
    env = os.environ.copy()
    pEnviron = patch.object(os, 'environ', env)
    with pCheckOutput, pEnviron:
        env['VISUAL'] = 'visual'
        assert hotedit.determine_editor() == 'visual'

        env['EDITOR'] = 'editor'
        assert hotedit.determine_editor() == 'editor'

        del env['VISUAL'], env['EDITOR']

        assert hotedit.determine_editor() == 'vi'

        with raises(OSError):
            hotedit.determine_editor(fallback=None)


def test_hotedit():
    """
    What happens if hotedit is called with an editor we can't find?
    """
    find_editor = lambda: '---asdfasdfwsdf---'

    input_ = "asdfasdfa"

    # 1. cmd does not exist -> OSError
    with raises(OSError):
        hotedit.hotedit(input_, find_editor=find_editor)

    # 2. error while editing -> EditingException
    pSubprocessCall = patch.object(subprocess, 'call', return_value=19)
    with pSubprocessCall, raises(hotedit.EditingException):
        hotedit.hotedit(input_, find_editor=find_editor)

    pRemove = patch.object(hotedit, "_remove", autospec=True)

    # 3. unchanged while editing + validate_unchanged -> Unchanged
    # 5. any exception -> temp is removed
    pSubprocessCall = patch.object(subprocess, 'call', return_value=0)
    with pRemove as mRemove, pSubprocessCall, raises(hotedit.Unchanged):
        hotedit.hotedit(input_, find_editor=find_editor, validate_unchanged=True)
    mRemove.assert_called_once_with(ANY)

    # 4. unchanged while editing + !validate_unchanged -> string
    # 6. happy path -> return edited string, temp is removed
    pSubprocessCall = patch.object(subprocess, 'call', return_value=0)
    with pRemove as mRemove, pSubprocessCall:
        ret = hotedit.hotedit(input_, find_editor=find_editor, validate_unchanged=False)
        assert ret == input_
        mRemove.assert_called_once_with(ANY)

    # 7. happy path + !delete_temp -> return edited string, temp is left
    with pRemove as mRemove, pSubprocessCall:
        ret = hotedit.hotedit(input_, find_editor=find_editor, validate_unchanged=False, delete_temp=False)
        assert ret == input_
        assert mRemove.call_count == 0
