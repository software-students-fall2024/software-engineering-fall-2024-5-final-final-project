import pytest
from app import create_app

def test_secret():
    app=create_app()
    assert app.config['SECRET_KEY'] is not None



