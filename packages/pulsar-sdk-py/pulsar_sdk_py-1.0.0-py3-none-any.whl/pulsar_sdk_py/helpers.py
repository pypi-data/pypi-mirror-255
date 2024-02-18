def filter_non_empty_params(**kwargs) -> dict:
    """
    Filter out any key-value pairs from a dictionary where the value is None.

    This function is used to remove any parameters that are not specified from a dictionary of key-value
    pairs. It can be used in various contexts where optional parameters may be specified and should be
    filtered out if they are not set.

    Args:
        **kwargs: A dictionary of key-value pairs to filter.

    Returns:
        dict: A new dictionary containing only the key-value pairs where the value is not None.

    """

    return {k: v for k, v in kwargs.items() if v is not None}
