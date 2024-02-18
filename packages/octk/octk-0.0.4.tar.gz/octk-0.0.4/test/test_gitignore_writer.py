from octk import projectify
import os

test_path = r'test'

def test_add_gitignore_file():
    projectify.add_gitignore_file(test_path, overwrite=True, template_keys=["python"], custom_gitignore_template=r".gitignore")
    assert os.path.exists(os.path.join(test_path, ".gitignore"))

def test_add_gitignore_file_append():
    projectify.add_gitignore_file(
        test_path, overwrite=True, template_keys=["python"], 
        custom_gitignore_template=r".gitignore", append=True)
    assert os.path.exists(os.path.join(test_path, ".gitignore"))


test_add_gitignore_file()
test_add_gitignore_file_append()