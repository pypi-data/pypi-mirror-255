# Kudaf Analytics platform on JupyterLab 

This analytics platform is **intended to be used by a Kudaf Data Consumer**. It provides the basic infrastructure to interact with the Kudaf system, namely to: 
- **OAuth2 Feide authorization and authentication** to receive a JWT (JSON Web Token). 
- This **JWT will allow access to the granted data variables** on the different datasources. 
- Finally, the user will be able to retrieve the granted data using the notebook and perform analytics on it.
 
## On JupyterLab 

From the [JupyterLab Documentation](https://jupyterlab.readthedocs.io/en/latest/):

    JupyterLab is a highly extensible, feature-rich notebook authoring 
    application and editing environment, and is a part of Project Jupyter, 
    a large umbrella project centered around the goal of providing tools 
    (and standards) for interactive computing with computational notebooks.

    A computational notebook is a shareable document that combines computer 
    code, plain language descriptions, data, rich visualizations like 3D 
    models, charts, graphs and figures, and interactive controls. A notebook, 
    along with an editor like JupyterLab, provides a fast interactive 
    environment for prototyping and explaining code, exploring and 
    visualizing data, and sharing ideas with others.

Click on the link for the documentation on how to [Get Started with Jupyterlab](https://jupyterlab.readthedocs.io/en/latest/getting_started/overview.html).

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

\$ `pip install kudaf_jupyter_server_extension`  


### Enable the KUDAF extension

\$ `jupyter server extension enable kudaf_extension` 


---

## JupyterLab operation

### Launch the JupyterLab instance

Navigate to the project directory and activate the virtual environment (**if not already activated**): 

\$ `source .venv/bin/activate`  

**Start-up the Jupyter server** 

\$ **`jupyter lab`**  

You should see output very much like this: 


    [I 2023-06-16 12:05:45.548 ServerApp] Jupyter Server 2.6.0 is running at:
    [I 2023-06-16 12:05:45.549 ServerApp] http://localhost:8888/lab?token=db15ff4d84eebd80cd45ac1b03921a2f1e13d6de4f874246
    [I 2023-06-16 12:05:45.549 ServerApp]     http://127.0.0.1:8888/lab?token=db15ff4d84eebd80cd45ac1b03921a2f1e13d6de4f874246
    [I 2023-06-16 12:05:45.549 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
    [C 2023-06-16 12:05:45.580 ServerApp] 
        
        To access the server, open this file in a browser:
            file:///home/daniel/.local/share/jupyter/runtime/jpserver-28857-open.html
        Or copy and paste one of these URLs:
            http://localhost:8888/lab?token=db15ff4d84eebd80cd45ac1b03921a2f1e13d6de4f874246
            http://127.0.0.1:8888/lab?token=db15ff4d84eebd80cd45ac1b03921a2f1e13d6de4f874246

This **should also automatically open a new Browser window** pointing to that local Jupyter server at **[http://localhost:8888/lab](http://localhost:8888/lab)**. 

### Kudaf pre-requisites to be able to obtain data

The [Kudaf front-end](https://kudaf-frontend-latest-review-wip-sandbo-9d2e64.paas2.uninett.no/) provides the entry-point for a Kudaf user to: 
- Log into Feide. 
- Browse the Catalog to see what data is available. 
- Select the desired Variables: **NOTE: Not all Variables in Kudaf have (at this point) data to be downloaded** 
- Finish the data-shopping by entering the Project details. 

Now this **data request still needs to be Approved**.: 
- This can be achieved using this [Kudaf Core Backend API endpoint](https://kudaf-core.paas2.uninett.no/docs#/Projects/modify_data_request_approval_status_api_v1_projects_data_request__patch), 
- for which an `admin` scope JWT token is required. 

**Only those approved variables that have defined data-download URLs will be made available** to download here. 

Below is a **list of some of the variables for which data is available**:  
- **Sikt datasource**:
    - `Antall Feide-pålogginger per tjeneste og hos en gitt FeideOrg og grunnskole`** (internal Kudaf variable name: FEIDESTATS_LOGINS_FORG_SCHOOL_SP_ACCUM)
    - `Feide organisasjonsnavn` (FEIDE_ORG_NAVN)
    - `Feide-organisasjons organisasjonsnummer` (FEIDE_ORG_BRREG_ORG)
    - `Feide organisasjons-ID knyttet til en gitt Feide-tjenesteleverandør` (FEIDE_SP_FEIDE_ORG)
    - `Tjenesteleverandørsnavn`  (FEIDE_SP_NAVN)
    - `Tjenesteleverandørsbeskrivelse` (FEIDE_SP_BESKRIVELSE)
- **Brreg datasource**:
    - `Organisasjons navn i Enhetsregisteret` (BRREG_ENHETSNAVN)
    - `En organisasjonenhets kommunetilhørighet` (BRREG_ORG_KOMMUNENR)
    - `En organisasjonenhets fylketilhørighet` (BRREG_ORG_FYLKESNR)
- **SSB datasource**:
    - `Kommunesnavn`  (SSB_KOMMUNENAVN)
    - `Fylkesnavn`  (SSB_FYLKESNAVN)
    - `Fylkeskommunenavn`  (SSB_FYLKESKOMMUNENAVN)
    - `En Kommuneenhets fylketilhørighet` (SSB_KOMMUNENR_FYLKESNR) 
- **NSR datasource**:
    - `Skolenivå` (NSR_ORG_LEVEL)
    - `Antall skoler i en organisasjon` (NSR_ORG_SCHOOL_COUNT)
    - `Antall elever i grunnskole` (NSR_ORG_STUDENT_COUNT) 
  
**Once that is done, we can proceed to retrieve the required data**.

### Run a Notebook to obtain statistics from Feide 

On the left-hand side of the browser window, there should be a file tree open showing the various files on the project's directory. 

**Double-click on the file `kudaf.ipynb`**, this will open the Notebook. 

## Notebook Instructions : Downloading data using the Kudaf Panel

1. Go to the first code cell and enter the following code:  
   
```python
from kudaf_extension import kudaf_notebook
kudaf_notebook.run()

```

2. Execute the code cell (`Ctrl-Enter`) to enable the KUDAF extension. 
3. An **orange button `Enable Kudaf`** will appear on the right-side of the **Top Bar** -> **Click** on it
4. A new browser tab will open to prompt for the **Feide Login**
5. After the login is complete, the **tab will become blank -> Close it**
6. **Go back to the JupyterLab tab**, the orange button from before is now green, and shows we're **logged in**
7. A new **orange button `Granted Variables`** appears now on the right-side of the **Top Bar** -> **Click** on it
8. A **new Jupyter tab `Kudaf Panel` will appear** on the bottom half of the screen **(if it appears blank on your browser, change the Zoom level by pressing `Ctrl +` or `Ctrl -`)**
    - This shows different **Accordions with the User's Projects**.
    - Under each Project Accordion, another **Accordion-style display shows the Datasources and the Variables granted**.
    - **Some Variables may display possible parameter-entry fields**, if defined for the variable in question, so the data **query can be further refined**.
    - Click on the **(orange) Download button to the right of a Variable** to download its data file
9.  **Data files will be saved under Jupyter Lab's `downloads` folder** (click on the folder icon on the Jupyter Lab left side panel to toggle display of the available files and folders)


### Notebook Instructions : Downloading data using Python code (and the Kudaf Jupyter Server Extension)

**Required**: 
- **Name of a Kudaf variable that has been authorized** for you
- **URL** where its data can be downloaded from

A **list of the authorized variables** for the logged-in user can be found at: [Granted Variables](http://localhost:8888/kudaf/settings) 

Below is an **example Async function call that will download the data file** to the **'downloads' folder** on the left panel

```python
var_params = {
    "variable": "FEIDE_SP_NAVN",
    "url": "https://kudaf-feide-stats.paas2.uninett.no/api/v1/fixed/FEIDE_SP_NAVN",
}
result = kudaf_notebook.loop.run_until_complete(kudaf_notebook.fetch_granted_data(var_params))
```


**HAPPY ANALYTICS! :)** 

---

---

## Developer installation

### Clone this repository locally  

Open up a Terminal window and enter the following commands:  

\$ `git clone git@gitlab.sikt.no:kudaf/jupyterlab.git` 


