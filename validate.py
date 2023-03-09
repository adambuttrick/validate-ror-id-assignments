import re
import csv
import json
from sys import argv
from collections import defaultdict
from unidecode import unidecode
from rapidfuzz import fuzz
from gensim.parsing.preprocessing import preprocess_string
from gensim.parsing.preprocessing import strip_tags
from gensim.parsing.preprocessing import strip_multiple_whitespaces
from gensim.parsing.preprocessing import strip_punctuation


def preprocess_text(text):
	custom_filters = [lambda x: x.lower(), strip_tags,
					  strip_punctuation, strip_multiple_whitespaces]
	return unidecode(' '.join(preprocess_string(text, custom_filters)))


def preprocess_primary_name(name):
	name = re.sub(r'\s\(.*\)', '', name)
	name = preprocess_text(name)
	return name


def create_primary_names(f):
	primary_names = {}
	with open(f, 'r+') as f_in:
		records = json.load(f_in)
		for record in records:
			ror_id = re.sub('https://ror.org/', '', record['id'])
			primary_name = preprocess_primary_name(record['name'])
			primary_names[ror_id] = primary_name
	return primary_names


def create_ror_names(f, primary_names):
	ror_names_dict = defaultdict(lambda:{'primary': '', 'faked': []})
	for key, value in primary_names.items():
		ror_names_dict[key]['primary'] = value
	with open(f) as f_in:
		reader = csv.DictReader(f_in)
		for row in reader:
			ror_id = row['label']
			affiliation = preprocess_text(row['text'])
			ror_names_dict[ror_id]['faked'].append(affiliation)
			ror_names_dict[ror_id]['faked'] = list(set(ror_names_dict[ror_id]['faked']))
	return ror_names_dict


def validate(data_dump_file, faked_affiliations_file, works_csv):
	# ROR data dumpfile https://zenodo.org/communities/ror-data
	primary_names = create_primary_names(data_dump_file)
	all_ror_names = create_ror_names(faked_affiliations_file, primary_names)
	validated = 'validated.csv'
	dropped = 'dropped.csv'
	with open(validated, 'w') as f_out:
		writer = csv.writer(f_out)
		writer.writerow(['ror_id', 'primary_name', 'affiliation_string', 'clean_affiliation_string'])
	with open(dropped, 'w') as f_out:
		writer = csv.writer(f_out)
		writer.writerow(['ror_id', 'primary_name', 'affiliation_string', 'clean_affiliation_string'])
	with open(works_csv, 'r+') as f_in:
		reader = csv.reader(f_in)
		for row in reader:
			ror_id = row[0]
			clean_ror_id = re.sub('https://ror.org/', '', ror_id)
			affiliation = row[1]
			clean_affiliation = preprocess_text(affiliation)
			ror_names = all_ror_names[clean_ror_id]
			primary_name = ror_names['primary']
			primary_in_clean = all(substring in clean_affiliation for substring in primary_name.split(' '))
			clean_in_primary = all(substring in primary_name for substring in clean_affiliation.split(' '))
			if primary_in_clean or clean_in_primary:
				with open(validated, 'a') as f_out:
					writer = csv.writer(f_out)
					writer.writerow([ror_id, primary_name, affiliation, clean_affiliation])
			elif fuzz.ratio(primary_name, clean_affiliation) >=90:
				with open(validated, 'a') as f_out:
					writer = csv.writer(f_out)
					writer.writerow([ror_id, primary_name, affiliation, clean_affiliation])
			else:
				faked_match = False
				for faked in ror_names['faked']:
					fake_in_clean = all(substring in clean_affiliation for substring in faked.split(' '))
					clean_in_fake = all(substring in faked for substring in clean_affiliation.split(' '))
					if fake_in_clean or clean_in_fake:
						faked_match = True
						with open(validated, 'a') as f_out:
							writer = csv.writer(f_out)
							writer.writerow([ror_id, primary_name, affiliation, clean_affiliation])
						break
					elif fuzz.ratio(faked, clean_affiliation) >=90:
						faked_match = True
						with open(validated, 'a') as f_out:
							writer = csv.writer(f_out)
							writer.writerow([ror_id, primary_name, affiliation, clean_affiliation])
						break
				if faked_match == False:
					with open(dropped, 'a') as f_out:
						writer = csv.writer(f_out)
						writer.writerow([ror_id, primary_name, affiliation, clean_affiliation])

if __name__ == '__main__':
	validate(argv[1], argv[2], argv[3])















