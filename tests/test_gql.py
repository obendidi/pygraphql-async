from pygraphql import gql, InvalidQueryType

import pytest
from graphql.error.syntax_error import GraphQLSyntaxError
from graphql.language import DocumentNode


def test_gql_syntax_error():
    query_string = "query {user() {id name}}"
    with pytest.raises(GraphQLSyntaxError):
        gql(query_string)


def test_gql_invalid_query_type():
    query_string = 123
    with pytest.raises(InvalidQueryType):
        gql(query_string)


def test_gql():
    query_string = """
    {
      droid(id: "2001") {
        name
        primaryFunction
      }
    }
    """
    document = gql(query_string)
    assert isinstance(document, DocumentNode)
