const PORTFOLIO_EMAIL = Object.freeze({
  RECIPIENT_FILE: 'email_recipients_current.csv',
  MANIFEST_FILE: 'email_delivery_manifest.csv',
  LOG_FILE: 'email_send_log.csv',
  NOTE_FILE: 'email_message_notes.csv',
  DATA_FOLDER: '02 Portfolio Data',
  PACKET_FOLDER: '03 Student Packets',
  EMAIL_FOLDER: 'Email Delivery',
  ALL_PERIODS: '__ALL__',
  NOTE_MAX_LENGTH: 1000
});

function doGet() {
  assertAuthorized_();
  return HtmlService.createTemplateFromFile('Index')
    .evaluate()
    .setTitle('Portfolio Report Email Delivery')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.DEFAULT);
}

function verifySetup() {
  const cfg = getConfig_();
  assertAuthorized_();
  const root = DriveApp.getFolderById(cfg.rootFolderId);
  return {
    ok: true,
    rootName: root.getName(),
    teacherEmail: cfg.teacherEmail,
    remainingRecipientQuota: MailApp.getRemainingDailyQuota()
  };
}

function getBootstrap() {
  const cfg = getConfig_();
  assertAuthorized_();
  const root = DriveApp.getFolderById(cfg.rootFolderId);
  const courses = [];
  const it = root.getFolders();
  while (it.hasNext()) {
    const courseFolder = it.next();
    const name = courseFolder.getName();
    if (name === '00 Contact Directory') continue;
    const units = listUnits_(courseFolder);
    if (units.length) courses.push({ name: name, units: units });
  }
  courses.sort((a, b) => a.name.localeCompare(b.name));
  return {
    teacherEmail: cfg.teacherEmail,
    teacherDisplayName: cfg.teacherDisplayName,
    rootName: root.getName(),
    remainingRecipientQuota: MailApp.getRemainingDailyQuota(),
    courses: courses
  };
}

function getUnitMeta(course, unit) {
  assertAuthorized_();
  const state = getUnitState_(course, unit);
  const recipients = readCsvObjects_(requireSingleFile_(state.dataFolder, PORTFOLIO_EMAIL.RECIPIENT_FILE));
  requireColumns_(recipients.headers, [
    'student_key', 'student_name', 'period', 'student_email', 'guardian_emails',
    'contact_status', 'contact_source_sha256', 'verified_at'
  ], PORTFOLIO_EMAIL.RECIPIENT_FILE);
  const periods = Array.from(new Set(recipients.rows.map(r => String(r.period || '').trim()).filter(Boolean)))
    .sort(naturalCompare_);
  return { periods: [PORTFOLIO_EMAIL.ALL_PERIODS].concat(periods) };
}

function getMessageNotes(course, unit, period) {
  assertAuthorized_();
  const state = getUnitState_(course, unit);
  const recipients = readCsvObjects_(requireSingleFile_(state.dataFolder, PORTFOLIO_EMAIL.RECIPIENT_FILE));
  requireColumns_(recipients.headers, [
    'student_key', 'student_name', 'period', 'student_email', 'guardian_emails',
    'contact_status', 'contact_source_sha256', 'verified_at'
  ], PORTFOLIO_EMAIL.RECIPIENT_FILE);
  const selectedPeriod = period || PORTFOLIO_EMAIL.ALL_PERIODS;
  const notes = readMessageNotes_(state.dataFolder);
  const students = recipients.rows
    .filter(r => selectedPeriod === PORTFOLIO_EMAIL.ALL_PERIODS || String(r.period || '').trim() === selectedPeriod)
    .map(r => {
      const key = String(r.student_key || '').trim();
      const saved = notes.students.get(key) || { note: '', includeThisWeek: false, updatedAt: '' };
      return {
        studentKey: key,
        studentName: String(r.student_name || '').trim(),
        period: String(r.period || '').trim(),
        note: saved.note,
        includeThisWeek: !!saved.includeThisWeek,
        updatedAt: saved.updatedAt || ''
      };
    })
    .sort((a, b) => naturalCompare_(a.period, b.period) || a.studentName.localeCompare(b.studentName));
  return {
    course: String(course),
    unit: String(unit),
    period: selectedPeriod,
    weeklyNote: notes.weeklyNote,
    weeklyUpdatedAt: notes.weeklyUpdatedAt,
    students: students
  };
}

function saveMessageNotes(request) {
  assertAuthorized_();
  request = request || {};
  const course = String(request.course || '').trim();
  const unit = String(request.unit || '').trim();
  const selectedPeriod = String(request.period || PORTFOLIO_EMAIL.ALL_PERIODS).trim() || PORTFOLIO_EMAIL.ALL_PERIODS;
  const state = getUnitState_(course, unit);
  const recipients = readCsvObjects_(requireSingleFile_(state.dataFolder, PORTFOLIO_EMAIL.RECIPIENT_FILE));
  const eligible = recipients.rows.filter(r => selectedPeriod === PORTFOLIO_EMAIL.ALL_PERIODS || String(r.period || '').trim() === selectedPeriod);
  const eligibleKeys = new Set(eligible.map(r => String(r.student_key || '').trim()).filter(Boolean));
  const notes = readMessageNotes_(state.dataFolder);
  const now = new Date().toISOString();

  notes.weeklyNote = safeNote_(request.weeklyNote);
  notes.weeklyUpdatedAt = now;

  const submitted = Array.isArray(request.students) ? request.students : [];
  submitted.forEach(item => {
    const key = String(item && item.studentKey || '').trim();
    if (!key || !eligibleKeys.has(key)) throw new Error('A submitted student note does not match the current selected roster. Reload notes and try again.');
    const note = safeNote_(item.note);
    const includeThisWeek = !!item.includeThisWeek && !!note;
    notes.students.set(key, { note: note, includeThisWeek: includeThisWeek, updatedAt: now });
  });

  writeMessageNotes_(state.dataFolder, notes);
  return getMessageNotes(course, unit, selectedPeriod);
}

function savePreflightStudentNote(course, unit, studentKey, note) {
  assertAuthorized_();
  const state = getUnitState_(course, unit);
  const recipients = readCsvObjects_(requireSingleFile_(state.dataFolder, PORTFOLIO_EMAIL.RECIPIENT_FILE));
  const key = String(studentKey || '').trim();
  const matches = recipients.rows.filter(r => String(r.student_key || '').trim() === key);
  if (!key || matches.length !== 1) {
    throw new Error('This student is not a unique current recipient. The custom note was not changed.');
  }

  const notes = readMessageNotes_(state.dataFolder);
  const saved = notes.students.get(key) || { note: '', includeThisWeek: false, updatedAt: '' };
  const submitted = safeNote_(note);
  const now = new Date().toISOString();
  if (submitted) {
    notes.students.set(key, { note: submitted, includeThisWeek: true, updatedAt: now });
  } else {
    notes.students.set(key, { note: saved.note || '', includeThisWeek: false, updatedAt: now });
  }
  writeMessageNotes_(state.dataFolder, notes);
  const current = notes.students.get(key);
  return {
    studentKey: key,
    note: current.includeThisWeek ? current.note : '',
    savedNote: current.note || '',
    includeThisWeek: !!current.includeThisWeek
  };
}

function runPreflight(course, unit, period, excludedStudentKeys) {
  assertAuthorized_();
  return buildPreflight_(course, unit, period || PORTFOLIO_EMAIL.ALL_PERIODS, true, excludedStudentKeys || []);
}

function sendTestToMe(request) {
  const cfg = getConfig_();
  assertAuthorized_();
  request = request || {};
  const pf = buildPreflight_(request.course, request.unit, request.period || PORTFOLIO_EMAIL.ALL_PERIODS, true, request.excludedStudentKeys || []);
  if (!request.digest || request.digest !== pf.digest) {
    throw new Error('Preview changed. Run Preflight again before sending a test.');
  }
  if (pf.blockingCount > 0) {
    throw new Error('Preflight has blocking errors. Fix them or explicitly exclude those rows before sending a test.');
  }
  const row = pf.rows.find(r => r.included && r.studentKey === request.studentKey && r.sendable && !r.alreadySent);
  if (!row) throw new Error('Choose a currently included, sendable student for the test.');
  if (MailApp.getRemainingDailyQuota() < 1) throw new Error('No MailApp recipient quota remains for a test email.');

  const file = getVerifiedReportFile_(row, getUnitState_(request.course, request.unit));
  const subject = '[TEST] ' + buildSubject_(row);
  const body = 'TEST ONLY - this message was sent only to the teacher.\n\n' + buildBody_(row, cfg.teacherDisplayName);
  MailApp.sendEmail({
    to: cfg.teacherEmail,
    subject: subject,
    body: body,
    name: cfg.teacherDisplayName,
    attachments: [file.getBlob().setName(row.reportFileName)]
  });
  appendSendLog_(request.course, request.unit, row, 'TEST', cfg.teacherEmail, '', 'SENT', '');
  return { ok: true, message: 'Test sent only to ' + cfg.teacherEmail + '.', studentName: row.studentName };
}

function sendLiveReports(request) {
  const cfg = getConfig_();
  assertAuthorized_();
  request = request || {};
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) throw new Error('Another send is already running. Wait a moment and try again.');
  try {
    const pf = buildPreflight_(request.course, request.unit, request.period || PORTFOLIO_EMAIL.ALL_PERIODS, true, request.excludedStudentKeys || []);
    if (!request.digest || request.digest !== pf.digest) {
      throw new Error('Preview changed after you reviewed it. Run Preflight again before sending.');
    }
    if (pf.blockingCount > 0) {
      throw new Error('Preflight has blocking errors in included rows. No live reports were sent.');
    }
    const sendRows = pf.rows.filter(r => r.included && r.sendable && !r.alreadySent);
    if (!sendRows.length) throw new Error('There are no unsent included reports in this selection.');
    const quota = MailApp.getRemainingDailyQuota();
    if (quota < pf.recipientCountToSend) {
      throw new Error('Insufficient daily email recipient quota. Need ' + pf.recipientCountToSend + ', remaining ' + quota + '. No live reports were sent.');
    }

    const state = getUnitState_(request.course, request.unit);
    let sent = 0, failed = 0;
    const failures = [];
    const sentStudentKeys = [];
    sendRows.forEach(row => {
      try {
        const file = getVerifiedReportFile_(row, state);
        const message = {
          to: row.studentEmail,
          subject: buildSubject_(row),
          body: buildBody_(row, cfg.teacherDisplayName),
          name: cfg.teacherDisplayName,
          attachments: [file.getBlob().setName(row.reportFileName)]
        };
        if (row.guardianEmails.length) message.bcc = row.guardianEmails.join(',');
        MailApp.sendEmail(message);
        appendSendLog_(request.course, request.unit, row, 'LIVE', row.studentEmail, row.guardianEmails.join('|'), 'SENT', '');
        sentStudentKeys.push(row.studentKey);
        sent++;
      } catch (err) {
        const msg = safeError_(err);
        appendSendLog_(request.course, request.unit, row, 'LIVE', row.studentEmail, row.guardianEmails.join('|'), 'FAILED', msg);
        failures.push({ studentName: row.studentName, error: msg });
        failed++;
      }
    });

    let noteResetWarning = '';
    if (sentStudentKeys.length) {
      try {
        markStudentNotesSent_(state.dataFolder, sentStudentKeys);
      } catch (err) {
        noteResetWarning = 'Reports were sent, but the custom-note include flags could not be reset automatically: ' + safeError_(err);
      }
    }

    return {
      ok: failed === 0,
      sent: sent,
      failed: failed,
      failures: failures,
      noteResetWarning: noteResetWarning,
      remainingRecipientQuota: MailApp.getRemainingDailyQuota()
    };
  } finally {
    lock.releaseLock();
  }
}

function buildPreflight_(course, unit, period, verifyFiles, excludedStudentKeys) {
  const state = getUnitState_(course, unit);
  const recipientCsv = readCsvObjects_(requireSingleFile_(state.dataFolder, PORTFOLIO_EMAIL.RECIPIENT_FILE));
  const manifestCsv = readCsvObjects_(requireSingleFile_(state.dataFolder, PORTFOLIO_EMAIL.MANIFEST_FILE));
  requireColumns_(recipientCsv.headers, [
    'student_key', 'student_name', 'period', 'student_email', 'guardian_emails',
    'contact_status', 'contact_source_sha256', 'verified_at'
  ], PORTFOLIO_EMAIL.RECIPIENT_FILE);
  requireColumns_(manifestCsv.headers, [
    'student_key', 'student_name', 'period', 'course', 'unit', 'report_number',
    'report_date', 'pdf_file_id', 'pdf_file_name', 'pdf_sha256'
  ], PORTFOLIO_EMAIL.MANIFEST_FILE);

  const messageNotes = readMessageNotes_(state.dataFolder);
  const weeklyNote = messageNotes.weeklyNote || '';
  const selectedPeriod = period || PORTFOLIO_EMAIL.ALL_PERIODS;
  const excludedSet = new Set((Array.isArray(excludedStudentKeys) ? excludedStudentKeys : [])
    .map(x => String(x || '').trim()).filter(Boolean));
  const recipients = recipientCsv.rows.filter(r => selectedPeriod === PORTFOLIO_EMAIL.ALL_PERIODS || String(r.period || '').trim() === selectedPeriod);
  if (!recipients.length) throw new Error('No recipient rows match the selected period.');
  const manifests = manifestCsv.rows.filter(r => selectedPeriod === PORTFOLIO_EMAIL.ALL_PERIODS || String(r.period || '').trim() === selectedPeriod);

  const recipientDupes = duplicateKeys_(recipientCsv.rows, 'student_key');
  const manifestDupes = duplicateKeys_(manifestCsv.rows, 'student_key');
  const manifestByKey = indexRows_(manifests, 'student_key');
  const logRows = readOptionalLog_(state.dataFolder);
  const sentSet = new Set(logRows.filter(r => String(r.mode).toUpperCase() === 'LIVE' && String(r.status).toUpperCase() === 'SENT')
    .map(r => String(r.student_key || '') + '|' + String(r.report_sha256 || '').toLowerCase()));

  const rows = [];
  recipients.forEach(rec => {
    const key = String(rec.student_key || '').trim();
    const included = !excludedSet.has(key);
    const issues = [];
    const warnings = [];
    const studentEmail = normalizeEmail_(rec.student_email);
    const guardians = parseGuardianList_(rec.guardian_emails);
    const guardianInvalid = guardians.invalid;
    const guardianEmails = guardians.valid;
    const contactStatus = String(rec.contact_status || '').trim().toUpperCase();
    const savedNote = messageNotes.students.get(key) || { note: '', includeThisWeek: false };
    const studentNote = savedNote.includeThisWeek ? String(savedNote.note || '').trim() : '';

    if (!['READY','WARNING_NO_GUARDIAN'].includes(contactStatus)) issues.push('Contact status is not send-ready');
    if (contactStatus === 'WARNING_NO_GUARDIAN') warnings.push('Contact file marks no guardian email');
    if (!key) issues.push('Missing student_key');
    if (recipientDupes.has(key)) issues.push('Duplicate student_key in recipient file');
    if (contactStatus === 'REVIEW') issues.push('Contact record requires review');
    if (!isValidEmail_(studentEmail)) issues.push('Missing or invalid student email');
    if (guardianInvalid.length) issues.push('Invalid guardian email: ' + guardianInvalid.join(', '));
    if (studentEmail && guardianEmails.some(e => e.toLowerCase() === studentEmail.toLowerCase())) issues.push('Student email also appears in guardian BCC list');
    if (!guardianEmails.length) warnings.push('No guardian email; student-only delivery');

    const matching = manifestByKey.get(key) || [];
    let man = null;
    if (manifestDupes.has(key) || matching.length > 1) issues.push('Multiple report manifest rows for student');
    else if (!matching.length) issues.push('Missing individual report');
    else man = matching[0];

    let reportHash = '', fileId = '', fileName = '', reportNumber = '', reportDate = '';
    if (man) {
      reportHash = String(man.pdf_sha256 || '').trim().toLowerCase();
      fileId = String(man.pdf_file_id || '').trim();
      fileName = String(man.pdf_file_name || '').trim();
      reportNumber = String(man.report_number || '').trim();
      reportDate = String(man.report_date || '').trim();
      if (String(man.course || '').trim() !== String(course).trim()) issues.push('Report course does not match selected course');
      if (String(man.unit || '').trim() !== String(unit).trim()) issues.push('Report unit does not match selected unit');
      if (String(man.period || '').trim() !== String(rec.period || '').trim()) issues.push('Report period does not match recipient period');
      if (!fileId || !fileName || !/^[0-9a-f]{64}$/i.test(reportHash)) issues.push('Report manifest file ID/name/hash is incomplete');
    }

    const alreadySent = !!(key && reportHash && sentSet.has(key + '|' + reportHash));
    const row = {
      course: String(course),
      unit: String(unit),
      studentKey: key,
      studentName: String(rec.student_name || '').trim(),
      period: String(rec.period || '').trim(),
      studentEmail: studentEmail,
      guardianEmails: guardianEmails,
      contactStatus: contactStatus,
      reportNumber: reportNumber,
      reportDate: reportDate,
      reportFileId: fileId,
      reportFileName: fileName,
      reportSha256: reportHash,
      weeklyNote: weeklyNote,
      studentNote: studentNote,
      included: included,
      issues: issues,
      warnings: warnings,
      alreadySent: alreadySent,
      sendable: false,
      status: ''
    };

    if (included && !issues.length && verifyFiles && man) {
      try {
        getVerifiedReportFile_(row, state);
      } catch (err) {
        issues.push(safeError_(err));
      }
    }
    row.sendable = included && issues.length === 0;
    if (!included) row.status = 'EXCLUDED';
    else if (issues.length) row.status = 'BLOCKED';
    else if (alreadySent) row.status = 'ALREADY_SENT';
    else if (warnings.length) row.status = 'WARNING';
    else row.status = 'READY';
    rows.push(row);
  });

  const recipientKeys = new Set(recipients.map(r => String(r.student_key || '').trim()).filter(Boolean));
  manifests.forEach(m => {
    const key = String(m.student_key || '').trim();
    if (key && !recipientKeys.has(key)) {
      const included = !excludedSet.has(key);
      rows.push({
        course: String(course),
        unit: String(unit),
        studentKey: key,
        studentName: String(m.student_name || '').trim(),
        period: String(m.period || '').trim(),
        studentEmail: '', guardianEmails: [], contactStatus: '',
        reportNumber: String(m.report_number || '').trim(), reportDate: String(m.report_date || '').trim(),
        reportFileId: String(m.pdf_file_id || '').trim(), reportFileName: String(m.pdf_file_name || '').trim(),
        reportSha256: String(m.pdf_sha256 || '').trim().toLowerCase(),
        weeklyNote: weeklyNote, studentNote: '', included: included,
        issues: ['Report exists without a matching current recipient row'], warnings: [],
        alreadySent: false, sendable: false, status: included ? 'BLOCKED' : 'EXCLUDED'
      });
    }
  });

  rows.sort((a, b) => naturalCompare_(a.period, b.period) || a.studentName.localeCompare(b.studentName));
  const blockingCount = rows.filter(r => r.included && r.issues.length).length;
  const warningCount = rows.filter(r => r.included && !r.issues.length && r.warnings.length && !r.alreadySent).length;
  const alreadySentCount = rows.filter(r => r.included && r.alreadySent && !r.issues.length).length;
  const excludedCount = rows.filter(r => !r.included).length;
  const sendRows = rows.filter(r => r.included && r.sendable && !r.alreadySent);
  const recipientCountToSend = sendRows.reduce((n, r) => n + 1 + r.guardianEmails.length, 0);
  const digest = digestPreview_(course, unit, selectedPeriod, rows, weeklyNote);

  return {
    course: String(course), unit: String(unit), period: selectedPeriod,
    weeklyNote: weeklyNote,
    rows: rows,
    digest: digest,
    blockingCount: blockingCount,
    warningCount: warningCount,
    alreadySentCount: alreadySentCount,
    excludedCount: excludedCount,
    excludedStudentKeys: rows.filter(r => !r.included).map(r => r.studentKey),
    sendableMessageCount: sendRows.length,
    recipientCountToSend: recipientCountToSend,
    remainingRecipientQuota: MailApp.getRemainingDailyQuota(),
    canSendLive: blockingCount === 0 && sendRows.length > 0 && MailApp.getRemainingDailyQuota() >= recipientCountToSend
  };
}

function getVerifiedReportFile_(row, state) {
  if (!row.reportFileId) throw new Error('Missing report Drive file ID');
  if (!state.emailFolder) throw new Error('Missing Drive folder: ' + PORTFOLIO_EMAIL.EMAIL_FOLDER);
  const file = DriveApp.getFileById(row.reportFileId);
  if (file.getMimeType() !== 'application/pdf') throw new Error('Report attachment is not a PDF');
  if (file.getName() !== row.reportFileName) throw new Error('Report filename no longer matches manifest');
  let inExpectedFolder = false;
  const parents = file.getParents();
  while (parents.hasNext()) {
    if (parents.next().getId() === state.emailFolder.getId()) { inExpectedFolder = true; break; }
  }
  if (!inExpectedFolder) throw new Error('Report file is not inside the exact Email Delivery folder');
  const actualHash = sha256Bytes_(file.getBlob().getBytes());
  if (actualHash !== String(row.reportSha256 || '').toLowerCase()) throw new Error('Report SHA-256 does not match manifest');
  return file;
}

function getUnitState_(course, unit) {
  const cfg = getConfig_();
  const root = DriveApp.getFolderById(cfg.rootFolderId);
  const courseName = String(course || '').trim();
  const unitValue = String(unit || '').trim();
  if (!courseName || !/^\d+$/.test(unitValue)) throw new Error('Invalid course/unit selection.');
  const courseFolder = requireSingleFolder_(root, courseName);
  const unitFolder = requireSingleFolder_(courseFolder, 'unit ' + unitValue);
  const dataFolder = requireSingleFolder_(unitFolder, PORTFOLIO_EMAIL.DATA_FOLDER);
  const packetFolder = requireSingleFolder_(unitFolder, PORTFOLIO_EMAIL.PACKET_FOLDER);
  const emailFolder = getOptionalSingleFolder_(packetFolder, PORTFOLIO_EMAIL.EMAIL_FOLDER);
  return { root: root, courseFolder: courseFolder, unitFolder: unitFolder, dataFolder: dataFolder, packetFolder: packetFolder, emailFolder: emailFolder };
}

function listUnits_(courseFolder) {
  const units = [];
  const it = courseFolder.getFolders();
  while (it.hasNext()) {
    const f = it.next();
    const m = /^unit\s+(\d+)$/i.exec(f.getName().trim());
    if (m) units.push(String(Number(m[1])));
  }
  return Array.from(new Set(units)).sort((a, b) => Number(a) - Number(b));
}

function buildSubject_(row) {
  return row.course + ' Unit ' + row.unit + ' Portfolio Progress Report - ' + row.studentName;
}

function buildBody_(row, teacherDisplayName) {
  const first = firstName_(row.studentName);
  const lines = [
    'Hello,',
    '',
    'Attached is ' + first + "'s current " + row.course + ' Unit ' + row.unit + ' Portfolio Progress Report. You can expect an updated Portfolio report about once each week as new evidence is collected.',
    '',
    'How the report works: the unit is organized into Mastery Goals and I Cans. The report shows the current evidence picture for each skill, what the student has demonstrated, and what kind of evidence or practice is useful next.',
    '',
    'How grading works: grades are based on the current body of evidence, not an average of assignment percentages. Checks, classwork, reassessments, and other evidence update the current picture. Newer or stronger evidence can improve a grade as learning grows.'
  ];
  if (String(row.course || '').trim().toLowerCase() === 'algebra 1') {
    lines.push(
      '',
      'In Algebra 1, we are currently testing four current Mastery Goal grades - one for each of the four major goals in the unit. Each Mastery Goal grade is updated from the I Can evidence inside that goal. During this pilot, PowerSchool still uses the existing single current Unit assignment while we test whether the four-goal view is more useful.'
    );
  }
  lines.push(
    '',
    'What "Next" means:',
    '- Needs first check - We do not yet have usable evidence for this skill.',
    '- Practice + check soon - More practice or support is needed before another independent check.',
    '- Needs another independent check - There is already convincing evidence, but another independent demonstration is needed to confirm mastery.',
    '- Secure - Current evidence supports mastery of this skill.',
    '- Extension - The skill is secure and the student is ready to apply it in a new or more challenging situation.'
  );
  if (row.weeklyNote) {
    lines.push('', "This week's note:", row.weeklyNote);
  }
  if (row.studentNote) {
    lines.push('', 'Teacher note for ' + first + ':', row.studentNote);
  }
  lines.push(
    '',
    'The "Next" statements are next steps, not assignment grades. The report can change as ' + first + ' learns, practices, and provides new evidence.',
    '',
    '- ' + teacherDisplayName
  );
  return lines.join('\n');
}

function digestPreview_(course, unit, period, rows, weeklyNote) {
  const compact = rows.map(r => ({
    studentKey: r.studentKey,
    period: r.period,
    studentEmail: r.studentEmail,
    guardianEmails: r.guardianEmails,
    reportNumber: r.reportNumber,
    reportFileId: r.reportFileId,
    reportSha256: r.reportSha256,
    studentNote: r.studentNote || '',
    included: !!r.included,
    issues: r.issues,
    warnings: r.warnings,
    alreadySent: r.alreadySent
  }));
  return sha256Text_(JSON.stringify({
    course: String(course), unit: String(unit), period: String(period),
    weeklyNote: String(weeklyNote || ''), rows: compact
  }));
}

function appendSendLog_(course, unit, row, mode, toEmail, bccEmails, status, error) {
  const state = getUnitState_(course, unit);
  const header = [
    'send_id','timestamp','mode','course','unit','report_number','student_key','report_sha256',
    'to_email','bcc_emails','status','error'
  ];
  const values = [
    Utilities.getUuid(), new Date().toISOString(), mode, course, unit, row.reportNumber, row.studentKey,
    row.reportSha256, toEmail, bccEmails, status, error || ''
  ];
  let file = getOptionalSingleFile_(state.dataFolder, PORTFOLIO_EMAIL.LOG_FILE);
  const line = csvLine_(values) + '\n';
  if (!file) {
    file = state.dataFolder.createFile(PORTFOLIO_EMAIL.LOG_FILE, csvLine_(header) + '\n' + line, 'text/csv');
  } else {
    const current = file.getBlob().getDataAsString('UTF-8');
    file.setContent(current.replace(/\s*$/, '\n') + line);
  }
}

function readOptionalLog_(dataFolder) {
  const f = getOptionalSingleFile_(dataFolder, PORTFOLIO_EMAIL.LOG_FILE);
  if (!f) return [];
  const parsed = readCsvObjects_(f);
  requireColumns_(parsed.headers, [
    'send_id','timestamp','mode','course','unit','report_number','student_key','report_sha256',
    'to_email','bcc_emails','status','error'
  ], PORTFOLIO_EMAIL.LOG_FILE);
  return parsed.rows;
}

function readMessageNotes_(dataFolder) {
  const out = { weeklyNote: '', weeklyUpdatedAt: '', students: new Map() };
  const f = getOptionalSingleFile_(dataFolder, PORTFOLIO_EMAIL.NOTE_FILE);
  if (!f) return out;
  const parsed = readCsvObjects_(f);
  requireColumns_(parsed.headers, ['scope','student_key','note','include_this_week','updated_at'], PORTFOLIO_EMAIL.NOTE_FILE);
  let weeklyCount = 0;
  parsed.rows.forEach(r => {
    const scope = String(r.scope || '').trim().toUpperCase();
    const key = String(r.student_key || '').trim();
    const note = String(r.note || '').trim();
    const includeThisWeek = /^(true|yes|1)$/i.test(String(r.include_this_week || '').trim());
    const updatedAt = String(r.updated_at || '').trim();
    if (scope === 'WEEKLY') {
      weeklyCount++;
      if (weeklyCount > 1) throw new Error('Multiple WEEKLY rows exist in ' + PORTFOLIO_EMAIL.NOTE_FILE + '. Resolve the duplicate before sending.');
      out.weeklyNote = note;
      out.weeklyUpdatedAt = updatedAt;
    } else if (scope === 'STUDENT') {
      if (!key) throw new Error('A STUDENT row in ' + PORTFOLIO_EMAIL.NOTE_FILE + ' is missing student_key.');
      if (out.students.has(key)) throw new Error('Duplicate student_key in ' + PORTFOLIO_EMAIL.NOTE_FILE + ': ' + key);
      out.students.set(key, { note: note, includeThisWeek: includeThisWeek && !!note, updatedAt: updatedAt });
    }
  });
  return out;
}

function writeMessageNotes_(dataFolder, notes) {
  const header = ['scope','student_key','note','include_this_week','updated_at'];
  const lines = [csvLine_(header)];
  lines.push(csvLine_(['WEEKLY','',notes.weeklyNote || '',notes.weeklyNote ? 'TRUE' : 'FALSE',notes.weeklyUpdatedAt || new Date().toISOString()]));
  Array.from(notes.students.keys()).sort(naturalCompare_).forEach(key => {
    const row = notes.students.get(key) || {};
    if (!row.note && !row.includeThisWeek) return;
    lines.push(csvLine_(['STUDENT',key,row.note || '',row.includeThisWeek ? 'TRUE' : 'FALSE',row.updatedAt || new Date().toISOString()]));
  });
  const text = lines.join('\n') + '\n';
  let f = getOptionalSingleFile_(dataFolder, PORTFOLIO_EMAIL.NOTE_FILE);
  if (!f) f = dataFolder.createFile(PORTFOLIO_EMAIL.NOTE_FILE, text, 'text/csv');
  else f.setContent(text);
}

function markStudentNotesSent_(dataFolder, studentKeys) {
  const keySet = new Set((studentKeys || []).map(x => String(x || '').trim()).filter(Boolean));
  if (!keySet.size) return;
  const notes = readMessageNotes_(dataFolder);
  let changed = false;
  keySet.forEach(key => {
    const row = notes.students.get(key);
    if (row && row.includeThisWeek) {
      row.includeThisWeek = false;
      row.updatedAt = new Date().toISOString();
      notes.students.set(key, row);
      changed = true;
    }
  });
  if (changed) writeMessageNotes_(dataFolder, notes);
}

function safeNote_(value) {
  const s = String(value == null ? '' : value).replace(/\r\n/g, '\n').trim();
  if (s.length > PORTFOLIO_EMAIL.NOTE_MAX_LENGTH) {
    throw new Error('A message note is too long. Maximum length is ' + PORTFOLIO_EMAIL.NOTE_MAX_LENGTH + ' characters.');
  }
  return s;
}

function readCsvObjects_(file) {
  const text = file.getBlob().getDataAsString('UTF-8').replace(/^\uFEFF/, '');
  const grid = Utilities.parseCsv(text);
  if (!grid.length) throw new Error(file.getName() + ' is empty.');
  const headers = grid[0].map(h => String(h || '').trim());
  const rows = grid.slice(1).filter(r => r.some(v => String(v || '').trim() !== '')).map(r => {
    const out = {};
    headers.forEach((h, i) => out[h] = r[i] == null ? '' : String(r[i]));
    return out;
  });
  return { headers: headers, rows: rows };
}

function requireColumns_(headers, required, label) {
  const set = new Set(headers);
  const missing = required.filter(x => !set.has(x));
  if (missing.length) throw new Error(label + ' is missing required column(s): ' + missing.join(', '));
}

function indexRows_(rows, keyName) {
  const map = new Map();
  rows.forEach(r => {
    const key = String(r[keyName] || '').trim();
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(r);
  });
  return map;
}

function duplicateKeys_(rows, keyName) {
  const counts = new Map();
  rows.forEach(r => {
    const k = String(r[keyName] || '').trim();
    if (k) counts.set(k, (counts.get(k) || 0) + 1);
  });
  return new Set(Array.from(counts.entries()).filter(x => x[1] > 1).map(x => x[0]));
}

function parseGuardianList_(value) {
  const seen = new Set(), valid = [], invalid = [];
  String(value || '').split('|').map(s => s.trim()).filter(Boolean).forEach(raw => {
    const email = normalizeEmail_(raw);
    const key = email.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    if (isValidEmail_(email)) valid.push(email); else invalid.push(raw);
  });
  return { valid: valid, invalid: invalid };
}

function normalizeEmail_(value) { return String(value || '').trim(); }
function isValidEmail_(value) { return /^[^\s@,;]+@[^\s@,;]+\.[^\s@,;]+$/.test(String(value || '').trim()); }

function firstName_(studentName) {
  const s = String(studentName || '').trim();
  if (!s) return 'your student';
  if (s.includes(',')) return s.split(',')[1].trim().split(/\s+/)[0] || s;
  return s.split(/\s+/)[0];
}

function requireSingleFolder_(parent, name) {
  const it = parent.getFoldersByName(name);
  if (!it.hasNext()) throw new Error('Missing Drive folder: ' + name);
  const first = it.next();
  if (it.hasNext()) throw new Error('Duplicate Drive folders named ' + name + '. Resolve the ambiguity before sending.');
  return first;
}

function getOptionalSingleFolder_(parent, name) {
  const it = parent.getFoldersByName(name);
  if (!it.hasNext()) return null;
  const first = it.next();
  if (it.hasNext()) throw new Error('Duplicate Drive folders named ' + name + '. Resolve the ambiguity before sending.');
  return first;
}

function requireSingleFile_(folder, name) {
  const file = getOptionalSingleFile_(folder, name);
  if (!file) throw new Error('Missing private Portfolio file: ' + name);
  return file;
}

function getOptionalSingleFile_(folder, name) {
  const it = folder.getFilesByName(name);
  if (!it.hasNext()) return null;
  const first = it.next();
  if (it.hasNext()) throw new Error('Duplicate private Portfolio files named ' + name + '. Resolve the ambiguity before sending.');
  return first;
}

function getConfig_() {
  const p = PropertiesService.getScriptProperties().getProperties();
  const cfg = {
    rootFolderId: String(p.PORTFOLIO_ROOT_FOLDER_ID || '').trim(),
    teacherEmail: String(p.TEACHER_EMAIL || '').trim().toLowerCase(),
    teacherDisplayName: String(p.TEACHER_DISPLAY_NAME || '').trim()
  };
  const missing = [];
  if (!cfg.rootFolderId) missing.push('PORTFOLIO_ROOT_FOLDER_ID');
  if (!cfg.teacherEmail) missing.push('TEACHER_EMAIL');
  if (!cfg.teacherDisplayName) missing.push('TEACHER_DISPLAY_NAME');
  if (missing.length) throw new Error('Missing Script Properties: ' + missing.join(', '));
  if (!isValidEmail_(cfg.teacherEmail)) throw new Error('TEACHER_EMAIL is not a valid email address.');
  return cfg;
}

function assertAuthorized_() {
  const cfg = getConfig_();
  const active = String(Session.getActiveUser().getEmail() || '').trim().toLowerCase();
  if (!active || active !== cfg.teacherEmail) {
    throw new Error('Access blocked. The active Google account could not be verified as the configured teacher account.');
  }
  return true;
}

function sha256Text_(text) {
  const bytes = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, String(text), Utilities.Charset.UTF_8);
  return bytesToHex_(bytes);
}
function sha256Bytes_(bytes) {
  return bytesToHex_(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, bytes));
}
function bytesToHex_(bytes) {
  return bytes.map(b => ('0' + ((b < 0 ? b + 256 : b).toString(16))).slice(-2)).join('');
}

function csvLine_(values) {
  return values.map(v => {
    const s = String(v == null ? '' : v);
    return /[",\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }).join(',');
}

function naturalCompare_(a, b) {
  return String(a || '').localeCompare(String(b || ''), undefined, { numeric: true, sensitivity: 'base' });
}
function safeError_(err) { return String(err && err.message ? err.message : err || 'Unknown error').slice(0, 500); }
