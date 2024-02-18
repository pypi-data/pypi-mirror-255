from unittest.mock import patch

import pytest

from lims_utils.database import Database, get_session


class FakeSession:
    def close(self):
        pass

    def rollback(self):
        pass


def test_no_session():
    """Should raise exception if there is no session present"""
    db = Database()
    with pytest.raises(Exception):
        db.session


def test_session():
    """Should not raise exception if there is a session present in the context"""
    db = Database()
    fs = FakeSession()

    with patch.object(fs, "close") as mock_session:
        with get_session(lambda: fs):
            db.session

        assert mock_session.called


def test_rollback():
    """Should rollback if unhandled exception occurs whilst in session context"""
    db = Database()
    fs = FakeSession()

    with patch.object(fs, "rollback") as mock_session:
        with pytest.raises(Exception):
            with get_session(lambda: fs):
                db.session
                raise Exception

        assert mock_session.called
