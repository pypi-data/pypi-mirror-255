# Metadata models adapted from https://github.com/statisticsnorway/microdata-tools/blob/master/microdata_tools/validation/model/metadata.py
# Under MIT License
# Copyright (c) 2023 Statistics Norway

import datetime
from enum import Enum
from typing import Optional, Union, List, Dict, Any 

from pydantic import BaseModel, conlist, root_validator, Extra


class TemporalityType(str, Enum):
    FIXED = "FIXED"
    STATUS = "STATUS"
    ACCUMULATED = "ACCUMULATED"
    EVENT = "EVENT"


class DataType(str, Enum):
    STRING = "STRING"
    LONG = "LONG"
    DATE = "DATE"
    DOUBLE = "DOUBLE"


class SensitivityLevel(str, Enum):
    PUBLIC = "PUBLIC"
    NONPUBLIC = "NONPUBLIC"


class LanguageCode(str, Enum):
    no = "no"
    nb = "nb"
    nn = "nn"
    en = "en"


class UnitTypeGlobal(str, Enum):
    PERSON = "PERSON"
    VIRKSOMHET = "VIRKSOMHET"
    FORETAK = "FORETAK"
    KOMMUNE = "KOMMUNE"
    FYLKE = "FYLKE"


class UnitIdTypeGlobal(str, Enum):
    FNR = "FNR"
    ORGNR = "ORGNR"
    KOMMUNEID = "KOMMUNEID"
    FYLKEID = "FYLKEID"


class MultiLingualString(BaseModel):
    languageCode: LanguageCode
    value: str


class DataRevision(BaseModel, extra=Extra.forbid):
    description: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]
    temporalEndOfSeries: bool


class KeyType(BaseModel):
    name: str
    label: str
    description: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]


class CodeListItem(BaseModel, extra=Extra.forbid):
    code: str
    categoryTitle: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]
    validFrom: Optional[Union[str, None]]
    validUntil: Optional[Union[str, None]]

    # @root_validator(skip_on_failure=True)
    # @classmethod
    # def validate_code_list_item(cls, values):
    #     def validate_date_string(field_name: str, date_string: str):
    #         try:
    #             datetime.datetime(
    #                 int(date_string[:4]),
    #                 int(date_string[5:7]),
    #                 int(date_string[8:10]),
    #             )
    #         except ValueError as e:
    #             raise ValueError(
    #                 f'Invalid {field_name} date for {values["code"]}. '
    #                 "Date format: YYYY-MM-DD"
    #             ) from e

    #     validate_date_string("validFrom", values["validFrom"])
    #     if values.get("validUntil", None) is not None:
    #         validate_date_string("validUntil", values["validUntil"])
    #     return values


class SentinelItem(BaseModel, extra=Extra.forbid):
    code: str
    categoryTitle: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]


class ValidPeriod(BaseModel, extra=Extra.forbid):
    start: Optional[Union[str, None]]
    start: Optional[Union[str, None]]


class ValueDomain(BaseModel, extra=Extra.forbid):
    description: Optional[Union[
        str, conlist(MultiLingualString, min_items=1)
    ]]
    measurementType: Optional[str]
    measurementUnitDescription: Optional[Union[
        str, conlist(MultiLingualString, min_items=1)
    ]    ]
    uriDefinition: Optional[List[Union[str, None]]]
    codeList: Optional[conlist(CodeListItem, min_items=1)]
    sentinelAndMissingValues: Optional[List[SentinelItem]]

    # @root_validator(skip_on_failure=True)
    # @classmethod
    # def validate_value_domain(cls, values: dict):
    #     def raise_invalid_with_code_list(field_name: str):
    #         raise ValueError(
    #             f"Can not add a {field_name} in a valuedomain with a codeList"
    #         )

    #     if values.get("codeList", None) is not None:
    #         if values.get("description", None) is not None:
    #             raise_invalid_with_code_list("description")
    #         if values.get("measurementType", None) is not None:
    #             raise_invalid_with_code_list("measurementType")
    #         if values.get("measurementUnitDescription", None) is not None:
    #             raise_invalid_with_code_list("measurementUnitDescription")
    #     elif values.get("description", None) is not None:
    #         if values.get("sentinelAndMissingValues", None) is not None:
    #             raise ValueError(
    #                 "Can not add sentinelAndMissingValues "
    #                 "in valuedomain with a description"
    #             )
    #     else:
    #         raise ValueError(
    #             "A valueDomain must contain either a codeList "
    #             "or a description"
    #         )
    #     return values


class UnitTypeShort(BaseModel, extra=Extra.ignore):
    shortName: str
    name: conlist(MultiLingualString, min_items=1)
    description: conlist(MultiLingualString, min_items=1)


class UnitTypeMetadata(BaseModel, extra=Extra.ignore):
    shortName: str
    name: conlist(MultiLingualString, min_items=1)
    description: conlist(MultiLingualString, min_items=1)
    dataType: Optional[DataType]
    valueDomain: Optional[ValueDomain]
    validPeriod: Optional[ValidPeriod]
    unitType: UnitTypeShort


class RepresentedVariable(BaseModel, extra=Extra.ignore):
    description: conlist(MultiLingualString, min_items=1)
    validPeriod: Optional[ValidPeriod]
    valueDomain: Optional[ValueDomain]


class InstanceVariable(BaseModel):
    name: str
    label: Optional[str]
    variableRole: Optional[str]
    dataType: Optional[DataType]
    format: Optional[str]
    keyType: Optional[KeyType]
    uriDefinition: Optional[List[Union[str, None]]]
    representedVariables: conlist(RepresentedVariable, min_items=1) 


class VariableMetadata(BaseModel, extra=Extra.ignore):
    name: str
    temporalityType: TemporalityType
    sensitivityLevel: SensitivityLevel
    populationDescription: conlist(Union[
        str, MultiLingualString
    ], min_items=1)
    spatialCoverageDescription: Optional[conlist(Union[
        str, MultiLingualString
    ], min_items=1)]
    subjectFields: conlist(Union[
        str, conlist(MultiLingualString, min_items=1)
    ], min_items=1)
    updatedAt: Optional[str]  
    dataRevision: Optional[DataRevision] 
    identifierVariables: conlist(InstanceVariable, min_items=1)
    measureVariables: conlist(InstanceVariable, min_items=1)
    attributeVariables: Optional[List[Dict[str, Any]]]


#################################################################
# INPUT DATA: API & DATASET DESCRIPTION INFO (from CONFIG.YAML) #
#################################################################

class ProjectInfo(BaseModel):
    name: str
    author: str
    datasourceName: str
    datasourceId: str

class ApiInfo(BaseModel):
    baseUrl: str
    openapiSpecUrl: Optional[str] = 'openapi.json'


class FileType(str, Enum):
    csv = "csv"
    json = "json"
    parquet = "parquet"


class FileInfo(BaseModel):
    fileNameExt: str 
    csvParseDelimiter: Optional[str] = ","  # Only needed for CSV files
    fileDirectory: Optional[str] = 'datasource_tools/files/data/input'  # There exists a default dir
    validPeriod: Optional[ValidPeriod]


class DataMapping(BaseModel):
    dataFile: Optional[FileInfo]
    identifierColumns: Optional[conlist(str, min_items=1)]
    measureColumns: Optional[conlist(str, min_items=1)]
    measureColumnsAccumulated: Optional[bool] = False
    attributeColumns: Optional[conlist(str, min_items=1)]
    apiUrl: Optional[str]


class UnitTypeMetadataInput(BaseModel, extra=Extra.ignore):
    shortName: str
    name: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]
    description: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]
    dataType: Optional[DataType]
    format: Optional[str]
    valueDomain: Optional[ValueDomain]
    validPeriod: Optional[ValidPeriod]


class IdentifierVariableInput(BaseModel, extra=Extra.forbid):
    unitType: Union[UnitTypeGlobal, UnitTypeMetadataInput]  # If not a UnitTypeGlobal, then it must have been previously defined as IdentifierVariable


class MeasureVariableInput(BaseModel, extra=Extra.ignore):
    unitType: Optional[Union[UnitTypeGlobal, UnitTypeMetadataInput]]  # If not a UnitTypeGlobal, then it must have been previously defined as IdentifierVariable
    label: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]  # 20231107 DD changed from 'name' to avoid confusion
    description: Union[
        str, conlist(MultiLingualString, min_items=1)
    ]
    dataType: Optional[DataType]
    uriDefinition: Optional[List[Union[str, None]]]
    format: Optional[str]
    valueDomain: Optional[ValueDomain]
    validPeriod: Optional[ValidPeriod]

    # @root_validator(skip_on_failure=True)
    # @classmethod
    # def validate_measure(cls, values: dict):
    #     def raise_invalid_with_unit_type(field_name: str):
    #         raise ValueError(
    #             f"Can not set a {field_name} in a measure variable "
    #             "together with a unitType"
    #         )

    #     if values.get("unitType", None) is not None:
    #         if values.get("dataType", None) is not None:
    #             raise_invalid_with_unit_type("dataType")
    #         if values.get("valueDomain", None) is not None:
    #             raise_invalid_with_unit_type("valueDomain")
    #     else:
    #         if values.get("dataType", None) is None:
    #             raise ValueError("Missing dataType in measure variable")
    #         if values.get("valueDomain", None) is None:
    #             raise ValueError("Missing valueDomain in measure variable")
    #     return values


class VariableMetadataInput(BaseModel):
    name: str
    temporalityType: TemporalityType
    sensitivityLevel: SensitivityLevel
    populationDescription: conlist(Union[
        str, MultiLingualString
    ], min_items=1)
    spatialCoverageDescription: Optional[conlist(Union[
        str, MultiLingualString
    ], min_items=1)]
    subjectFields: conlist(Union[
        str, conlist(MultiLingualString, min_items=1)
    ], min_items=1)
    updatedAt: Optional[str]  
    dataRevision: Optional[DataRevision]  
    identifierVariables: conlist(IdentifierVariableInput, min_items=1) 
    measureVariables: conlist(MeasureVariableInput, min_items=1) 
    dataMapping: Optional[DataMapping]
