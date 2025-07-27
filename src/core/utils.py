import json
import csv
import os


def read_file(filepath):
    """
    Reads a JSON or CSV file and returns its contents.
    Args:
        filepath (str): Path to the file.
    Returns:
        list or dict: Data from the file. For CSV, returns a list of dicts. For JSON, returns the loaded object.
    Raises:
        ValueError: If the file extension is not supported.
        FileNotFoundError: If the file does not exist.
        Exception: For other IO errors.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    try:
        if ext == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif ext == '.csv':
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
    except Exception as e:
        raise e


def write_data(filepath, data, fieldnames=None):
    """
    Writes data to a JSON or CSV file.
    Args:
        filepath (str): Path to the file.
        data (list or dict): Data to write. For CSV, should be a list of dicts.
        fieldnames (list, optional): List of fieldnames for CSV. Required if writing CSV and data is not empty.
    Raises:
        ValueError: If the file extension is not supported or fieldnames are missing for CSV.
        Exception: For other IO errors.
    """
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    try:
        if ext == '.json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif ext == '.csv':
            if not isinstance(data, list) or (data and not isinstance(data[0], dict)):
                raise ValueError("For CSV, data must be a list of dicts.")
            if not fieldnames:
                if data:
                    fieldnames = list(data[0].keys())
                else:
                    raise ValueError("fieldnames must be provided for empty CSV data.")
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
    except Exception as e:
        raise e