# 200-Person Biography JSON

Created `outputs/requested_200_biographies/biographies_200.json` in the requested overall schema.

## Selection

Because the long message did not arrive as a workspace JSON attachment and did not specify which 200 subset to select, this first batch uses the **first 200 records of the repository's `famous_people_birth_data.json`**. It is not claimed to be the first 200 names in the pasted message.

## Evidence policy

Unknown fields remain JSON `null`. I did not infer wealth, poverty, marriage dates, children, coordinates, success causes or career milestones from planetary positions or name recognition.

The JSON includes:

- name and birth date
- birth place/country
- coordinates fields, currently null where not sourced
- career/profession
- source URL
- source status
- marriage, children, death, education and career fields where the source infobox supplied them
- explicit nulls for missing wealth, childhood and milestone details

This is a reproducible baseline, not a complete biography. A complete 200-person dataset requires a defined person list, geocoding policy and independent verification of every major date and wealth claim.
