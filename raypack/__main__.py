"""
Create a package for AWS Glue, Ray.io tasks. 

If you are only using included-by-default packages, public packages, pure python packages, 
binary wheel packages, you don't have to do this.

AWS Glue can't handle anything without a binary wheel or private package repositories.

So you have build on a machine that matches the AWS runtime OS (Fedora-like), create a virtual directory,
and then zip it up and upload it to s3.

This tool aims to do that and be pipx installable and work on any OS

Some code generate with ChatGPT (OpenAI)
"""
import os
import zipfile
import sys

def get_site_packages_dir():
    # First, check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment, check the known paths where site-packages could be
        for path in sys.path:
            if 'site-packages' in path:
                return path
    
    # If no virtual environment is detected, we'll try to infer the site-packages path from the environment variable
    poetry_venv_path = os.getenv("POETRY_VIRTUALENVS_PATH")
    if poetry_venv_path:
        # Append the typical structure to get to site-packages from the base venv path.
        # This might differ between platforms and Python versions, so this is a general attempt.
        return os.path.join(poetry_venv_path, "lib", "python" + sys.version[:3], "site-packages")

    # Return None if we can't infer the location
    return None

def package_for_ray(temp_dir_name, files_to_include, output_zip_name):
    if not os.path.exists(temp_dir_name):
        os.makedirs(temp_dir_name)

    # Copy files to the temporary directory
    for file in files_to_include:
        if os.path.basename(file) != "__MACOSX":
            destination_path = os.path.join(temp_dir_name, os.path.basename(file))
            if os.path.isdir(file):
                copy_tree(file, destination_path)
            else:
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                os.replace(file, destination_path)

    # Zip the directory
    with zipfile.ZipFile(output_zip_name, 'w') as zipf:
        for foldername, subfolders, filenames in os.walk(temp_dir_name):
            for filename in filenames:
                if "__MACOSX" not in filename:
                    filepath = os.path.join(foldername, filename)
                    zipf.write(filepath, os.path.relpath(filepath, temp_dir_name))

    print(f"Packaged files saved as {output_zip_name}")

    # Cleanup
    os.rmdir(temp_dir_name)
