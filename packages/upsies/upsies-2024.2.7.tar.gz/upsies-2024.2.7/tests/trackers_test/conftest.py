import pytest


@pytest.fixture
def assert_config_list_of_choice():
    def assert_config_list_of_choice(items, exp_items, exp_options, exp_description=None):
        assert items == exp_items
        for item in items:
            assert item.options == tuple(sorted(exp_options))

            cls = type(item)
            for option in item.options:
                assert cls(option) == option
                assert cls(option).options == tuple(sorted(exp_options))

            exp_options_string = ', '.join(sorted(exp_options))
            with pytest.raises(ValueError, match=rf'^Not one of {exp_options_string}: foo$'):
                cls('foo')

        if exp_description is not None:
            assert items.description == exp_description

    return assert_config_list_of_choice


@pytest.fixture
def assert_config_number():
    def assert_config_number(number, value, min, max, description=None):
        assert number == value
        assert number.min == min
        assert number.max == max

        cls = type(number)
        for i in range(min, max + 1):
            assert cls(i) == i
            assert cls(i).min == min
            assert cls(i).max == max

        with pytest.raises(ValueError, match=rf'^Minimum is {min}$'):
            cls(min - 1)

        with pytest.raises(ValueError, match=rf'^Maximum is {max}$'):
            cls(max + 1)

        if description is not None:
            assert number.description == description

    return assert_config_number
