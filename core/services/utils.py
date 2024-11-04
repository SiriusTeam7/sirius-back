import os


def delete_temp_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
        return True
    return False
