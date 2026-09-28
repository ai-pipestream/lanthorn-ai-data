Read README.md and BRIEF.md in this workspace.

Perform a small source-discovery pilot for recall training data. Use web research
to identify at most three interactive-fiction games with a publicly accessible
walkthrough and an obtainable playable release. Prefer IF Archive, IFWiki,
IFDB, and author-maintained sources. Follow at most ten relevant pages; do not
perform a broad crawl or download game binaries or bulk page collections.

Write `sources/pilot-inventory.json` containing, per game: title, author if
verified, release/version if verified, walkthrough URL, playable-release page
URL, access date, evidence for version compatibility, reuse/license statement
or `unknown`, and uncertainties. Only include URLs actually visited. A source
discovery result is not a captured playthrough or a training example.

Write `sources/pilot-next-steps.md` explaining which one game is the best pilot,
how to obtain a real command/response transcript, what tools or input are still
missing, and how a first batch of 25 question candidates would be verified.

Do not fabricate transcripts or produce training rows from walkthrough prose.
If a page is unavailable or permission blocks a tool, record that limitation.
Do not bypass access restrictions. Stop after this bounded inventory and plan.

In the final response list files actually written, pages actually visited, and
remaining blockers. Distinguish verified facts from suggestions.
