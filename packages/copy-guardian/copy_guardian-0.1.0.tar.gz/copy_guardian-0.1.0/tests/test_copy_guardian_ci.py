import filecmp
import os

import pytest

from copy_guardian import Connection


@pytest.mark.skipif(os.environ.get("CI") is None, reason="only works on CI")
def test_copy_ci_single_file(tmpdir):
    c = Connection(
        host="ssh-server",
        user="linuxserver.io",
        private_key="./id_ed25519",
        port=2222,
    )
    c.rsync_to(__file__, "remote_data/")
    back_file = str(tmpdir / "back.py")
    c.rsync_from("remote_data/*.py", back_file)
    assert filecmp.cmp(__file__, back_file)


@pytest.mark.skipif(os.environ.get("CI") is None, reason="only works on CI")
def test_copy_ci_recursively(tmpdir):
    c = Connection(
        host="ssh-server",
        user="linuxserver.io",
        private_key="./id_ed25519",
        port=2222,
    )

    here = os.path.dirname(os.path.abspath(__file__))
    c.rsync_to(here, "remote_data_tests/")
    c.rsync_from("remote_data_tests/", tmpdir)

    cmp = filecmp.dircmp(here, tmpdir)
    assert cmp.diff_files == []
    assert cmp.funny_files == []
