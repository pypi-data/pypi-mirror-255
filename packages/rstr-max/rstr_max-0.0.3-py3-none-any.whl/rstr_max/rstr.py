from typing import Generator

from sklearn.feature_extraction.text import CountVectorizer

def half(vocab: list[tuple[str, int]]) -> Generator[tuple[str, int], None, None]:
    last_seen = None
    for v, c in vocab:
        if not last_seen:
            last_seen = (v, c)
            continue

        if last_seen[0] in v:
            if last_seen[1] == c:
                last_seen = (v, c)
                continue

        yield last_seen
        last_seen = None


def filter(result: list[tuple[str, int]]) -> list[tuple[str, int]]:
    result = list(result)
    for i, (v, c) in enumerate(result):
        if not c:
            continue

        for j, (v2, c2) in enumerate(result[i + 1:], start=i + 1):
            if not c2:
                continue

            if all((v in v2, c2 == c)):
                result[i] = (v, 0)

    return [x for x in result if x[1]]


def max_repeated_substrings(
        s: str | list[str],
        *args,
        min_len: int = 1,
        min_count: int = 2,
        max_count: int = None,
        max_len: int = None,
        **kwargs
) -> list[tuple[str, int]]:
    # Argument validation
    if isinstance(s, list):
        if any(not isinstance(x, str) for x in s):
            raise ValueError("List should contain only strings")
        pass
    elif isinstance(s, str):
        s = [s]

    assert min_len > 0, "min_len should be equal or greater than 1"
    assert min_count > 0, "min_count should be equal or greater than 1"

    if max_len is None or max_count is None:
        max_ = max(map(len, s))
        max_len = max_len or max_
        max_count = max_count or max_
        del max_

    assert max_len >= min_len, "max_len should be equal or greater than min_len"
    assert max_count >= min_count, "max_count should be equal or greater than min_count"

    # Now we get to business
    cv = CountVectorizer(analyzer='char', ngram_range=(min_len, max_len))
    cv = cv.fit(s)

    counts = cv.transform(s).sum(axis=0).A1

    vocab = cv.get_feature_names_out()

    del cv

    vocab = sorted(zip(vocab, counts))

    result = set(half(vocab))

    vocab = sorted(result, reverse=True)

    result.update(half(vocab))

    del vocab

    result = filter(result)

    result = sorted(result, key=lambda x: x[1], reverse=True)

    result = [x for x in result if min_count <= x[1] <= max_count]
    result = [x for x in result if min_len <= len(x[0]) <= max_len]
    return result
