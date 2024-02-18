import itertools


def condition_generator(test_parameters: dict[str, list[float | str]]) -> list[dict[str, str | float | int]]:
    """
    General-purpose test condition generator.
    Takes a map of Stepper names as key with the conditions as a list of values. It will
    generate a list of set-conditions in order of the keys and values.

    It generates a set of conditions for each key. The values of each key are iterated
    in order and the keys from last to first.
    The key order should represent significance of change, e.g. how long it takes for a
    condition to be reached.

    To visualize this, an input of {"a": [1, 2], "b": ["foo", "bar"], "c": [3, 4]} will
    result in the following output:
    [
        {"a": 1, "b": "foo", "c": 3},
        {"a": 1, "b": "foo", "c": 4},
        {"a": 1, "b": "bar", "c": 3},
        {"a": 1, "b": "bar", "c": 4},
        {"a": 2, "b": "foo", "c": 3},
        {"a": 2, "b": "foo", "c": 4},
        {"a": 2, "b": "bar", "c": 3},
        {"a": 2, "b": "bar", "c": 4},
    ]
    """

    test_conditions: list[dict[str, str | float | int]] = []
    for idx, e in enumerate(itertools.product(*test_parameters.values())):
        d: dict[str, str | float | int] = {"sequence_number": idx}
        for sub_index, key in enumerate(test_parameters.keys()):
            d[key] = e[sub_index]
        test_conditions.append(d)
    return test_conditions
