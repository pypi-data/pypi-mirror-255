#
# This is an auto-generated file.  DO NOT EDIT!
#

SHASH = "430648f7df949b91819d62a5c2d5a5c49d1d67217fb3474ee31e0c78e5ffbd43"

from ansys.systemcoupling.core.adaptor.impl.types import *

from .clear_state import clear_state
from .delete_snapshot import delete_snapshot
from .open import open
from .open_snapshot import open_snapshot
from .save import save
from .save_snapshot import save_snapshot


class case_root(Container):
    """
    'root' object
    """

    syc_name = "CaseCommands"

    command_names = [
        "clear_state",
        "delete_snapshot",
        "open",
        "open_snapshot",
        "save",
        "save_snapshot",
    ]

    clear_state: clear_state = clear_state
    """
    clear_state command of case_root.
    """
    delete_snapshot: delete_snapshot = delete_snapshot
    """
    delete_snapshot command of case_root.
    """
    open: open = open
    """
    open command of case_root.
    """
    open_snapshot: open_snapshot = open_snapshot
    """
    open_snapshot command of case_root.
    """
    save: save = save
    """
    save command of case_root.
    """
    save_snapshot: save_snapshot = save_snapshot
    """
    save_snapshot command of case_root.
    """
