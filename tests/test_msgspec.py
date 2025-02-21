import numpy as np
import pytest

from sunflare.virtual import encode, decode
from sunflare.virtual._bus import _msgpack_dec_hook, _msgpack_enc_hook


def test_list_encoding():
    enc = encode([1, 2, 3])
    dec = decode(enc)

    assert dec == [1, 2, 3]


def test_hooks():
    array = np.array([1, 2, 3])
    ret = _msgpack_enc_hook(array)
    assert isinstance(ret, tuple)
    assert isinstance(ret[0], bytes)
    assert isinstance(ret[1], str)
    assert isinstance(ret[2], tuple)

    original = _msgpack_dec_hook(np.ndarray, ret)
    assert np.array_equal(original, array)

    with pytest.raises(NotImplementedError):
        _msgpack_enc_hook([1, 2, 3])

    non_array = encode([1, 2, 3])
    non_array_ret = _msgpack_dec_hook(list, non_array)
    assert non_array_ret == non_array
