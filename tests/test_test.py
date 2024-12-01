import pytest
import app from app

def test_secret():
    assert app.config['SECRET_KEY'] is not None



