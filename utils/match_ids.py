from typing import List


def generate_match_ids(draw_size: int) -> List[str]:
    """
    Generate main draw match IDs based on draw size.

    Example:
    32 draw -> 31 matches -> ms001 ... ms031
    """

    # Safety guard
    if not isinstance(draw_size, int) or draw_size < 2:
        return []

    total_matches = draw_size - 1
    return [f"ms{i:03d}" for i in range(1, total_matches + 1)]


def generate_qualifier_ids(max_qualy: int = 20) -> List[str]:
    """
    Generate qualifier match IDs up to a reasonable limit.

    ATP qualifier match IDs look like qs001, qs002, etc.
    """

    if not isinstance(max_qualy, int) or max_qualy <= 0:
        return []

    return [f"qs{i:03d}" for i in range(1, max_qualy + 1)]
