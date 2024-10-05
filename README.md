# ProyectO_IC_GINI

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

## Aseguramiento de la Calidad

Este proyecto incluye un proceso de validación de datos durante el procesamiento, para garantizar que los datos sean consistentes y correctos.

### Validaciones Implementadas:
1. Verificación de valores nulos.
2. Comprobación de los tipos de datos esperados.
3. Detección de registros duplicados en las claves primarias.
4. Validación de que los valores del ingreso no sean negativos.
5. Verificación de formato correcto en las fechas.

Para ejecutar el procesamiento y aseguramiento de la calidad, utiliza el siguiente comando:

```python proyecto_ic_mcd/transform.py```

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         proyecto_ic_mcd and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── proyecto_ic_mcd   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes proyecto_ic_mcd a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    │
    └── plots.py                <- Code to create visualizations
```

--------

