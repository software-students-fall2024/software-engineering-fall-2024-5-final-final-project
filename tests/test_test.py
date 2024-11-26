import pytest
from app import app

def test_secret():
    assert app.config['SECRET_KEY'] is not None



