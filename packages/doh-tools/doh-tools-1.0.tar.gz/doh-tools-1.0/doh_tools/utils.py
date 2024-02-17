#%%
import yaml
from bs4 import BeautifulSoup

def read_config(input_path = 'config/config.yaml'):
    '''
    Reads a yaml file and converts it to a dict.

    Parameters:
        - input_path: Path to the input yaml file

    Returns:
        - yaml_data: A dictionary of the yaml contents
    '''
    read = open(input_path, 'r')
    data = read.read()
    yaml_data = yaml.safe_load(data)
    return yaml_data

def html_tables_to_yaml(input_file):
    '''
    Generate Data Specification yaml from html.

    This function takes an html file or markdown file with html-style content and creates a data specification yaml file of the same name as the input file. 
    Not much can be gleaned from an html table with regards to metadata, but table name, column name, and the actual data values should be consistently captured.

    Parameters:
        - input_file: Path to the html or markdown input file

    Returns:
        - Data Specification: A data specification as a yaml file
    '''
    # Read the HTML file
    with open(input_file, 'r') as f:
        content = f.read()

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    data_spec_yaml = {}

    # Find and parse tables
    table_count = 0
    for table in soup.find_all('table'):
        table_data = []
        table_info = {}
        
        # Extract column names and add placeholder metadata
        columns_info = []
        for th in table.find('tr').find_all('th'):
            column_name = th.get_text().strip()
            columns_info.append({
                'name': column_name,
                'data_type': None,  # Default data type
                'description': None # Default description
            })
        
        # Extract data rows
        for row in table.find_all('tr')[1:]:
            row_data = {}
            for idx, cell in enumerate(row.find_all(['td', 'th'])):
                column_name = columns_info[idx]['name']
                cell_text = cell.get_text().strip()
                row_data[column_name] = cell_text
            table_data.append(row_data)

        # Add metadata for the table
        table_info['name'] = f'table_{table_count+1}'
        table_info['columns'] = columns_info
        table_info['data'] = table_data

        # Add table info to YAML
        data_spec_yaml[f'table_{table_count+1}'] = table_info
        table_count += 1

    # Write YAML to file
    output_file = input_file.replace('.md', '.yaml')
    with open(output_file, 'w') as yaml_file:
        yaml.dump(data_spec_yaml, yaml_file, default_flow_style=False)