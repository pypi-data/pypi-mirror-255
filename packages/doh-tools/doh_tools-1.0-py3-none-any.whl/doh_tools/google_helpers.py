#%%
from google.cloud import secretmanager

#%%
def access_secret_version(project_id, secret_id, version_id="latest"):
    '''
    Get secret value from google secret manager.

    This function takes a project_id (numeric project id), a secret_id (name of secret in google secret manager), and a version_id (default to latest but issues with that, 
    try 1 if getting version error) and returns the secret value.

    Parameters:
        - project_id: The numeric project id
        - secret_id: The name of the secret
        - version_id: Typically 1

    Returns:
        - Secret: The secret stored in google secret manager
    '''
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Extract the payload. The payload is a bytes representation of the secret data.
    payload = response.payload.data.decode("UTF-8")

    return payload


def replace_special_characters_col_headers(df):
    '''
    Replace special characters in column headers of a pandas DataFrame.

    This function is helpful for handling special characters in column headers, which is commmon and allowed in pandas but not allowed
    in a Google BigQuery table. This function will take a pandas df and replace special characters in the column headers with their
    text equivalent based on the hardcoded mapping dictionary you find below. 

    Parameters:
        - df (DataFrame): The pandas DataFrame whose column headers need to be processed.

    Returns:
        - DataFrame: The DataFrame with special characters replaced with text in column headers.
    '''
    # Dictionary mapping special characters to their written-out equivalents
    special_characters_mapping = {
        '%': ' percent ',
        '$': ' dollars ',
        '#': ' hash ',
        '@': ' at ',
        '&': ' and ',
        '+': ' plus ',
        '-': ' minus ',
        '*': ' asterisk ',
        '/': ' slash ',
        '\\': ' backslash ',
        '=': ' equals ',
        ':': ' colon ',
        ';': ' semicolon ',
        '<': ' less_than ',
        '>': ' greater_than ',
        '(': ' left_parenthesis ',
        ')': ' right_parenthesis ',
        '[': ' left_bracket ',
        ']': ' right_bracket ',
        '{': ' left_curly_brace ',
        '}': ' right_curly_brace ',
        '"': ' double_quote ',
        "'": ' single_quote ',
        '`': ' backtick ',
        '~': ' tilde ',
        '!': ' exclamation ',
        '?': ' question ',
        ',': ' comma ',
        '.': ' period ',
        '_': ' underscore ',
        '|': ' pipe ',
        '^': ' caret ',
        '@': ' at ',
        '~': ' tilde '
    }

    # Function to replace special characters
    def replace_chars(value):
        for char, replacement in special_characters_mapping.items():
            value = value.replace(char, replacement)
        return value
    
    # Apply the replacement function to all column headers
    df.columns = [replace_chars(col) for col in df.columns]

    return df