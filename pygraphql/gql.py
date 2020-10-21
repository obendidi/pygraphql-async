from graphql.language import DocumentNode
from graphql.language.parser import parse
from graphql.language.source import Source


def gql(query_string: str) -> DocumentNode:
    """A gql parser of graphql queries

    Arguments:
        query_string: query string to parse

    Raises:
        Exception: raises and exception when provided query is not of type string
        GraphQLSyntaxError: when teh query syntax is incorrect (can't catch all
        inconsistencies because schema is not provided)

    Returns:
        [DocumentNode]: ast parsed query
    """
    if isinstance(query_string, str):
        source = Source(query_string, "GraphQL request")
        return parse(source)

    raise Exception(
        "Received incompatible query expected type 'str' recieved '{}'.".format(
            type(query_string)
        )
    )
