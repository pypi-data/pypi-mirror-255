from sl_optimizer.utils import is_struct


def test_is_struct():
    assert is_struct("t_struct(Person)")


def test_is_struct_fail():
    assert not is_struct("t_uint256")
    assert not is_struct("(Person)t_struct")
