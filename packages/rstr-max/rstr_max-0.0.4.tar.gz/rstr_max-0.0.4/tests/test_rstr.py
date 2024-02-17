from src.rstr_max.rstr import max_repeated_substrings as rstr_max

import lorem

print(
    rstr_max(
        lorem.text(),
        min_count=2,
        min_len=3
    )
)

print(
    rstr_max(
        ["TOTOTITI"],
        # min_count=2,
        # min_len=3,
        # max_len=10
    )
)
