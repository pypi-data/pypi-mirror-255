# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2022)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Upload a new source distribution (tarball) to the IGWN source archive
hosted on software.igwn.org.

Examples:

    $ python igwn-source-upload.py mypackage.tar.gz

or to upload to a subdirectory of the source archive

    $ python igwn-source-upload.py mypackage.tar.gz --target mysuite/

(the trailing slash is important)
"""

import argparse
import logging
import os
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from shutil import which
from unittest import mock

from . import __version__

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

# configure logging
LOGGER = logging.getLogger(__name__.rsplit(".", 1)[-1])
try:
    from coloredlogs import ColoredFormatter as _Formatter
except ImportError:
    _Formatter = logging.Formatter
if not LOGGER.hasHandlers():
    _LOG_HANDLER = logging.StreamHandler()
    _LOG_HANDLER.setFormatter(_Formatter(
        fmt="[%(asctime)s] %(levelname)+8s: %(message)s",
    ))
    LOGGER.addHandler(_LOG_HANDLER)

# map to HTTP URL for new files
HTTP_SLO = "https://software.igwn.org/sources/source"
HTTP_URL = {
    ("software.cgca.uwm.edu", "lscsrc"): HTTP_SLO,
    ("software.igwn.org", "lscsrc"): HTTP_SLO,
    ("software.ligo.org", "lscsrc"): HTTP_SLO,
}

# executables to use
RSYNC = which("rsync") or "rsync"
SSH = which("ssh") or "ssh"

RSYNC_PASSWORD = os.getenv(
    "LSCSRC_RSYNC_PASSWORD",
    os.getenv("RSYNC_PASSWORD"),
)


# -- utilities ----------------------------------

def check_call_verbose(cmd, *args, dry_run=False, **kwargs):
    """Execute `subprocess.check_call` with logging
    """
    cmdstr = " ".join(cmd)
    LOGGER.debug(f"$ {cmdstr}")
    if dry_run:
        return
    try:
        return subprocess.check_call(cmd, *args, **kwargs)
    except subprocess.CalledProcessError:
        LOGGER.critical(f"command failed: {cmdstr!r}")
        raise


def _ssh_cmd(*args):
    cmd = [SSH] + list(args)
    if LOGGER.level > logging.INFO:  # add quiet option
        cmd.insert(-1, "-q")
    if LOGGER.level <= logging.DEBUG:  # add verbose option
        cmd.insert(-1, "-v")
    return cmd


@contextmanager
def ssh_tunnel(
    remotehost,
    remoteport,
    remoteuser=None,
    localport=8730,
    dry_run=False,
):
    """Open (and close) an SSH tunnel in context
    """
    LOGGER.info("opening SSH tunnel")

    if remoteuser is not None:
        remotehost = f"{remoteuser}@{remotehost}"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        sktfile = tmpdir / "controlmaster"

        # This forwards what the $REMOTEHOST calls "localhost" to the
        # $LOCALPORT on the localhost running this script.
        # The issue is that rsync may be bound on $REMOTEHOST to 127.0.0.1,
        # not the public IP.
        ssh_cmd = _ssh_cmd(
            "-C",
            "-f",
            "-L", f"{localport}:localhost:{remoteport}",
            "-M",
            "-N",
            "-S", str(sktfile),
            remotehost,
        )
        check_call_verbose(ssh_cmd, dry_run=dry_run)
        LOGGER.debug("opened ssh tunnel")

        try:
            yield
        finally:
            LOGGER.info("closing ssh tunnel")
            ssh_cmd = _ssh_cmd(
                "-S", str(sktfile),
                "-O", "exit",
                remotehost,
            )
            check_call_verbose(ssh_cmd, dry_run=dry_run)
            LOGGER.debug("closed ssh tunnel")


# -- uploader functions -------------------------

def upload_file(
    source,
    remotehost,
    remoteport=None,
    remoteuser=None,
    localport=8730,
    target=None,
    rsync_module="lscsrc",
    rsync_user="lscsrc",
    rsync_password=RSYNC_PASSWORD,
    dry_run=False,
):
    """Upload a source file to the IGWN source repository

    Parameters
    ----------
    source : `str`, `pathlib.Path`
        the path to the source file to upload

    remotehost : `str`
        the host name of the remote server to upload to

    remoteport : `int`
        the port on the remote host to connect to

    localport : `int`
        the port on this machine to use when connecting

    target : `str`, optional
        the path on the remote machine to sync to

    rsync_module : `str`, optional
        the name of the rsync module to connect to

    rsync_user : `str`, optional
        the name of the rsync user to authenticate as

    rsync_password : `str`, optional
        the password to user when authenticating with rsync

    dry_run : `bool`, optional
        if `False` just print what would have been done, but
        don't actually send anything
    """
    if remoteport is None:
        remotehost, remoteport = remotehost.rsplit(":", 1)

    # construct rsync target
    source = Path(source)
    base = f"{rsync_user}@localhost::{rsync_module}"
    if target and str(target).endswith("/"):
        stub = f"{target.strip('/')}/{source.name}"
    elif target:
        stub = f"{target.lstrip('/')}"
    else:
        stub = f"{source.name}"
    rsync_target = f"{base}/{stub}"

    tunnel = ssh_tunnel(
        remotehost,
        remoteport,
        remoteuser=remoteuser,
        localport=localport,
        dry_run=dry_run,
    )
    with tunnel, mock.patch.dict(os.environ):
        if rsync_password and not dry_run:
            os.environ["RSYNC_PASSWORD"] = rsync_password

        # sync the specified file
        LOGGER.info("executing rsync")
        rsync_cmd = [
            RSYNC,
            "--archive",
            "--delete",
            "--hard-links",
            "--one-file-system",
            "--port", str(localport),
            "--whole-file",
            str(source),
            rsync_target,
        ]
        if LOGGER.level <= logging.DEBUG:
            rsync_cmd.insert(-2, "--verbose")
        check_call_verbose(rsync_cmd, dry_run=dry_run)
    LOGGER.debug("rsync complete")

    # print the URL of the new file
    try:
        remote_base = HTTP_URL[(remotehost, rsync_module)]
    except KeyError:
        pass
    else:
        LOGGER.info(
            f"your file should now be visible from {remote_base}/{stub}",
        )


# -- command-line execution ---------------------

def create_parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        prog="igwn-source-upload",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "source_path",
        help="path to source distribution",
        type=Path,
    )
    parser.add_argument(
        "-t",
        "--target",
        help="path on remote to rync to",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="print verbose logging, can be given multiple times",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=__version__,
        help="print version number and exit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="just print commands that would be executed, "
             "don't actually run them",
    )

    sshargs = parser.add_argument_group("ssh options")
    sshargs.add_argument(
        "-u",
        "--remote-user",
        help="username on remote host",
    )
    sshargs.add_argument(
        "-p",
        "--local-port",
        type=int,
        default=8730,
        help="local port number",
    )
    sshargs.add_argument(
        "-P",
        "--remote-port",
        type=int,
        default=873,
        help="local port number",
    )
    sshargs.add_argument(
        "-r",
        "--remote-host",
        type=str,
        default="software.cgca.uwm.edu",
        help="remote host name",
    )

    rsyncargs = parser.add_argument_group("rsync options")
    rsyncargs.add_argument(
        "-R",
        "--relative",
        action="store_true",
        default=False,
        help="use the rsync --relative option to send relative paths",
    )
    rsyncargs.add_argument(
        "-M",
        "--rsync-module",
        type=str,
        default="lscsrc",
        help="rsync module",
    )
    rsyncargs.add_argument(
        "-U",
        "--rsync-user",
        type=str,
        default="lscsrc",
        help="rsync user",
    )
    rsyncargs.add_argument(
        "-C",
        "--rsync-password",
        type=str,
        default=RSYNC_PASSWORD,
        required=RSYNC_PASSWORD is None,
        help="rsync password, see https://secrets.ligo.org/secrets/433/, "
             "can be stored in ${LSCSRC_RSYNC_PASSWORD} or ${RSYNC_PASSWORD}",
    )

    return parser


def main(args=None):
    """Run the lscsrc uploader
    """
    # parse the command line
    parser = create_parser()
    args = parser.parse_args(args=args)

    # set verbose logging
    LOGGER.setLevel(max(3 - args.verbose, 0) * 10)

    # upload the file
    return upload_file(
        args.source_path,
        args.remote_host,
        remoteport=args.remote_port,
        remoteuser=args.remote_user,
        localport=args.local_port,
        target=args.target,
        rsync_module=args.rsync_module,
        rsync_user=args.rsync_user,
        rsync_password=args.rsync_password,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    sys.exit(main())
