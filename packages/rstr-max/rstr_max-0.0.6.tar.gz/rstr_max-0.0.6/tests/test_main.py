from src.rstr_max.main import max_repeated_substrings as rstr_max

import lorem

print(
    rstr_max(
        ["TOTOTITI"],
        min_count=1,
        min_len=1
    )
)

lt = lorem.text()

print(lt)
print(
    rstr_max(
        lt,
        min_count=2,
        min_len=4
    )
)
