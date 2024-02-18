import os
import shutil
from jinja2 import Template

from pagekey_docgen.config import PageKeySite


def get_files_list(path: str):
    """Walk directory and get all files recursively.
    
    Args:
      path: Directory path to walk.
    """
    result = []
    for root, dirs, files in os.walk(path):
        for cur_file in files:
            cur_file_path = os.path.relpath(os.path.join(root, cur_file))
            result.append(cur_file_path)
    return result

def create_output_directory():
    """Create output directory to copy the generated site into."""
    os.makedirs('build')

def remove_output_directory():
    """Remove the output directory recursively.
    
    Clean the project.
    """
    if os.path.exists('build'):
        shutil.rmtree('build')

def render_file(path: str):
    """Render a docs file to the final HTML site.

    Args:
      path: Path to file to be rendered.
    """
    dirname = os.path.dirname(path)
    if len(dirname) < 1:
        # File is at the top-level of the repo - keep it simple
        dest_dir_relpath = os.path.join('build', 'sphinx')
    else:
        # Handle nested files
        src_dir_relpath = os.path.relpath(os.path.dirname(path))
        dest_dir_relpath = os.path.join('build', 'sphinx', src_dir_relpath)
    # Create directories containing this file if not exists
    os.makedirs(dest_dir_relpath, exist_ok=True)
    # Copy the file over
    # TODO / NOTE: eventually this will do templating too
    shutil.copy(path, dest_dir_relpath)

def get_repo_root(cur_file=__file__):
    """Get root directory of installed package.
    
    Useful for copying files within the package.
    
    Args:
      cur_file: The value of __file__. Included as kwarg for testing purposes.  
    """
    return os.path.dirname(cur_file)

def render_template(filename: str, config: PageKeySite):
    """Render a template file.
    
    Args:
      filename: Name of file within templates directory.
    """
    repo_root = get_repo_root()
    src_path = os.path.join(repo_root, 'templates', filename)
    dest_path = os.path.join('build', 'sphinx', os.path.basename(filename))
    if not os.path.exists('build/sphinx'):
        os.makedirs('build/sphinx')
    file_contents = get_file_as_string(src_path)
    template = Template(file_contents)
    output_string = template.render(config=config)
    write_string_to_file(dest_path, output_string)

def get_file_as_string(filename: str):
    with open(filename, 'r') as file:
        return file.read()

def write_string_to_file(filename: str, data: str):
    with open(filename, 'w') as file:
        file.write(data)
