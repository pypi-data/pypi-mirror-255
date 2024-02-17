# Copyright (C) 2018-2023  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from os import path
from typing import Dict, List

import pytest

from swh.loader.core.utils import compute_nar_hashes
from swh.model.hashutil import MultiHash


@pytest.fixture
def tarball_path(datadir):
    """Return tarball filepath fetched by TarballDirectoryLoader test runs."""
    return path.join(datadir, "https_example.org", "archives_dummy-hello.tar.gz")


@pytest.fixture
def tarball_with_executable_path(datadir):
    """Return tarball filepath (which contains executable) fetched by
    TarballDirectoryLoader test runs."""
    return path.join(
        datadir, "https_example.org", "archives_dummy-hello-with-executable.tar.gz"
    )


@pytest.fixture
def content_path(datadir):
    """Return filepath fetched by ContentLoader test runs."""
    return path.join(
        datadir, "https_common-lisp.net", "project_asdf_archives_asdf-3.3.5.lisp"
    )


@pytest.fixture
def executable_path(datadir):
    """Return executable filepath fetched by ContentLoader test runs."""
    return path.join(datadir, "https_example.org", "test-executable.sh")


def compute_hashes(filepath: str, hash_names: List[str] = ["sha256"]) -> Dict[str, str]:
    """Compute checksums dict out of a filepath"""
    return MultiHash.from_path(filepath, hash_names=hash_names).hexdigest()


@pytest.fixture
def tarball_with_std_hashes(tarball_path):
    return (
        tarball_path,
        compute_hashes(tarball_path, ["sha1", "sha256", "sha512"]),
    )


@pytest.fixture
def tarball_with_nar_hashes(tarball_path):
    nar_hashes = compute_nar_hashes(tarball_path, ["sha256"])
    # Ensure it's the same hash as the initial one computed from the cli
    assert (
        nar_hashes["sha256"]
        == "23fb1fe278aeb2de899f7d7f10cf892f63136cea2c07146da2200da4de54b7e4"
    )
    return (tarball_path, nar_hashes)


@pytest.fixture
def tarball_with_executable_with_nar_hashes(tarball_with_executable_path):
    nar_hashes = compute_nar_hashes(tarball_with_executable_path, ["sha256"])
    # Ensure it's the same hash as the initial one computed from the cli
    assert (
        nar_hashes["sha256"]
        == "1d3407e5ad740331f928c2a864c7a8e0796f9da982a858c151c9b77506ec10a8"
    )
    return (tarball_with_executable_path, nar_hashes)


@pytest.fixture
def content_with_nar_hashes(content_path):
    nar_hashes = compute_nar_hashes(content_path, ["sha256"], is_tarball=False)
    # Ensure it's the same hash as the initial one computed from the cli
    assert (
        nar_hashes["sha256"]
        == "0b555a4d13e530460425d1dc20332294f151067fb64a7e49c7de501f05b0a41a"
    )
    return (content_path, nar_hashes)


@pytest.fixture
def executable_with_nar_hashes(executable_path):
    nar_hashes = compute_nar_hashes(executable_path, ["sha256"], is_tarball=False)
    # Ensure it's the same hash as the initial one computed from the (guix hash) cli
    assert (
        nar_hashes["sha256"]
        == "d29c24cee7dfc0f015b022e9af1c913f165edfaf918fde966d82e2006013a8ce"
    )
    return (executable_path, nar_hashes)
