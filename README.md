# The Human Cost of Civilian Targeting

An analysis of how violence targeting civilians changed globally between 2021 and 2025, and where its reported human cost was most severe. The project was developed as an individual Data Visualization assignment using ACLED event data, Python, and Tableau.

## Research questions

1. Which regions record the highest number of civilian-targeting events?
2. How does the human cost of civilian-targeting vary across regions?
3. Which forms drive fatalities in the most affected regions?
4. Which countries show the greatest need for attention from a civilian-protection perspective?

## Main findings

- The Middle East records the highest number of civilian-targeting events: 44,141 across the available period, followed by South America with 41,401.
- Frequency alone does not explain human cost. Western Africa ranks fourth by event count but second by reported fatalities.
- In the Middle East, air/drone strikes account for 47,916 reported fatalities. In Western Africa, attacks are the leading form, with 34,132.
- Palestine and the Democratic Republic of Congo have the highest Relative Attention Index values, reflecting the strongest overlap between event frequency and lethality.

## Relative Attention Index

The final country comparison reproduces the indicator used in Tableau. For each country, event frequency and lethality (reported fatalities per event) are converted into rank percentiles and combined with equal weight through their geometric mean:

$$
RAI = \sqrt{P_{events} \times P_{fatalities/event}}
$$

The index is a relative ACLED-based comparison. It is not an official humanitarian-needs index or a measure of individual risk.

## Repository structure

```text
.
├── notebooks/
│   ├── 01_acled_data_cleaning.ipynb
│   └── 02_acled_eda.ipynb
├── data/
│   └── processed/
│       └── acled_civilian_targeting_2021_2025.parquet
├── scripts/
├── DataVisualization.pdf
├── requirements.txt
└── README.md
```

- [`01_acled_data_cleaning.ipynb`](notebooks/01_acled_data_cleaning.ipynb) filters, validates, and prepares the ACLED data.
- [`02_acled_eda.ipynb`](notebooks/02_acled_eda.ipynb) contains the four final research questions, figures, result commentary, and Tableau exports.
- [`DataVisualization.pdf`](DataVisualization.pdf) contains the final presentation.

Generated CSV tables, figure exports, screenshots, local cache files, and the licensed raw ACLED download are intentionally excluded from the repository.

## Reproducing the analysis

1. Clone the repository and create a Python environment.
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Obtain the global ACLED export under the applicable ACLED licence and place the CSV in the repository root. The cleaning notebook automatically selects the largest matching `*acled*.csv*` file.
4. Run the notebooks in order:

   ```text
   notebooks/01_acled_data_cleaning.ipynb
   notebooks/02_acled_eda.ipynb
   ```

The analysis covers complete years 2021–2024 and data through 25 August for the partial year 2025.

## Data notes and limitations

- `civilian_targeting` identifies events in which civilians are recorded as the main or sole target; it does not capture every indirect effect of conflict.
- ACLED fatality figures are estimates based on available reporting. They are described here as **reported fatalities in civilian-targeting events**, not exact counts of civilian deaths.
- Reporting coverage can vary across countries, periods, and conflicts.
- The raw ACLED dataset is not redistributed in this repository. Users must obtain access directly from [ACLED](https://acleddata.com/) and comply with its End User Licence Agreement.

## Licence

The presentation *The Human Cost of Civilian Targeting* by Nicole Winy Hernandez is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). ACLED data remain subject to ACLED's own terms and licence.
