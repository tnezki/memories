# Grading & Evidence Control Panel - Pilot

This is a district-wide pilot tool for packaging student evidence into a self-contained request ZIP for ChatGPT.

## Teacher flow

1. Enter a class/group name and assignment/evidence-set name.
2. Upload student evidence (required).
3. Upload a rubric/scoring guide (optional).
4. Add teacher notes (optional). The interface includes clickable note hints such as focusing on reasoning, marking work as formative, ignoring a question, noting paired work, allowing multiple solution methods, or emphasizing explanation/vocabulary.
5. Click **Build Request ZIP**.
6. Upload the generated ZIP to ChatGPT and ask it to run the grading request.
7. ChatGPT is instructed to return one response ZIP. The teacher unzips it and opens `CLICK_ME.html`.

## Pilot scoring behavior

- With a rubric/scoring guide: ChatGPT may score against it when the match is clear and must show/flag evidence and uncertainty.
- Without a rubric/scoring guide: ChatGPT is instructed not to invent a numeric grade. It provides evidence-based feedback, mastery/next-step indicators, class analysis, and instructional stations.

## Requested response package

The generated request instructs ChatGPT to return a static, offline-friendly ZIP containing:

- `CLICK_ME.html` - teacher dashboard
- `students/` - one print-friendly report per identified student
- `class/class_overview.html` - class strengths, common mistakes, pattern counts, groupings, extension readiness, and limitations
- `stations/` - a teacher-facing station plan plus 2-4 printable review stations based on common mistakes and 1-2 printable extension stations when justified by evidence
- `data/analysis.json` - structured analysis behind the HTML
- `data/request.json` - copy of the original request metadata
- `assets/styles.css` - shared local styling

The request tells ChatGPT to use relative links and no CDN dependencies so the package works after unzip without a web server.

## Privacy / data handling

The control panel itself reads selected files in the browser and packages them locally into a ZIP. It does not upload evidence by itself. Teachers still need to follow district policy when uploading student data to an AI service.

## Implementation note

The pilot uses a small built-in ZIP writer (STORE/no compression) so the page has no third-party JavaScript dependency. This makes the builder easier to host in GitHub Pages and keeps the request-building step self-contained.
