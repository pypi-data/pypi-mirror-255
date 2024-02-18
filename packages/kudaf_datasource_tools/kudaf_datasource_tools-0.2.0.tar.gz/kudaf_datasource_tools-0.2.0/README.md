# KUDAF Datasource CLI Tools

This is a set of Command Line Interface (CLI) tools to facilitate the technical tasks requirered from Data Providers that want to make their data available on the KUDAF data-sharing platform.  

The CLI can create the following Kudaf Data Source components: 
1. Variables Metadata, and /or
2. REST API Datasource back-end (including variables metadata and possibly even the data files themselves)

---

## About KUDAF

(Summary info and links for the Kudaf initiative)

--- 

## High-level workflow for Data Source administrators

(Summary of the process for Datasource admins to make their data available in KUDAF, and where these CLI Tools fit in that journey)

--- 

## Local installation instructions (Linux/Mac)  


### Make sure Python3 is installed on your computer (versions from 3.8 up to 3.11 should work fine)

\$ `python3 --version` 

### Navigate to the folder chosen to contain this project

\$ `cd path/to/desired/folder` 


### Create a Python virtual environment and activate it  

\$ `python3 -m venv .venv` 

This created the virtualenv under the hidden folder `.venv`  

Activate it with: 

\$ `source .venv/bin/activate`  

### Install Kudaf Datasource Tools and other required Python packages 

\$ `pip install kudaf_datasource_tools`  

---

## Creating a YAML configuration file

Click here for a [basic YAML syntax tutorial](https://realpython.com/python-yaml/#yaml-syntax)  


### Example YAML configuration file

The following file is included in the package and can be found in the `datasource_tools/config` folder:  

`config_example.yaml`  

```yaml
---

projectInfo:
  name: "Kudaf_datasource_API_my_Datasource_Name"
  author: Author Name
  datasourceName: "my_Datasource_Name"
  datasourceId: "my-FeideKundeportal-Datasource-UUID"

dataFiles:

- dataFile: &mydatafile
    fileNameExt: mydatafile.csv
    csvParseDelimiter: ";"  # Valgfritt (som standard ","). Angir tegnet som brukes i CSV-filen for å skille verdier innenfor hver rad
    fileDirectory: /path/to/my/datafiles/directory  # Bare nødvendig hvis forskjellig fra gjeldende katalog

unitTypes: 

- MIN_ENHETSTYPE: &min_enhetstype  # Bare nødvendig hvis forskjellig fra de globale enhetstypene: PERSON/VIRKSOMHET/KOMMUNE/FYLKE
    shortName: MIN_ENHETSTYPE
    name: Kort identifikasjonsetikett
    description: Detaljert beskrivelse av denne enhetstypen
    dataType: LONG  # En av STRING/DATE/LONG/DOUBLE

variables:

- name: VARIABELENS_NAVN
  temporalityType: EVENT  # En av FIXED/EVENT/STATUS/ACCUMULATED
  sensitivityLevel: NONPUBLIC  # En av PUBLIC/NONPUBLIC
  populationDescription: 
  - Beskrivelse av populasjonen som denne variabelen måler
  spatialCoverageDescription:
  - Norge
  - Annen geografisk beskrivelse som gjelder disse dataene
  subjectFields: 
  - Temaer/konsepter/begreper som disse dataene handler om
  identifierVariables:
  - unitType: *min_enhetstype  # Kan også være en av de globale enhetstypene: PERSON/VIRKSOMHET/KOMMUNE/FYLKE
  measureVariables: 
  - label: Kort etikett på hva denne variabelen måler/viser
    description: Detaljert beskrivelse av hva denne variabelen måler/viser
    dataType: STRING  # En av STRING/LONG/DATE/DOUBLE
  dataMapping: 
    dataFile: *mydatafile
    identifierColumns:
    - Min_Identificatorkolonne  # CSV-filkolonne for identifikatoren
    measureColumns:
    - Min_Målkolonnen  # CSV-filkolonne for det som måles
    attributeColumns:   # Kun nødvendig for EVENT/STATUS/ACCUMULATED temporalityType(s)
    - Start_Time  # CSV-filkolonnen for starttidspunktet
    - End_Time  # CSV-filkolonne for sluttidspunktet

- name: VARIABELENS_NAVN_ACCUM
  temporalityType: ACCUMULATED  # En av FIXED/EVENT/STATUS/ACCUMULATED
  sensitivityLevel: NONPUBLIC  # En av PUBLIC/NONPUBLIC
  populationDescription: 
  - Beskrivelse av populasjonen som denne variabelen måler
  spatialCoverageDescription:
  - Norge
  - Annen geografisk beskrivelse som gjelder disse dataene
  subjectFields: 
  - Temaer/konsepter/begreper som disse dataene handler om
  identifierVariables:
  - unitType: *min_enhetstype  # Kan også være en av de globale enhetstypene: PERSON/VIRKSOMHET/KOMMUNE/FYLKE
  measureVariables: 
  - label: Kort etikett på hva denne variabelen måler/viser
    description: Detaljert beskrivelse av hva denne variabelen måler/viser
    dataType: LONG  # Hvis akkumulerte data må summeres, bør dette enten være en av LONG/DOUBLE
  dataMapping: 
    dataFile: *mydatafile
    identifierColumns:
    - Min_Identificatorkolonne  # CSV-filkolonne for identifikatoren
    measureColumns:
    - Min_Målkolonnen  # CSV-filkolonne for det som måles
    measureColumnsAccumulated: False # Valgfritt (True/False, som standard False). Angir om dataene i filen allerede er akkumulert
    attributeColumns:   # Kun nødvendig for EVENT/STATUS/ACCUMULATED temporalityType(s)
    - Start_Time  # CSV-filkolonnen for starttidspunktet
    - End_Time  # CSV-filkolonne for sluttidspunktet
... 

```

---

## Kudaf Datasource Tools CLI operation

Navigate to the project directory and activate the virtual environment (**only if not already activated**): 

\$ `source .venv/bin/activate`  

The **`kudaf-generate` command** should be now activated. This is the main entry point to the CLI's functionalities.


### Displaying the help menus 

\$ **`kudaf-generate --help`**  
 

    Usage: kudaf-generate [OPTIONS] COMMAND [ARGS]...
    
    Kudaf Datasource Tools                                                                                             
                                                                                                                        
    ╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ --install-completion          Install completion for the current shell.                                          │
    │ --show-completion             Show completion for the current shell, to copy it or customize the installation.   │
    │ --help                        Show this message and exit.                                                        │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
    ╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ api                 Generate a Kudaf Datasource REST API back-end                                                │
    │ metadata            Generate Variables/UnitTypes Metadata                                                        │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

As we can see, there are **two sub-commands** available: **`api`** and  **`metadata`**. 

We can obtain **help** on them as well: 

\$ **`kudaf-generate api --help`**  

                                                                                                                        
    Usage: kudaf-generate api [OPTIONS]                                                                                
                                                                                                                        
    Generate a Kudaf Datasource REST API back-end                                                                      
                                                                                                                        
    ╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ --config-yaml-path            PATH  Absolute path to the YAML configuration file                                 │
    │                                     [default: /home/me/current/directory/config.yaml]                            │
    │ --input-data-files-dir        PATH  Absolute path to the data files directory                                    │
    │                                     [default: /home/me/current/directory]                                        │
    │ --output-api-dir              PATH  Absolute path to directory where the Datasource API folder is to be written  │
    │                                     to                                                                           │
    │                                     [default: /current/directory]                                                │
    │ --help                              Show this message and exit.                                                  │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯


\$ **`kudaf-generate metadata --help`**  


    Usage: kudaf-generate metadata [OPTIONS]                                                                           
                                                                                                                        
    Generate Variables/UnitTypes Metadata                                                                              
    JSON metadata files ('variables.json' and maybe 'unit_types.json') will be written to the                          
    (optionally) given output directory.                                                                               
    If any of the optional directories is not specified, the current directory is used as default.                     
                                                                                                                        
    ╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ --config-yaml-path            PATH  Absolute path to the YAML configuration file                                 │
    │                                     [default: /home/me/current/directory/config.yaml]                            │
    │ --output-metadata-dir         PATH  Absolute path to directory where the Metadata files are to be written to     │
    │                                     [default: /home/me/current/directory]                                        │
    │ --help                              Show this message and exit.                                                  │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯


### Generating metadata only from a YAML configuration file 

\$ **`kudaf-generate metadata --config-yaml-path /home/me/path/to/config.yaml --output-metadata-dir /home/me/path/to/metadata/folder`**  


### Generating an API 

\$ **`kudaf-generate api --config-yaml-path /home/me/path/to/config.yaml --output-api-dir /home/me/path/to/api/folder`**  

---

## Local API launch

Navigate to the folder containing the generated API:

\$ `cd /home/me/path/to/api/folder` 

### Create a Python virtual environment and activate it  

\$ `python3 -m venv .venv` 

This created the virtualenv under the hidden folder `.venv`  

Activate it with: 

\$ `source .venv/bin/activate`  

### Install needed Python packages 

\$ `pip install -r requirements.txt` 

### Launch the Kudaf Datasource API 

\$ `uvicorn app.main:app` 

### Browser: Navigate to the the API's interactive documentation at: 

**`http://localhost:8000/docs`** 

---

## Docker API launch (Linux)

### Install Docker for your desktop 

Follow instructions for your desktop model at `https://docs.docker.com/desktop/`  

### Navigate to the folder containing the generated API:

\$ `cd /home/me/path/to/api/folder`

### Create a Docker image 

\$ **`sudo docker build -t my-kudaf-datasource-image .`**  

(Note: The **last `.`** in the above command is important! Make sure it's entered like that )

### Create and launch a Docker container for the generated image 

\$ **`sudo docker run -d --name my-kudaf-datasource-container -p 9000:8000 my-kudaf-datasource-image`**  


### Browser: Navigate to the the API's interactive documentation at: 

**`http://localhost:9000/docs` 


---

## Developers

### Download the package to your computer

#### Option A: Installation from repository:

Open up a Terminal window and clone the repo locally:

\$ `git clone https://gitlab.sikt.no/kudaf/kudaf-datasource-tools.git`  


#### Option B: Installation from source:

1. Open up your **browser** and navigate to the project's GitLab page: **`https://gitlab.sikt.no/kudaf/kudaf-datasource-tools`**  

2. Once there, **download a ZIP file with the source code**  

![Download ZIP file](static/kdst_download.png)

3. Move the zipped file to whichever directory you want to use for this installation

4. Open a **Terminal window and navigate** to the directory where the zipped file is

5. **Unzip the downloaded file**, it will create a folder called `kudaf-datasource-tools-main` 

6. Switch to the newly created folder 

\$ `cd path/to/kudaf-datasource-tools-main` 


### Make sure Python3 is installed on your computer (versions from 3.8 up to 3.11 should work fine)

\$ `python3 --version` 


### Install Poetry (Python package and dependency manager) on your computer 

Full Poetry documentation can be found here: [`https://python-poetry.org/docs/`](https://python-poetry.org/docs/) 

The **official installer** should work fine on the command line for Linux, macOS and Windows: 

\$ `curl -sSL https://install.python-poetry.org | python3 -` 

If the installation was successful, configure this option:

\$ `poetry config virtualenvs.in-project true`   


#### Mac users: Troubleshooting

**In case of errors installing Poetry on your Mac**, you may have to try installing it with `pipx` . But to install that, we need to have `Homebrew` installed first.   

\$ `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` 

(Homebrew documentation: https://brew.sh/)

Once `Homebrew` is installed, proceed to install `pipx`: 

\$ `brew install pipx` 

\$ `pipx ensurepath` 

Finally, install `Poetry` :

\$ `pipx install poetry` 


### Create a Python virtual environment and activate it  

\$ `python3 -m venv .venv` 

This created the virtualenv under the hidden folder `.venv`  

Activate it with: 

\$ `source .venv/bin/activate`  

### Install Kudaf Datasource Tools and other required Python packages 

\$ `poetry install`  
