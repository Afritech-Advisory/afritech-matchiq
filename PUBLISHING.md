# Publishing a match to MatchIQ

Checklist for anyone at Afritech Sports adding a finished match. Two repos are involved:

- **afritech-matchiq** (public website): the dashboard with broadcast key frames and no clips.
- **afritech-matchiq-clients** (private, no website): the full dashboard with every clip embedded.

## Before you publish

1. The dashboard has passed offline QA: network cut, zero outside requests, every goal sequence plays and hands on to the next goal, then to the next topic, at desktop and phone widths.
2. You have two versions. The **public** version has no embedded clips. Each goal shows three key frames credited "Key frames: [broadcaster] broadcast, used for match analysis." The **client** version has every clip embedded, credited "Footage: [broadcaster] broadcast, embedded for match analysis."
3. Andrew has approved the release.

## Folder names

Use `YYYY-MM-DD-team-a-team-b-competition`, all lowercase, with hyphens.
Example: `2026-11-07-japan-nigeria-u17w-final`

## Public site (afritech-matchiq)

1. Create `matches/<folder>/` and save the public dashboard inside it as `index.html`.
2. Add the PDF report as `report.pdf` and the match-story videos as `story-16x9.mp4`, `story-1x1.mp4` and `story-9x16.mp4`, if they exist.
3. Any file over 100 MB cannot go in the repo. Attach it to a GitHub Release named after the folder and link it from the home page card instead.
4. Add a card to `index.html` at the top of the Matches grid. Copy the existing card and change the link, competition, score, date and venue.
5. Commit with the message `Publish <match>`. The site updates within a few minutes at https://afritech-advisory.github.io/afritech-matchiq/

## Client edition (afritech-matchiq-clients)

1. Create `matches/<folder>/` and save the client dashboard inside it as `index.html`.
2. Share it only with the clients Andrew names: add them as repo collaborators or send them the file.

## Size

The public site must stay under 1 GB. When it gets close, start a new repo for the next season (`afritech-matchiq-2027`) and link it from the home page.

Contact: Advisory@afritechsports.com
