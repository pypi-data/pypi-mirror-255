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

    result = sorted(filter(lambda x: min_count <= x[1] <= max_count, result), key=lambda x: x[1], reverse=True)

    return result


if __name__ == '__main__':

    rstr_max = max_repeated_substrings(
        "Salut, j'essayais des trucs avec le rstr et je me demandais si"
        " t'avais des anciens résultats de la rstrisation pour tester le script ?",
        min_count=2,
        min_len=3
    )

    print(rstr_max)


