


from micropype.utils import merge_dicts


def test_dict_merge():
    a = {
        "a": 0,
        "b": {
            1: 200,
            2: 300
        }
    }

    b = {
        "b": {
            2: 400,
            4: 101
        }
    }

    c = merge_dicts(a, b)
    print(c)
    assert(c["a"] == 0)
    assert(c["b"][4] == 101)
    assert(c["b"][4] == 101)