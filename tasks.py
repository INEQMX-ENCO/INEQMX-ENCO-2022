from invoke import task 
import shutil
import pathlib

@task
def requirements(c):
    c.run("python -m pip install -U pip")
    c.run("python -m pip install -r requirements.txt")

@task
def download_data(c):
    print(">>> Downloading raw data...")
    c.run("python modules/dataset_modules/data_downloader.py")

@task
def transform_data(c):
    print(">>> Transforming raw data...")
    c.run("python modules/dataset_modules/data_clean_enco.py")
    c.run("python modules/dataset_modules/data_clean_enigh.py")
    c.run("python modules/dataset_modules/data_clean_shp.py")
    c.run("python modules/dataset_modules/data_clean_censo.py")

@task
def clean_data(c):
    print(">>> Cleaning up intermediate files...")

    # Define the main directories to clean
    main_directories = ['data/interim', 'data/raw']

    # For each main directory, iterate through its subdirectories
    for main_dir in main_directories:
        path = pathlib.Path(main_dir)

        # Target each subdirectory within the main directory (e.g., data/raw/enigh, data/raw/enco)
        for subdir in path.iterdir():
            if subdir.is_dir():
                # Delete all files and subdirectories within this subdir
                for item in subdir.rglob('*'):
                    if item.is_file():
                        item.unlink()  # Delete file
                    elif item.is_dir():
                        shutil.rmtree(item)  # Recursively delete subdirectory if it has contents

    print(">>> Clean up complete!")

@task
def clean(c):
    print(">>> Deleting compiled Python files...")
    for pyc in pathlib.Path('.').rglob('*.py[co]'):
        pyc.unlink()
    for pycache in pathlib.Path('.').rglob('__pycache__'):
        pycache.rmdir()

@task
def lint(c):
    c.run("flake8 proyecto_ic_mcd")
    c.run("isort --check --diff --profile black proyecto_ic_mcd")
    c.run("black --check --config pyproject.toml proyecto_ic_mcd")

@task
def format(c):
    c.run("black --config pyproject.toml proyecto_ic_mcd")

@task
def generate_data_vis(c):
    print(">>> Generating visualizations...")
    c.run("python modules/scripts/generate_data_vis.py")

@task
def build_docs(c):
    print(">>> Building documentation...")
    c.run("mkdocs build")

@task
def deploy_docs(c):
    print(">>> Deploying MkDocs site to GitHub Pages...")
    c.run("mkdocs gh-deploy --force")

@task
def full_pipeline(c):
    download_data(c)
    transform_data(c)
    generate_data_vis(c)

@task
def deploy(c):
    generate_data_vis(c)
    deploy_docs(c)
