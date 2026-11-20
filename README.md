# Afritech Sports MatchIQ

Public match library for Afritech Sports Technology and Innovation Group Limited.

Website: https://afritech-advisory.github.io/afritech-matchiq/

Each match lives in `matches/<date-teams-competition>/`. Every dashboard is a single file that works offline on a phone. Public dashboards use broadcast key frames; the full clip editions are kept in the private client repo.

To add a match, follow the publishing checklist in Afritech Sports' private files (see [PUBLISHING.md](PUBLISHING.md)).

Contact: Advisory@afritechsports.com

## Four languages

Every page is published in English, French, Kiswahili and Brazilian Portuguese (copies under `fr/`, `sw/` and `pt/`, each with a language bar). After adding or changing a page, add the French, Kiswahili and Brazilian Portuguese wording for any new text to `i18n/strings.py` and run `python3 i18n/build.py`. The build stops and lists any text that has no translation in `i18n/missing.txt`. Names, scores and source titles stay as written.
