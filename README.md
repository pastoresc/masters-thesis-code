# Master's Thesis – Recommender System for Master's Program Selection

This repository contains the code developed for the master's thesis project titled:

**"Design of a Recommender System Model Leveraging Graph Databases for Master's Program Selection"**

## Repository Structure

The repository is organized as follows:

- `/scrapers/`  
  Contains web and PDF scrapers used to extract program and course data from different university sources.

- `/merge/`  
  Contains scripts for merging website and course data into a harmonized and unified dataset.

- `/tuition/`  
  Includes normalization scripts for tuition fees (e.g. conversion to EUR per semester).

- `/notebooks/`  
  Jupyter Notebooks used for keyword mapping, course enrichment and validation logic (e.g. fuzzy matching).

## How to Use

1. Clone the repository
2. Install dependencies (see `requirements.txt`)
3. Run scrapers individually per university
4. Use merge scripts to combine the data
5. Use Notebooks to validate, enrich and analyze

## Notes

- This repository was created for academic purposes.
- For questions, please contact the author via GitHub or through the university.
