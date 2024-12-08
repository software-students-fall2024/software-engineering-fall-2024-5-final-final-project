"""
This file contains the tests for the craps functions. It uses seed 50 to make sure tests
can be consistently reproduced.
"""
from craps_func import linebet, buybet
from random import seed
import pytest

seed(50)  # to set the seed

def test_passwin7():
    """Tests that an initial seven is a win for a pass bet"""
    rolls, result = linebet(True)
    assert len(rolls) == 1
    assert result == 'w'

def test_passlose7():
    """Test case where 7 comes before established point"""
    rolls, result = linebet(True)
    assert len(rolls) == 3
    assert result == 'l'

def test_buybet5win():
    """Tests that a buy bet for 5 wins and returns correct odds."""
    rolls, result, odds = buybet(True, 5)
    assert len(rolls) == 2
    assert result == 'w'
    assert odds == 1.5

def test_passwin11():
    """Tests that an initial 11 is a win for pass bet"""
    rolls, result = linebet(True)
    assert len(rolls) == 1
    assert result == 'w'

def test_passlose():
    """Tests that an initial 3 is a loss for a pass bet"""
    rolls, result = linebet(True)
    assert len(rolls) == 1
    assert result == 'l'

def test_buybet10long():
    """Tests that a buy bet for 10 wins"""
    rolls, result, odds = buybet(True, 10)
    assert len(rolls) == 5
    assert result == 'w'
    assert odds == 2

def test_laybet5win():
    """Tests that a lay bet for 5 wins"""
    rolls, result, odds = buybet(False, 5)
    assert len(rolls) == 10
    assert result == 'w'
    assert odds == 2/3

def test_dontpasslose11():
    """Tests that an initial 11 is a loss for dont' pass"""
    rolls, result = linebet(False)
    assert len(rolls) == 1
    assert result == 'l'

def test_dontpasswin():
    """Tests a win for dont pass"""
    rolls, result = linebet(False)
    assert len(rolls) == 3
    assert result == 'w'

def test_buybetloss9():
    """Tests that a buy bet loses"""
    rolls, result, odds = buybet(True, 9)
    assert len(rolls) == 4
    assert result == 'l'
    assert odds == 1.5

def test_laybetlose():
    """Tests a loss for a lay bet"""
    rolls, result, odds = buybet(False, 8)
    assert len(rolls) == 7
    assert result == 'l'
    assert odds == 5/6

def test_dontpassinitialwin():
    """Tests that an initial 3 is a win for dont pass bet"""
    rolls, result = linebet(False)
    assert len(rolls) == 1
    assert result == 'w'

def test_passtie():
    """Tests a tie for a pass bet with seed 20"""
    seed(20)
    rolls, result = linebet(True)
    assert len(rolls) == 1
    assert result == 't'
    seed(50)

def test_dontpasstie():
    """Tests a tie for a dont bass bet with seed 20"""
    seed(20)
    rolls, result = linebet(False)
    assert len(rolls) == 1
    assert result == 't'
    seed(50)