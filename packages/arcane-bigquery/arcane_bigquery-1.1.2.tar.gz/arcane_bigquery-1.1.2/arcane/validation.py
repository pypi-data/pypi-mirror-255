from arcane.core.exceptions import BadRequestError

SPECIAL_KEYWORD_PATTERN = [
    "INFORMATION_SCHEMA", "DROP", "ALTER", "SELECT", "WHERE", "FROM", "CREATE", "MERGE", "UNION", "TRUNCATE", "DELETE", "INSERT", "UPDATE"
]

def assert_query_does_not_contain_special_keywords(query: str) -> None:
    """
    Assert that the query does not contain special keywords

    Raises:
        BadRequestError: the query contains special keywords. It is a Forbidden operation
    """

    for keyword in SPECIAL_KEYWORD_PATTERN:
        list_regex = ['\'.*\'', '\".*\"', '`.*`']
        new_query = query

        for regex_pattern in list_regex:
            new_query = re.sub(regex_pattern, '', new_query)
        if re.search(rf"(^{keyword}\W)|(\W{keyword}\W)", new_query, re.IGNORECASE):
                # If it's a comment go back useless to check
            raise BadRequestError(
                f"Forbbiden operation. You use an unauthorized keyword ({keyword}) in your query. ({query})")
