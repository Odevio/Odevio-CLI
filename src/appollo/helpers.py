import os
import shutil


def zip_directory(directory_path):
    """ Archives a directory in a zip file."""
    shutil.make_archive(os.path.join(os.getcwd(), '.app'), "zip", directory_path)


def print_validation_error(console, response_dict):
    """ Pretty print helper for validation errors in the console"""
    error = response_dict.pop('non_field_errors', None)
    if error is not None:
        console.print(f"Error: {error}")
    for field, errors in response_dict.items():
        if errors is str:
            console.print(f"Error: for {field} - {list(errors)}")
        else:
            console.print(f"Error: for {field} - {errors}")
