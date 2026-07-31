# Q-Series Biographical Enrichment

The 5,010 Q records originate from a Wikipedia birth-date/person dataset and are generally public or historical figures, but the source should not be described as a fully verified “famous people” registry. Fame, source reliability and biographical completeness vary.

## Added fields

`outputs/q_people_enriched/q_people_enriched.csv` now includes:

- Q ID
- name and birth date
- birth place/country where available
- career/profession
- industry group where available
- repository achievement score where available
- source URL and reliability
- marriage details status
- children details status
- wealth details status
- major-events status

Career/profession is present for **4,858 of 5,010** people. The current repository has no verified Q-series marriage, children, wealth or dated major-event fields, so those columns are explicitly marked unavailable rather than invented.

## Why marriage and event information is not filled automatically

Marriage and family details require person-specific source extraction and often have ambiguity around dates, multiple marriages, privacy, historical records and source reliability. They should be collected as separate event rows with source URLs, event-date precision and confidence—not inferred from a chart or a single biography sentence.

## Next event-table schema

`q_id`, `event_type`, `event_date`, `date_precision`, `event_description`, `source_url`, `source_type`, `reliability`, `independent_source_count`, `public_record_status`.

Suggested event types include `job_start`, `promotion`, `career_change`, `marriage`, `divorce`, `child_birth`, `wealth_gain`, `bankruptcy`, `award`, `major_success`, `illness`, `accident`, `death` and `retirement`.
