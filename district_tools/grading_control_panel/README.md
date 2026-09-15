# Grading & Evidence Control Panel - Pilot

This is a district-wide pilot tool for packaging student evidence into a self-contained request ZIP for ChatGPT.

## Teacher flow

1. Enter a class/group name and assignment/evidence-set name.
2. Upload student evidence (required).
3. Upload a rubric/scoring guide (optional).
4. Add teacher notes (optional). The interface includes clickable note hints such as focusing on reasoning, marking work as formative, ignoring a question, noting paired work, allowing multiple solution methods, or emphasizing explanation/vocabulary.
5. Click **Build Request ZIP**.
6. Upload the generated ZIP to ChatGPT. The packaged request contains the task instructions, so processing can begin from the upload without the teacher having to provide a special run phrase.
7. ChatGPT is instructed to return one response ZIP. The teacher unzips it and opens `CLICK_ME.html`.

## Pilot scoring behavior

- With a rubric/scoring guide: ChatGPT may score against it when the match is clear and must show/flag evidence and uncertainty.
- Without a rubric/scoring guide: ChatGPT is instructed not to invent a numeric grade. It provides evidence-based feedback, mastery/next-step indicators, class analysis, and follow-up practice.

## Requested response package

The generated request instructs ChatGPT to return a static, offline-friendly ZIP containing:

- `CLICK_ME.html` - teacher dashboard with Student Reports, Class Data, and Print Options
- `students/` - one print-friendly report per identified student
- `class/class_overview.html` - class strengths, common mistakes, pattern counts, groupings, extension readiness, and limitations
- `print/all_student_reports.pdf` - all individual student reports combined with page breaks for one-click class printing
- `print/all_student_reports.html` - browser-printable equivalent of the combined report PDF
- `print/common_review_extension_packet.pdf` - one general class packet targeting the most important common needs plus extension when justified
- `print/common_review_extension_packet.html` - browser-printable version of the common packet
- `print/individualized/` - one student-specific practice packet per identified student
- `print/individualized_packets.pdf` - the entire individualized class set combined with page breaks for easy printing and distribution
- `data/analysis.json` - structured analysis behind the reports and print materials
- `data/request.json` - copy of the original request metadata
- `assets/styles.css` - shared local styling

The request tells ChatGPT to use relative links and no CDN dependencies so the HTML package works after unzip without a web server. PDFs are required as finished printable files, not placeholders.

## Privacy / data handling

The control panel itself reads selected files in the browser and packages them locally into a ZIP. It does not upload evidence by itself. Teachers still need to follow district policy when uploading student data to an AI service.

## Implementation note

The pilot uses a small built-in ZIP writer (STORE/no compression) so the page has no third-party JavaScript dependency. This makes the builder easier to host in GitHub Pages and keeps the request-building step self-contained.
