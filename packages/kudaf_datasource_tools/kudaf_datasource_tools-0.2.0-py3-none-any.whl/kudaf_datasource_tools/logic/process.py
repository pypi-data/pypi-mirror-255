import os 
import pydantic
import logging
from pathlib import Path
from typing import Union, List, Dict, Tuple, Any, TypeVar 
from pyarrow import csv, json, parquet

from kudaf_datasource_tools.logic.models import (
    VariableMetadataInput,
    VariableMetadata,
    InstanceVariable,
    UnitTypeMetadataInput,
    UnitTypeMetadata,
    UnitTypeGlobal,
    UnitTypeShort,
    KeyType,
    ValueDomain,
    RepresentedVariable,
    FileInfo,
    FileType,
    ProjectInfo,
)
from kudaf_datasource_tools.logic.utils import (
    load_json,
    write_json,
    load_yaml,
    replace_enums,
    convert_to_multilingual_dict,
    convert_list_to_multilingual,
    unittype_to_multilingual,
    value_domain_to_multilingual,
)
from kudaf_datasource_tools.logic.exceptions import (
    ValidationError,
    UnregisteredUnitTypeError,
    ParseMetadataError,
)
from kudaf_datasource_tools.logic import (
    temporal_attributes,
    unit_type_variables,
)


BASE_DIR: Path = Path(__file__).parent.parent
TEMPLATE_DIR: Path = BASE_DIR / 'template_api'

ModelType = TypeVar("ModelType")
logger = logging.getLogger()


class MetadataProcess:

    @staticmethod
    def _format_pydantic_error(error: Dict) -> str:
        location = "->".join(
            loc for loc in error["loc"] if loc != "__root__" and not isinstance(loc, int)
        )
        return f'{location}: {error["msg"]}'
    
    def validate_metadata_model(self, Model: ModelType, metadata_json: Dict) -> ModelType:
        try:
            model_obj = Model(**metadata_json)  
        except pydantic.ValidationError as e:
            logger.exception(e)
            error_messages = [
                self._format_pydantic_error(error) for error in e.errors()
            ]
            raise ValidationError("metadata file", errors=error_messages)
        except Exception as e:
            logger.exception(e)
            raise e
        
        return model_obj
    
    def convert_unit_type_to_identifier(self, utype: Dict) -> InstanceVariable:
        try:
            utmodel = UnitTypeMetadata(**utype)
            ivmodel = InstanceVariable(**{
                "name": utmodel.shortName,
                "label": utmodel.name[0].value,
                "dataType": utmodel.dataType,
                "variableRole": "Identifier",
                "keyType": KeyType(**{
                    "name": utmodel.unitType.shortName,
                    "label": utmodel.unitType.name[0].value,
                    "description": utmodel.unitType.description,
                }),
                "representedVariables": [
                    RepresentedVariable(**{
                        "description": utmodel.description,
                        "valueDomain": utmodel.valueDomain,
                    })
                ]
            })
        except pydantic.ValidationError as e:
            logger.exception(e)
            error_messages = [
                self._format_pydantic_error(error) for error in e.errors()
            ]
            raise ValidationError("metadata file", errors=error_messages)
        except Exception as e:
            logger.exception(e)
            raise e 
        return ivmodel

    def insert_instance_variables(self, metadata_input: VariableMetadataInput) -> Tuple[List, Dict]:
        """
        Create instance variable metadata for Identifier, Measure and Attibute Variables
        Create metadata for Datasource-specific Unit Types, if any
        """
        # Identifier Variables: 
        # Could come from pre-defined Global Unit Types or from provided Datasource-specific Unit Types
        ivars = []
        ds_units = []
        for _iv in metadata_input.identifierVariables:
            _utype = _iv.unitType
            if isinstance(_utype, UnitTypeGlobal) and _utype in unit_type_variables.UNIT_TYPE_VARIABLES:
                 _ivmodel = self.convert_unit_type_to_identifier(unit_type_variables.get(_utype))
                 ivars.append(replace_enums(input_dict=_ivmodel.dict(exclude_unset=True)))
            elif isinstance(_utype, UnitTypeMetadataInput):
                # This is a datasource-specific UnitType
                # First create an Identifier Variable out of it (an InstanceVariable)
                if isinstance(_iv.unitType.name, str):
                    # Extract if string before converting to dicts
                    _label = _iv.unitType.name
                else:
                    # Whatever, pick first one
                    _label = _iv.unitType.name[0].get('value', "")
                _utype = unittype_to_multilingual(utype=_utype, default_lang="no")
                _ivdict = {
                    "name": _utype.shortName,
                    "label": _label,
                    "dataType": _iv.unitType.dataType,
                    "variableRole": "Identifier",
                    "keyType": KeyType(**{
                        "name": _utype.shortName,
                        "label": _label,
                        "description": _utype.description,
                    }),
                    "representedVariables": [
                        RepresentedVariable(**{
                            "description": _utype.description,
                            "valueDomain": _utype.valueDomain,
                        })
                    ]
                }
                _ivmodel = self.validate_metadata_model(Model=InstanceVariable, metadata_json=_ivdict)             
                ivars.append(replace_enums(input_dict=_ivmodel.dict(exclude_unset=True)))   

                # Now create the metadata for this new UnitType
                _utdict = _utype.dict(exclude_unset=True)
                # Add a keyType field, as above
                _utdict.update({
                    "unitType": UnitTypeShort(**{
                        "shortName": _utype.shortName,
                        "name": _utype.name,
                        "description": _utype.description,
                    }),
                })
                _utmodel = self.validate_metadata_model(Model=UnitTypeMetadata, metadata_json=_utdict)             
                ds_units.append(_utmodel.dict(exclude_unset=True))
            else:
                raise UnregisteredUnitTypeError
            
        # Measure Variables 
        mvars = []
        for _mv in metadata_input.measureVariables:
            insert_measure = {}
            _mvdict = _mv.dict(exclude_unset=True)
            _utype = _mvdict.get("unitType", "")

            insert_measure["name"] = metadata_input.name
            insert_measure["label"] = _mvdict["label"]
            insert_measure["description"] = _mvdict["description"] if isinstance(_mvdict["description"], list) else [
                            convert_to_multilingual_dict(input_str=_mvdict["description"], default_lang="no")
                        ]
            insert_measure["variableRole"] = "Measure"

            if _utype:
                if isinstance(_utype, UnitTypeGlobal) and _utype in unit_type_variables.UNIT_TYPE_VARIABLES:
                    utmodel = UnitTypeMetadataInput(**unit_type_variables.get(_utype))
                elif isinstance(_utype, dict):
                    utmodel = UnitTypeMetadataInput(**_utype)
                    utmodel = unittype_to_multilingual(utype=utmodel, default_lang="no")
                elif type(_utype) not in [str, UnitTypeMetadataInput]:
                    logger.error(f"UTYPE: {_utype} NOT FOUND")
                    raise UnregisteredUnitTypeError
                
                insert_measure.update({
                    "keyType": KeyType(**{
                        "name": utmodel.shortName,
                        "label":utmodel.name[0].get('value', "") if isinstance(utmodel.name[0], dict) else utmodel.name[0].value,
                        "description": utmodel.description if isinstance(utmodel.description, list) else [
                            convert_to_multilingual_dict(input_str=utmodel.description, default_lang="no")
                        ],
                    }),
                    "representedVariables": [
                        RepresentedVariable(**{
                            "description": utmodel.description,
                            "valueDomain": utmodel.valueDomain,
                        })
                    ]
                })
            else:
                insert_measure.update({
                    "representedVariables": [
                        RepresentedVariable(**{
                            "description": _mvdict["description"] if isinstance(_mvdict["description"], list) else [
                                convert_to_multilingual_dict(input_str=_mvdict["description"], default_lang="no")
                            ],
                            "valueDomain": value_domain_to_multilingual(
                                val_dom=_mvdict.get('valueDomain') if _mvdict.get('valueDomain') else ValueDomain(**{
                                        "uriDefinition": None,
                                        "description": "N/A",
                                        "measurementUnitDescription": "N/A"
                                }), 
                                default_lang="no"
                            ),
                        })
                    ]
                })

            _mvmodel = self.validate_metadata_model(Model=InstanceVariable, metadata_json=insert_measure)         
            mvars.append(replace_enums(input_dict=_mvmodel.dict(exclude_unset=True)))

        # Attribute Variables
        attrvars = [
            temporal_attributes.generate_start_time_attribute(metadata_input.temporalityType),
            temporal_attributes.generate_stop_time_attribute(metadata_input.temporalityType),
        ] # + metadata_input.get("attributeVariables", [])

        instance_vars = {
            "identifierVariables": ivars,
            "measureVariables": mvars,
            "attributeVariables": attrvars,
        }

        return ds_units, instance_vars
    
    def convert_descriptions_to_multilingual(
        self, 
        metadata_input: VariableMetadataInput, 
        default_lang: str = "no"
    ) -> Dict[str, Any]:
        multi_dict = {}
        multilingual_fields = ["populationDescription", "spatialCoverageDescription", "subjectFields"]
        nested_list_fields = ["subjectFields"]
        # Convert string fields to Norwegian multilungual strings if needed
        for field in multilingual_fields:
            field_contents = getattr(metadata_input, field)
            if isinstance(field_contents, list):
                if field in nested_list_fields:
                    multi_dict[field] = convert_list_to_multilingual(
                        input_list=field_contents, 
                        default_lang=default_lang,
                        nested_list=True)
                else:
                    multi_dict[field] = convert_list_to_multilingual(input_list=field_contents, default_lang=default_lang)

        return multi_dict

    def generate(
        self, 
        config_file_path: Path,
        input_data_files_dir: Path,
        output_metadata_dir: Union[Path, None] = None,
        temp_dirs: Dict[str, Any] = None,
        generate_api_files: bool = True,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Generates Kudaf JSON Metadata files (for both Variables and Unit Types) and Variable-to-Data Mappings 
        from a YAML configuration file
        """
        variables = []
        unit_types = []
        files = {}
        mappings = {}

        config_dict = load_yaml(config_file_path)

        if generate_api_files:

            # Update project and datasource info in cookiecutter config file
            cookiecutter_config = load_json(TEMPLATE_DIR / "cookiecutter.json")
            
            projinfo_model = self.validate_metadata_model(
                Model=ProjectInfo, 
                metadata_json=config_dict.get('projectInfo')
            )

            cookiecutter_config['project_name'] = projinfo_model.name
            cookiecutter_config['module_name'] = projinfo_model.name.lower().replace(' ', '_').replace('-', '_')
            cookiecutter_config['author'] = projinfo_model.author
            cookiecutter_config['datasource_name'] = projinfo_model.datasourceName
            cookiecutter_config['datasource_id'] = projinfo_model.datasourceId

            # Process datafiles
            for _dfile in config_dict.get('dataFiles'):
                _in_filemodel = self.validate_metadata_model(Model=FileInfo, metadata_json=_dfile.get('dataFile'))
                if _in_filemodel.fileDirectory is None:
                    # Use CLI-given option if dir not in the file
                    _in_filemodel.fileDirectory = input_data_files_dir

                # Remove trailing slash if present
                if _in_filemodel.fileDirectory[-1] == '/':
                    _in_filemodel.fileDirectory = _in_filemodel.fileDirectory[:-1]

                _infpath = os.path.join(_in_filemodel.fileDirectory, _in_filemodel.fileNameExt)
                if not os.path.exists(_infpath):
                    raise ParseMetadataError(f'File not found: {_infpath}')

                _table = None 
                
                _filename, _fileext = _in_filemodel.fileNameExt.split('.')
                try:
                    FileType(_fileext.lower())
                except ValueError as e:
                    raise ParseMetadataError(
                        f'Not a valid file type: "{_fileext}" for file at: {_infpath}'
                    )

                if _fileext.lower() == 'csv':
                    parseopts = csv.ParseOptions(delimiter=_in_filemodel.csvParseDelimiter)
                    _table = csv.read_csv(_infpath, parse_options=parseopts)
                elif _fileext.lower() == 'json':
                    _table = json.read_json(_infpath)
                elif _fileext.lower() == 'parquet':
                    _table = parquet.read_table(_infpath)

                datafiles_dir = temp_dirs.get('temp_datafiles_dir').name
                _outfpath = os.path.join(datafiles_dir, _filename) + ".parquet"
                # For API generation case only, write out Parquet datafile to Temp dir
                if generate_api_files and _table is not None:          
                    parquet.write_table(table=_table, where=_outfpath)

                files[_filename] =_outfpath

        # Variables metadata
        for _var in config_dict.get('variables'):
            # Validate Input Variable Metadata
            _in_varmodel = self.validate_metadata_model(Model=VariableMetadataInput, metadata_json=_var)

            # Add the Instance (Identifier, Measure, Attribute) Variables
            _ds_units, _inst_vars = self.insert_instance_variables(metadata_input=_in_varmodel)
            _var.update(_inst_vars)
            _descript_vars = self.convert_descriptions_to_multilingual(metadata_input=_in_varmodel, default_lang='no')
            _var.update(_descript_vars)     

            # Validate completed Output Variable Metadata model
            _metmodel = self.validate_metadata_model(Model=VariableMetadata, metadata_json=_var)

            variables.append(_metmodel.dict(exclude_unset=True))

            if generate_api_files:
                # Map parquet data file and columns to Variable name
                _datafile_path = files[_in_varmodel.dataMapping.dataFile.fileNameExt.split('.')[0]]
                _datafilenameext = _datafile_path.split('/')[-1]
                
                mappings[_in_varmodel.name] = {
                    "data_filepath": os.path.join('files', _datafilenameext),
                    "identifier_columns": _in_varmodel.dataMapping.identifierColumns,
                    "measure_columns": _in_varmodel.dataMapping.measureColumns,
                    "measure_columns_accumulated": _in_varmodel.dataMapping.measureColumnsAccumulated,
                    "attribute_columns": _in_varmodel.dataMapping.attributeColumns,
                    "api_url": _in_varmodel.dataMapping.apiUrl,
                    "temporality_type": _in_varmodel.temporalityType.value,
                }

            # Working list of UnitTypes so far
            ut_names = [_u.get('shortName') for _u in unit_types]
            # Add to UnitTypes if new
            unit_types += [_unit for _unit in _ds_units if _unit.get('shortName') not in ut_names]

        # Output files
        if generate_api_files:
            # Metadata files to API folder
            out_dir = temp_dirs.get('temp_metadatafiles_dir').name
            # Update also data mappings in cookiecutter config file and write them to disk
            cookiecutter_config["variable_mappings"] = mappings
            write_json(TEMPLATE_DIR / "cookiecutter.json", cookiecutter_config)
        else:
            # Write out only Metadata files
            out_dir = output_metadata_dir

        write_json(
            filepath=Path(out_dir) / "variables_metadata.json", 
            content=variables
        )
        if unit_types:
            write_json(
                filepath=Path(out_dir) / "unit_types_metadata.json", 
                content=unit_types
            )

        # Set Mappings instance variable, for further processing
        self.mappings = mappings

        return variables, mappings
    
    def check_variable_data(
        self, 
        variable_name: str, 
        limit_rows: int = 65536
    ) -> Any:
        """
        Utility function to check file data
        """
        data = []
        columns = []
        if not self.mappings:
            print('No Variable mappings available yet, please run Metadata process first')
            return
        elif variable_name not in self.mappings:
            print(f'No data found for variable: {variable_name}')
            return

        var_map = self.mappings.get(variable_name)

        if "CALCULATED" not in var_map.get('measure_columns'):
            for type_col in ["identifier_columns", "measure_columns", "attribute_columns"]:
                columns += var_map.get(type_col) if var_map.get(type_col) is not None else []

            filepath = var_map.get('data_filepath')
            
            for csv_chunk in self.file_iterator(
                parquet_file=parquet.ParquetFile(source=filepath, memory_map=True), 
                columns=columns,
                batch_size=limit_rows
            ):
                print(csv_chunk)
                data.append(csv_chunk)
                # Print only one chunk
                break
        else:
            """
            >>>>>
                Insert here  the logic (or function calls) necessary for
                CALCULATED measure column(s).

                See also code PLACEHOLDER in the template API logic at:
                template_api/{{ cookiecutter.module_name }}/app/logic/data.py
            <<<<<<
            """
            ...

        return data

    @staticmethod
    def file_iterator(parquet_file: parquet.ParquetFile, columns: List[str] = None, batch_size = 65536):
        # parquet_file = parquet.ParquetFile(filepath, memory_map=True)
        for record_batch in parquet_file.iter_batches(
            columns=columns,
            batch_size=batch_size
        ):
            yield record_batch.to_pandas().to_csv(index=False)      
                    

metadata_process = MetadataProcess()
