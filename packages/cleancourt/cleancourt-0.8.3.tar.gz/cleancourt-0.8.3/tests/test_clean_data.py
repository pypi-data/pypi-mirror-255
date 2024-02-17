import pytest

from cleancourt import clean_data


def test_clean_pha_names():
    """this test ensures that common patterns regarding housing authorities are handled properly"""
    raw_name = 'wise regional housing authority'
    clean_name = clean_data(raw_name)
    assert clean_name == 'wise regional pha'

    raw_name1 = 'norfolk redevelopment housing authority'
    raw_name2 = 'norfolk redevelopment & housing authority'
    clean_name1 = clean_data(raw_name1)
    clean_name2 = clean_data(raw_name2)
    assert clean_name1 == clean_name2

    raw_name = 'portsmouth redevelopment & housing authy'
    clean_name = clean_data(raw_name)
    assert clean_name == 'portsmouth rha'

    raw_name1 = 'prince hall housing authority, inc'
    raw_name2 = 'prince hall housing authority'
    raw_name3 = 'prince hall housing authority, inc.'

    clean_name1 = clean_data(raw_name1)
    clean_name2 = clean_data(raw_name2)
    clean_name3 = clean_data(raw_name3)

    assert clean_name1 == clean_name2
    assert clean_name1 == clean_name3

    raw_name = 'fargo housing and redevelopment authority'
    clean_name = clean_data(raw_name)
    assert clean_name == 'fargo pha'

    raw_name1 = 'flora parke homeowners associa'
    raw_name2 = 'jim homeowners assoc test'

    clean_name1 = clean_data(raw_name1)
    clean_name2 = clean_data(raw_name2)

    assert clean_name1 == 'flora parke hoa'
    assert clean_name2 == 'jim hoa test'

    raw_name1 = 'member 1 federal credit union'
    raw_name2 = 'virginia beach schools federal credit union'

    clean_name1 = clean_data(raw_name1)
    clean_name2 = clean_data(raw_name2)

    assert clean_name1 == 'member 1 fcu'
    assert clean_name2 == 'virginia beach schools fcu'

#test_clean_pha_names()