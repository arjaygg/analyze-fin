"""
Unit Tests: SpendingQuery - Initialization and basic invariants.
"""


from analyze_fin.queries.spending import SpendingQuery


class TestSpendingQueryInit:
    """Test SpendingQuery initialization."""

    def test_p0_query_can_be_instantiated(self, db_session):
        """
        [P0] GIVEN a valid database session
        WHEN SpendingQuery is instantiated
        THEN query object is created successfully
        """
        session = db_session
        query = SpendingQuery(session)

        assert query is not None
        assert isinstance(query, SpendingQuery)

    def test_p1_query_stores_session_reference(self, db_session):
        """
        [P1] GIVEN a database session
        WHEN SpendingQuery is instantiated
        THEN session is stored for later use
        """
        session = db_session
        query = SpendingQuery(session)
        assert query._session is session

    def test_p1_query_initializes_empty_filters(self, db_session):
        """
        [P1] GIVEN a new SpendingQuery
        WHEN instantiated
        THEN filters list is empty
        """
        query = SpendingQuery(db_session)
        assert query._filters == []


