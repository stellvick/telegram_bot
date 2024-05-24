import os
import shutil


class FolderUtils:
    @staticmethod
    def create_file(folder_path: str, file_name: str):
        if not os.path.exists(folder_path):
            print("Creating folder: " + folder_path)
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, file_name)
        if not os.path.exists(file_path):
            print("Creating file: " + file_path)
            with open(file_path, 'w'):
                pass

    @staticmethod
    def create_folder(folder_path: str):
        if not os.path.exists(folder_path):
            print("Creating folder: " + folder_path)
            os.makedirs(folder_path)

    @staticmethod
    def delete_folder(folder_path: str):
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

    @staticmethod
    def delete_files_in_folder(folder_path: str):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    @staticmethod
    def get_files_in_folder(folder_path: str):
        return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    @staticmethod
    def get_folders_in_folder(folder_path: str):
        return [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]

    @staticmethod
    def get_files_in_folder_recursively(folder_path: str):
        file_list = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list

    @staticmethod
    def get_folders_in_folder_recursively(folder_path: str):
        folder_list = []
        for root, dirs, files in os.walk(folder_path):
            for dir_ in dirs:
                folder_list.append(os.path.join(root, dir_))
        return folder_list

    @staticmethod
    def get_files_in_folder_with_extension(folder_path: str, extension: str):
        return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))
                and f.endswith(extension)]

    @staticmethod
    def get_files_in_folder_recursively_with_extension(folder_path: str, extension: str):
        file_list = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(extension):
                    file_list.append(os.path.join(root, file))
        return file_list