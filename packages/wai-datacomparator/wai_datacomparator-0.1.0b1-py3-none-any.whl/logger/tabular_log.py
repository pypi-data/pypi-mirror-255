from tabulate import tabulate


def format_as_table(log_entry: dict) -> str:
    """Format log entry as a table with tabulate."""
    headers = list(log_entry.keys())
    row = [list(log_entry.values())]

    return tabulate(
        row,
        headers=headers,
        tablefmt='double_grid',
        colalign='center',
        stralign="center",
        rowalign="center",
        numalign="center"
    )
