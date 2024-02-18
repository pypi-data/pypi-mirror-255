from typing import Tuple

from .migrate_none_to_1_0 import migrate_board as v0_to_v1
from .minor_migration import get_minor_migration


MIGRATION_SCRIPTS = {
    None: v0_to_v1,
    "1.0": get_minor_migration("1.1"),
    # add here new migrations, e.g.:
    # "1.0": v1_to_v2,
}


def migrate_newest(board_dict: dict) -> Tuple[bool, dict]:
    """
    Migrates the board to the most recent version.

    Parameters
    ----------
    board_dict: The board to migrate as dict.

    Returns
    -------
    A tuple of boolean (did any migration happen) and the migrated board as dict.

    """
    migrated = False
    while True:
        version = board_dict.get("version")
        migration = MIGRATION_SCRIPTS.get(version)
        if migration is None:
            break
        board_dict = migration(board_dict)
        migrated = True

    return migrated, board_dict
