# validate-affiliation-string-ror-id-assignments
Scripts for validating affiliation string assignments

## Background
OpenAlex has a [publicly available works dataset](https://docs.openalex.org/download-snapshot) that includes ROR ID assignments based on affiliation strings. These ROR IDs are assigned using the text classification model described [here](https://github.com/ourresearch/openalex-institution-parsing). Real world testing suggests model accuracy in the 80-90% range for those ROR IDs that have sufficient affiliation string examples/training data in their works dataset. In order to further determine the accuracy of the model, we can compare the names and location data in ROR records with the affiliation strings to which their works have been assigned.

## Validation
Validation is done using a basic, procedural check for the presence of ROR record primary names, aliases, and labels in the affiliation strings have been assigned. In addition, a set of faked affiliation strings, based on names and locations from the assigned ROR ID/record, [following the example of the model's construction](https://github.com/ourresearch/openalex-institution-parsing/blob/main/V1/001_Exploration/001_institutions_and_ror_exploration.ipynb), can be compared to determine incorrect assignments. See the [faked_affiliations file](https://github.com/adambuttrick/validate-affiliation-string-ror-id-assignments/blob/main/sample_data/faked_affiliations.zip) for examples.

## Usage
Download the latest [ROR data dump](https://zenodo.org/communities/ror-data/) from Zenodo
```
pip install -r requirements.txt
```
Inputs are the data dump file, a faked affiliations string file, and CSV containing ROR IDs and their associated affiliations strings, parsed from the OpenAlex works dataset. See [affiliation_string_assignment_sample.csv](https://github.com/adambuttrick/validate-affiliation-string-ror-id-assignments/blob/main/sample_data/affiliation_string_assignment_sample.csv) for an example
```
python validate.py data_dump_file.json faked_affiliations.csv affiliation_string_assignment_sample.csv
```
Outputs are two CSVs containing the records that pass and fail the checks.

## Limitations
No one set of checks can account for all of the inherent variability of affiliation strings. This validation check is meant to flag the most obvious set of incorrect assignments for further examination and to identify opportunities for model refinement. The script will flag as wrong some subset of correct ID assignments. In addition, acronyms from ROR records were not used by themselves in the checks, only as part of faked affiliations where location data was present, as they were found to produce too many false positives. This means that affiliations that overly rely on acronyms are dropped at a higher rate than other name forms.
