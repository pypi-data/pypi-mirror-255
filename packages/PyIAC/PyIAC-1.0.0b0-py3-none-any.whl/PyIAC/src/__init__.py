import os
import PyIAC

def get_directory(folder_name=None):
    """

    """
    if folder_name:

        path_name = os.path.join(PyIAC.__file__.replace(os.path.join(os.path.sep,'__init__.py'),''),folder_name)

    else:

        path_name = os.path.join(PyIAC.__file__.replace(os.path.join(os.path.sep, '__init__.py'), ''))

    return path_name