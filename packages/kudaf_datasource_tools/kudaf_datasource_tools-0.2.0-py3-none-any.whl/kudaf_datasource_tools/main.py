#!/usr/bin/env python
import os 
import shutil 
import tempfile
import typer
from typing_extensions import Annotated
from pathlib import Path
from cookiecutter.main import cookiecutter

from kudaf_datasource_tools.logic.process import metadata_process
from kudaf_datasource_tools.logic.utils import (
    load_json,
    check_filepaths_validity,
)

BASE_DIR: Path = Path(__file__).parent
CONFIG_DIR: Path = BASE_DIR / 'config'
TEMPLATE_DIR: Path = BASE_DIR / 'template_api'


app = typer.Typer()


@app.callback()
def callback():
    """
    Kudaf Datasource Tools
    """
    ...


@app.command(name='metadata')
def gen_metadata(
    config_yaml_path: Annotated[Path, typer.Option(
        help="Absolute path to the YAML configuration file"
    )] = Path.cwd() / 'config.yaml',
    input_data_files_dir: Annotated[Path, typer.Option(
        help="Absolute path to the data files directory"
    )] = Path.cwd(),
    output_metadata_dir: Annotated[Path, typer.Option(
        help="Absolute path to directory where the Metadata files are to be written to" 
    )] = Path.cwd(),
):
    """
    Generate Variables/UnitTypes Metadata  

    JSON metadata files ('variables.json' and maybe 'unit_types.json') will be written to the \n
    (optionally) given output directory. \n

    If any of the optional directories is not specified, the current directory is used as default.

    """
    check_filepaths_validity([config_yaml_path, input_data_files_dir, output_metadata_dir])

    variables, mappings = metadata_process.generate(
        config_yaml_path, input_data_files_dir, output_metadata_dir, generate_api_files=False,
    )

    print(f"Generated Metadata (Variables and UnitTypes) available at: {output_metadata_dir}")

    return variables, mappings


@app.command(name='api')
def gen_api(
    config_yaml_path: Annotated[Path, typer.Option(
        help="Absolute path to the YAML configuration file"
    )] = Path.cwd() / 'config.yaml',
    input_data_files_dir: Annotated[Path, typer.Option(
        help="Absolute path to the data files directory"
    )] = Path.cwd(),
    output_api_dir: Annotated[Path, typer.Option(
        help="Absolute path to directory where the Datasource API folder is to be written to" 
    )] = Path.cwd(),
):
    """
    Generate a Kudaf Datasource REST API back-end 
    """
    # Create temp directories
    temp_dirs = {
        "temp_datafiles_dir": tempfile.TemporaryDirectory(),
        "temp_metadatafiles_dir": tempfile.TemporaryDirectory(),
    }
  
    check_filepaths_validity([config_yaml_path, input_data_files_dir, output_api_dir])

    variables, mappings = metadata_process.generate(
        config_file_path=config_yaml_path,
        input_data_files_dir=input_data_files_dir,
        temp_dirs=temp_dirs,
        generate_api_files=True,
    )
    
    # Initiate cookiecutter
    cookiecutter(
        template=str(TEMPLATE_DIR), 
        output_dir=str(output_api_dir), 
        overwrite_if_exists=True,
        no_input=True
    )

    # Get module name from generated cookiecutter.json file
    cookiecutter_props = load_json(TEMPLATE_DIR / "cookiecutter.json")
    module_name = cookiecutter_props.get('module_name')
    
    # Copy generated Parquet data files from temp directory to generated API folder
    for filename in os.listdir(temp_dirs['temp_datafiles_dir'].name):
        shutil.copyfile(
            src=Path(temp_dirs['temp_datafiles_dir'].name) / filename, 
            dst=Path(output_api_dir) / module_name / 'files' / filename,
        )
        
    # Copy generated JSON metadata files from temp directory to generated API folder
    for filename in os.listdir(temp_dirs['temp_metadatafiles_dir'].name):
        shutil.copyfile(
            src=Path(temp_dirs['temp_metadatafiles_dir'].name) / filename, 
            dst=Path(output_api_dir) / module_name / 'metadata' / filename,
        )

    # Remove temporary directories
    temp_dirs['temp_datafiles_dir'].cleanup()
    temp_dirs['temp_metadatafiles_dir'].cleanup()
  
    # Reset generic cookiecutter.json file in template
    shutil.copyfile(src=CONFIG_DIR / 'cookiecutter.json', dst=TEMPLATE_DIR / 'cookiecutter.json')

    print(f"Generated FastAPI Datasource Backend API available at: {output_api_dir}")
    print(f"Generated Metadata (Variables and UnitTypes) available "
          "in the /metadata folder")

    return variables, mappings
