# Perception vs. Reality of Household Income in Mexico

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

## Description

This project aims to analyze the discrepancy between individuals' perceptions of their income and what they actually earn and spend. Inspired by the concept of the "Doña Florinda syndrome," which reflects the tendency of some people to view their financial situation optimistically and, at times, excessively, we seek to investigate how this perception can influence the economic behavior of households.

Using data from the ENCO 2022 and ENIGH 2022 surveys provided by INEGI, this analysis focuses on unraveling the differences between reported incomes and actual expenditures, as well as the social and economic consequences that arise from this misalignment. Through the calculation of the Gini coefficient, we will explore economic inequality and how it manifests across different population sectors, shedding light on the realities behind these perceptions.

This project not only aims to provide a clear view of the financial situation of households in Mexico but also to encourage critical reflection on how perceptions can distort reality and affect economic decisions.

## Intended Audience

The final data product is designed for a diverse audience, including:

1. **General Public**: Individuals interested in understanding their economic environment and comparing their perceptions of income and expenses with actual data. This can foster a deeper understanding of financial issues affecting their communities.

2. **Policymakers and Government Officials**: Decision-makers who require insights into the economic conditions and perceptions of citizens. This data can aid in formulating policies aimed at improving financial literacy and economic well-being.

3. **Non-Governmental Organizations (NGOs)**: Organizations focused on social issues, poverty alleviation, and economic development. The data can help these organizations understand community needs and design effective programs.


## Project Organization

```
├── LICENSE                  # Open-source license if one is chosen.
├── Makefile                 # Convenience commands for building and running the project (e.g., `make data`, `make train`).
├── README.md                # The top-level README file for developers using or contributing to this project.
├── requirements.txt         # Python dependencies needed to run the project 
│
├── data
│   ├── external            # Data from third-party sources.
│   ├── interim             # Intermediate data that has been transformed.
│   ├── metadata            # Additional data describing the datasets.
│   ├── processed           # The final, canonical datasets for modeling.
│   └── raw                 # The original, immutable data dump.
│
├── modules                         
│   ├── dataset_modules      # Python scripts for downloading and transforming datasets.
│   │   ├── data_downloader.py
│   │   ├── data_transform_enco.py
│   │   └── data_transform_engih.py
│   ├── models               # Model-related scripts or information.
│   └── config.py            # Configuration files for the documentation generation tool.                  <-
│
├── notebooks                # Jupyter notebooks used for data exploration, model development, or reporting. Naming     │                              convention: `number-author-initials-description`.
│
├── references               # Data dictionaries, manuals, and all other explanatory materials.
│   ├── diccionario_enghi_2022.md
│   └── diccionario_enco_2022.md
│
├── reports                  # This folder stores generated analysis in formats such as HTML, PDF, or LaTeX, along with │                              any figures created during the project.
│   └── figures              # Generated graphics and figures for use in reporting.
│
└── IENQMX-ENCO-2022         # Source code for use in this project.
    │
    └── __init__.py          # Makes INEQMX-ENCO-2022 a Python module
```

## Usage Instructions

1. Clone the repository: `git clone https://github.com/INEQMX-ENCO/INEQMX-ENCO-2022`
2. Install the dependencies: `pip install -r requirements.txt`
3. Run the Makefile commands: `make data`, `make train`, etc.
4. Explore the notebooks: `jupyter notebook`
5. Check the reports and figures in the `reports/` directory.

## Requirements

To run this project, you need the following Python 3.12+ packages:

- pandas
- geopandas
- numpy
- requests
- tqdm

You can install the required packages using pip:

```bash
pip install -r requirements.txt
```

## Data Sources

The data used in this project comes from:

- [ENCO](https://www.inegi.org.mx/programas/enco/): National Consumer Confidence Survey by INEGI.
- [ENIGH 2022](https://www.inegi.org.mx/programas/enigh/nc/2022/): National Survey on Household Income and Expenditure by INEGI.


## Quality Assurance

This project includes a data validation process during processing, to ensure that the data is consistent and correct.

### Validations implemented:
1. Verification of null values.
2. Checking the expected data types.
3. Detection of duplicate records in the primary keys.
4. Validation that the income values are not negative.
5. Verification of correct format on dates.

To run processing and quality assurance, use the following command:
```bash
python modules/dataset_modules/data_transform_enco.py
```

## Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request with your changes

## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/INEQMX-ENCO/INEQMX-ENCO-2022/blob/9666c9b5b0534d9a4b39b0fa83da141ad7de8b40/LICENSE) file for details.

## Acknowledgments
Thanks to the team for their collaborative efforts in this project and to INEGI for providing the datasets used in our analysis.

--------

