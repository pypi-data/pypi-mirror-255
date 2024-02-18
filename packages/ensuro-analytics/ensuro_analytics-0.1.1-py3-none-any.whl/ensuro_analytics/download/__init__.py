"""
This module contains the functions to download data from Ensuro's API and BigQuery.
"""


def get_from_quote(x, field):
    """
    This function attempts to retrieve a specific field from policies' metadata in the 'quote' column.

    Parameters:
    x (dict): The quote from which to retrieve the field. It is expected to be a dictionary with a "data" key.
    field (str): The name of the field to retrieve from the quote.

    Returns:
    The value of the specified field if it exists, None otherwise.
    """
    try:
        return x["data"][field]
    except:
        return None
