const STUDENT_DATA_EMAIL = Object.freeze({
  APP_VERSION: '3.4',
  PACKAGE_SCHEMA: 'portfolio-email-sender-package/1.0',
  APP_FOLDER: '_Student Data Tools Email Sender',
  CURRENT_FOLDER: 'Current Package',
  MANIFEST_FILE: 'current_sender_manifest.json',
  LOG_FILE: 'email_send_log.csv',
  NOTE_MAX_LENGTH: 1000
});

function doGet(){
  assertAuthorized_();
  return HtmlService.createTemplateFromFile('Index').evaluate()
    .setTitle('Portfolio Report Email Delivery')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.DEFAULT);
}

function verifySetup(){
  const c=getConfig_();
  assertAuthorized_();
  return {
    ok:true,
    version:STUDENT_DATA_EMAIL.APP_VERSION,
    teacherEmail:c.teacherEmail,
    teacherDisplayName:c.teacherDisplayName,
    remainingRecipientQuota:MailApp.getRemainingDailyQuota(),
    currentPackage:getCurrentPackageSummary_()
  };
}

function getBootstrap(){return verifySetup();}

function beginPackageUpload(fileName,totalBytes,totalChunks){
  assertAuthorized_();
  fileName=String(fileName||'').trim();
  totalBytes=Number(totalBytes||0);
  totalChunks=Number(totalChunks||0);
  if(fileName!=='Portfolio_Email_Sender_Package.zip')throw new Error('Choose Portfolio_Email_Sender_Package.zip created by Student Data Tools.');
  if(!Number.isFinite(totalBytes)||totalBytes<=0)throw new Error('The selected sender package is empty.');
  if(totalBytes>35*1024*1024)throw new Error('This sender package is larger than 35 MB. Prepare a smaller student batch and try again.');
  if(!Number.isInteger(totalChunks)||totalChunks<1||totalChunks>200)throw new Error('The sender package upload could not be started.');
  const app=getAppFolder_();
  const old=app.getFolders();
  while(old.hasNext()){
    const f=old.next();
    if(/^Upload_/.test(f.getName()))f.setTrashed(true);
  }
  const uploadId=Utilities.getUuid(),folder=app.createFolder('Upload_'+uploadId);
  folder.createFile('upload_meta.json',JSON.stringify({fileName:fileName,totalBytes:totalBytes,totalChunks:totalChunks,createdAt:new Date().toISOString()},null,2),'application/json');
  return{uploadId:folder.getId(),totalChunks:totalChunks};
}

function uploadPackageChunk(uploadId,index,totalChunks,base64Chunk){
  assertAuthorized_();
  const folder=getUploadFolder_(uploadId),meta=readUploadMeta_(folder);
  index=Number(index);totalChunks=Number(totalChunks);
  if(totalChunks!==Number(meta.totalChunks))throw new Error('Upload chunk count changed. Start the upload again.');
  if(!Number.isInteger(index)||index<0||index>=totalChunks)throw new Error('Invalid upload chunk number.');
  base64Chunk=String(base64Chunk||'');
  if(!base64Chunk)throw new Error('An upload chunk was empty. Start the upload again.');
  const name=chunkName_(index),existing=folder.getFilesByName(name);
  if(existing.hasNext())throw new Error('An upload chunk was duplicated. Start the upload again.');
  folder.createFile(name,base64Chunk,'text/plain');
  return{ok:true,index:index};
}

function finishPackageUpload(uploadId){
  assertAuthorized_();
  const folder=getUploadFolder_(uploadId),meta=readUploadMeta_(folder);
  try{
    const bytes=[];
    for(let i=0;i<Number(meta.totalChunks);i++){
      const f=getOptionalSingleFile_(folder,chunkName_(i));
      if(!f)throw new Error('Upload is incomplete. Missing chunk '+(i+1)+' of '+meta.totalChunks+'.');
      const part=Utilities.base64Decode(f.getBlob().getDataAsString('UTF-8').trim());
      for(let j=0;j<part.length;j++)bytes.push(part[j]);
    }
    if(bytes.length!==Number(meta.totalBytes))throw new Error('Uploaded package size does not match the selected file. Start the upload again.');
    const blob=Utilities.newBlob(bytes,'application/zip',String(meta.fileName||'Portfolio_Email_Sender_Package.zip'));
    return loadLocalSenderBlob_(blob);
  }finally{
    folder.setTrashed(true);
  }
}

function getUploadFolder_(uploadId){
  uploadId=String(uploadId||'').trim();
  if(!uploadId)throw new Error('Upload session is missing.');
  let folder;
  try{folder=DriveApp.getFolderById(uploadId);}catch(e){throw new Error('Upload session expired. Choose the package again.');}
  const app=getAppFolder_();let ok=false,parents=folder.getParents();
  while(parents.hasNext())if(parents.next().getId()===app.getId()){ok=true;break;}
  if(!ok||!/^Upload_/.test(folder.getName()))throw new Error('Invalid upload session.');
  return folder;
}

function readUploadMeta_(folder){
  const f=getOptionalSingleFile_(folder,'upload_meta.json');
  if(!f)throw new Error('Upload metadata is missing. Start the upload again.');
  return JSON.parse(f.getBlob().getDataAsString('UTF-8'));
}

function chunkName_(index){return 'chunk_'+('00000'+Number(index)).slice(-5)+'.txt';}

function loadLocalSenderBlob_(blob){
  assertAuthorized_();
  if(!blob)throw new Error('Choose the Portfolio_Email_Sender_Package.zip created by Student Data Tools.');
  let entries;
  try{entries=Utilities.unzip(blob);}catch(e){throw new Error('Could not read the selected Portfolio_Email_Sender_Package.zip. Build a new sender package from Student Data Tools and try again. '+safeError_(e));}
  const byName={};
  entries.forEach(b=>byName[b.getName()]=b);
  const manifestBlob=byName['sender_manifest.json'];
  if(!manifestBlob)throw new Error('The ZIP is missing sender_manifest.json. Build a new sender package from the local Portfolio email page.');
  let manifest;
  try{manifest=JSON.parse(manifestBlob.getDataAsString('UTF-8'));}catch(e){throw new Error('sender_manifest.json is not valid JSON.');}
  if(manifest.schema!==STUDENT_DATA_EMAIL.PACKAGE_SCHEMA)throw new Error('Unsupported sender package schema: '+String(manifest.schema||'(missing)'));
  if(!String(manifest.course||'').trim()||!Number(manifest.unit)||!Array.isArray(manifest.rows)||!manifest.rows.length)throw new Error('Sender package metadata is incomplete.');

  const appFolder=getAppFolder_(),current=replaceCurrentFolder_(appFolder),seen=new Set();
  const storedRows=[];
  manifest.rows.forEach((raw,i)=>{
    const row=normalizePackageRow_(raw);
    if(!row.studentKey||!row.studentName)throw new Error('Sender package row '+(i+1)+' is missing student identity.');
    if(seen.has(row.studentKey))throw new Error('Duplicate student in sender package: '+row.studentName);
    seen.add(row.studentKey);
    row.driveFileId='';
    if(row.readyToSend){
      if(!row.identityVerified)throw new Error('Identity verification is missing for '+row.studentName+'.');
      if(!row.pdfPath||!row.reportSha256)throw new Error('Prepared PDF metadata is missing for '+row.studentName+'.');
      const pdfBlob=byName[row.pdfPath];
      if(!pdfBlob)throw new Error('Prepared PDF is missing from the ZIP for '+row.studentName+'.');
      const actual=sha256Bytes_(pdfBlob.getBytes());
      if(actual!==row.reportSha256)throw new Error('Prepared PDF hash mismatch for '+row.studentName+'.');
      const file=current.createFile(pdfBlob.copyBlob().setName(baseName_(row.pdfPath)).setContentType(MimeType.PDF));
      row.driveFileId=file.getId();
    }
    storedRows.push(row);
  });
  const stored={
    schema:STUDENT_DATA_EMAIL.PACKAGE_SCHEMA,
    loadedAt:new Date().toISOString(),
    generatedAt:String(manifest.generated_at||''),
    course:String(manifest.course),
    unit:Number(manifest.unit),
    rows:storedRows
  };
  current.createFile(STUDENT_DATA_EMAIL.MANIFEST_FILE,JSON.stringify(stored,null,2),'application/json');
  return buildPreflight_([],true);
}

function runPreflight(request){
  assertAuthorized_();
  request=request||{};
  return buildPreflight_(request.excludedStudentKeys||[],request.includeSupportStaff!==false);
}

function sendTestToMe(request){
  const c=getConfig_();
  assertAuthorized_();
  request=request||{};
  const pf=buildPreflight_(request.excludedStudentKeys||[],request.includeSupportStaff!==false);
  guardDigest_(request,pf);
  if(pf.blockingCount)throw new Error('Preflight has blocking errors.');
  const row=pf.rows.find(r=>r.included&&r.studentKey===String(request.studentKey||'')&&r.sendable&&!r.alreadySent);
  if(!row)throw new Error('Choose a currently included, sendable student.');
  const f=getVerifiedReportFile_(row);
  MailApp.sendEmail({
    to:c.teacherEmail,
    subject:'[TEST] '+buildSubject_(row),
    body:'TEST ONLY - this message was sent only to the teacher.\n\n'+buildBody_(row,c.teacherDisplayName),
    name:c.teacherDisplayName,
    attachments:[f.getBlob().setName(row.reportFileName)]
  });
  appendSendLog_(row,'TEST',c.teacherEmail,'','SENT','');
  return{ok:true,message:'Test sent only to '+c.teacherEmail+'.',studentName:row.studentName};
}

function sendLiveReports(request){
  const c=getConfig_();
  assertAuthorized_();
  request=request||{};
  const lock=LockService.getScriptLock();
  if(!lock.tryLock(30000))throw new Error('Another send is already running.');
  try{
    const pf=buildPreflight_(request.excludedStudentKeys||[],request.includeSupportStaff!==false);
    guardDigest_(request,pf);
    if(pf.blockingCount)throw new Error('Preflight has blocking errors in included rows.');
    const rows=pf.rows.filter(r=>r.included&&r.sendable&&!r.alreadySent);
    if(!rows.length)throw new Error('There are no unsent included reports.');
    if(MailApp.getRemainingDailyQuota()<pf.recipientCountToSend)throw new Error('Insufficient daily email recipient quota.');
    let sent=0,failed=0;const failures=[];
    rows.forEach(row=>{
      try{
        const f=getVerifiedReportFile_(row),bcc=dedupeEmails_(row.guardianEmails.concat(row.supportStaffEmails));
        const msg={
          to:row.studentEmail,
          subject:buildSubject_(row),
          body:buildBody_(row,c.teacherDisplayName),
          name:c.teacherDisplayName,
          attachments:[f.getBlob().setName(row.reportFileName)]
        };
        if(bcc.length)msg.bcc=bcc.join(',');
        MailApp.sendEmail(msg);
        appendSendLog_(row,'LIVE',row.studentEmail,bcc.join('|'),'SENT','');
        sent++;
      }catch(e){
        failed++;
        const er=safeError_(e);
        failures.push({studentName:row.studentName,error:er});
        appendSendLog_(row,'LIVE',row.studentEmail,'','FAILED',er);
      }
    });
    return{ok:failed===0,sent:sent,failed:failed,failures:failures,remainingRecipientQuota:MailApp.getRemainingDailyQuota()};
  }finally{lock.releaseLock();}
}

function buildPreflight_(excludedStudentKeys,includeSupportStaff){
  const pkg=readCurrentPackage_(),excluded=new Set((excludedStudentKeys||[]).map(String));
  const sentSet=new Set(readSendLog_().filter(r=>String(r.mode).toUpperCase()==='LIVE'&&String(r.status).toUpperCase()==='SENT').map(r=>String(r.student_key)+'|'+String(r.report_sha256).toLowerCase()));
  const rows=pkg.rows.map(src=>{
    const r=Object.assign({},src),issues=[],warnings=[];
    const included=!excluded.has(r.studentKey);
    const studentEmail=normalizeEmail_(r.studentEmail);
    if(!isValidEmail_(studentEmail))issues.push('Missing or invalid student email');
    const guardians=validateEmailArray_(r.guardianEmails,issues,'Invalid guardian email');
    if(!guardians.length)warnings.push('No guardian email listed');
    const supportStaff=Array.isArray(r.supportStaff)?r.supportStaff:[];
    const supportEmails=[];
    if(includeSupportStaff){
      supportStaff.forEach(x=>{
        const e=normalizeEmail_(x&&x.email);
        if(!e)return;
        if(isValidEmail_(e))supportEmails.push(e);else warnings.push('Support staff email is invalid: '+String(x&&x.name||e));
      });
    }
    if(!r.readyToSend)issues.push('Local package row is not marked ready to send');
    if(!r.identityVerified)issues.push('Report identity has not been verified');
    if(!r.driveFileId||!r.reportSha256)issues.push('Prepared report attachment is missing');
    const already=!!(r.studentKey&&r.reportSha256&&sentSet.has(r.studentKey+'|'+r.reportSha256));
    if(included&&!issues.length){try{getVerifiedReportFile_(r);}catch(e){issues.push(safeError_(e));}}
    const row={
      course:pkg.course,unit:pkg.unit,studentKey:r.studentKey,studentId:r.studentId,studentName:r.studentName,period:r.period,
      studentEmail:studentEmail,guardianEmails:guardians,supportStaff:supportStaff,supportStaffEmails:dedupeEmails_(supportEmails),
      mgGrades:Array.isArray(r.mgGrades)?r.mgGrades.slice(0,4):[],reportFileId:r.driveFileId,reportFileName:baseName_(r.pdfPath||''),reportSha256:r.reportSha256,
      weeklyNote:String(r.wholeClassNote||''),studentNote:String(r.studentNote||''),included:included,issues:issues,warnings:warnings,alreadySent:already,
      sendable:included&&!issues.length,status:''
    };
    row.status=!included?'OMITTED THIS SEND':issues.length?'BLOCKED':already?'ALREADY SENT':warnings.length?'WARNING':'READY';
    return row;
  });
  rows.sort((a,b)=>naturalCompare_(a.period,b.period)||a.studentName.localeCompare(b.studentName));
  const blocking=rows.filter(r=>r.included&&r.issues.length).length,sendRows=rows.filter(r=>r.included&&r.sendable&&!r.alreadySent);
  const recipientCount=sendRows.reduce((n,r)=>n+1+r.guardianEmails.length+r.supportStaffEmails.length,0);
  const result={
    version:STUDENT_DATA_EMAIL.APP_VERSION,course:pkg.course,unit:pkg.unit,generatedAt:pkg.generatedAt||'',loadedAt:pkg.loadedAt||'',rows:rows,
    blockingCount:blocking,warningCount:rows.filter(r=>r.included&&!r.issues.length&&r.warnings.length&&!r.alreadySent).length,
    alreadySentCount:rows.filter(r=>r.included&&r.alreadySent&&!r.issues.length).length,excludedCount:rows.filter(r=>!r.included).length,
    sendableMessageCount:sendRows.length,recipientCountToSend:recipientCount,remainingRecipientQuota:MailApp.getRemainingDailyQuota(),includeSupportStaff:!!includeSupportStaff
  };
  result.digest=digestPreview_(result);
  result.canSendLive=blocking===0&&sendRows.length>0&&result.remainingRecipientQuota>=recipientCount;
  return result;
}

function normalizePackageRow_(raw){
  raw=raw||{};
  return{
    studentKey:String(raw.student_key||'').trim(),studentId:String(raw.student_id||'').trim(),studentName:String(raw.student_name||'').trim(),period:String(raw.period||'').trim(),
    studentEmail:String(raw.student_email||'').trim(),guardianEmails:Array.isArray(raw.guardian_emails)?raw.guardian_emails.map(String):[],supportStaff:(Array.isArray(raw.support_staff)?raw.support_staff:[]).map(x=>({name:String(x&&x.name||''),email:String(x&&x.email||''),role:String(x&&x.role||'Support staff'),supportClass:String(x&&x.support_class||x&&x.supportClass||'')})),
    mgGrades:Array.isArray(raw.mg_grades)?raw.mg_grades:[],pdfPath:String(raw.pdf_path||'').trim(),reportSha256:String(raw.pdf_sha256||'').trim().toLowerCase(),
    identityVerified:raw.identity_verified===true,readyToSend:raw.ready_to_send===true,status:String(raw.status||'').trim(),wholeClassNote:safeNote_(raw.whole_class_note||''),studentNote:safeNote_(raw.student_note||'')
  };
}

function getCurrentPackageSummary_(){
  try{const p=readCurrentPackage_();return{loaded:true,course:p.course,unit:p.unit,generatedAt:p.generatedAt||'',loadedAt:p.loadedAt||'',rowCount:p.rows.length};}
  catch(e){return{loaded:false};}
}

function readCurrentPackage_(){
  const app=getAppFolder_(),it=app.getFoldersByName(STUDENT_DATA_EMAIL.CURRENT_FOLDER);
  if(!it.hasNext())throw new Error('No local sender package is loaded. Build it in Student Data Tools, then upload it here.');
  const folder=it.next();if(it.hasNext())throw new Error('Duplicate current sender folders were found.');
  const f=getOptionalSingleFile_(folder,STUDENT_DATA_EMAIL.MANIFEST_FILE);if(!f)throw new Error('The current sender manifest is missing. Load the local package again.');
  const p=JSON.parse(f.getBlob().getDataAsString('UTF-8'));
  if(p.schema!==STUDENT_DATA_EMAIL.PACKAGE_SCHEMA||!Array.isArray(p.rows))throw new Error('The current sender package is invalid.');
  return p;
}

function getAppFolder_(){
  const root=DriveApp.getRootFolder(),it=root.getFoldersByName(STUDENT_DATA_EMAIL.APP_FOLDER);
  if(!it.hasNext())return root.createFolder(STUDENT_DATA_EMAIL.APP_FOLDER);
  const f=it.next();if(it.hasNext())throw new Error('Duplicate '+STUDENT_DATA_EMAIL.APP_FOLDER+' folders exist in My Drive.');return f;
}

function replaceCurrentFolder_(app){
  const old=app.getFoldersByName(STUDENT_DATA_EMAIL.CURRENT_FOLDER);while(old.hasNext())old.next().setTrashed(true);
  return app.createFolder(STUDENT_DATA_EMAIL.CURRENT_FOLDER);
}

function getVerifiedReportFile_(row){
  const pkg=readCurrentPackage_(),app=getAppFolder_(),it=app.getFoldersByName(STUDENT_DATA_EMAIL.CURRENT_FOLDER);
  if(!it.hasNext())throw new Error('Current sender package folder is missing.');
  const folder=it.next(),f=DriveApp.getFileById(row.reportFileId);
  if(f.getMimeType()!=='application/pdf')throw new Error('Report attachment is not a PDF');
  if(f.getName()!==row.reportFileName)throw new Error('Report filename no longer matches the loaded package');
  let ok=false,ps=f.getParents();while(ps.hasNext())if(ps.next().getId()===folder.getId()){ok=true;break;}
  if(!ok)throw new Error('Report file is not inside the current sender package');
  if(sha256Bytes_(f.getBlob().getBytes())!==String(row.reportSha256||'').toLowerCase())throw new Error('Report SHA-256 does not match the loaded package');
  return f;
}

function buildSubject_(row){return row.course+' Unit '+row.unit+' Portfolio Update';}
function buildBody_(row,teacherName){
  const first=firstName_(row.studentName),lines=[
    'Hi '+first+',',
    '',
    'Your current '+row.course+' Unit '+row.unit+' Portfolio report is attached.',
    'It shows your progress on each Mastery Goal and what to work on next.',
    '',
    'PowerSchool shows one current grade for each Mastery Goal after we have enough evidence.',
    'I means In Progress. It can change as you show more evidence.'
  ];
  if(row.weeklyNote){lines.push('','Class note:',row.weeklyNote);}
  if(row.studentNote){lines.push('','Note for you:',row.studentNote);}
  lines.push('','-'+teacherName);
  return lines.join('\n');
}

function digestPreview_(pf){return sha256Text_(JSON.stringify({course:pf.course,unit:pf.unit,includeSupportStaff:pf.includeSupportStaff,rows:pf.rows.map(r=>({studentKey:r.studentKey,studentEmail:r.studentEmail,guardianEmails:r.guardianEmails,supportStaffEmails:r.supportStaffEmails,reportSha256:r.reportSha256,weeklyNote:r.weeklyNote,studentNote:r.studentNote,included:r.included,issues:r.issues,warnings:r.warnings,alreadySent:r.alreadySent}))}));}
function guardDigest_(req,pf){if(!req.digest||req.digest!==pf.digest)throw new Error('Preview changed. Run Recheck before sending.');}

function appendSendLog_(row,mode,to,bcc,status,error){
  const app=getAppFolder_(),headers=['send_id','timestamp','mode','course','unit','student_key','report_sha256','to_email','bcc_emails','status','error'],vals=[Utilities.getUuid(),new Date().toISOString(),mode,row.course,row.unit,row.studentKey,row.reportSha256,to,bcc,status,error||''],line=csvLine_(vals)+'\n',f=getOptionalSingleFile_(app,STUDENT_DATA_EMAIL.LOG_FILE);
  if(!f)app.createFile(STUDENT_DATA_EMAIL.LOG_FILE,csvLine_(headers)+'\n'+line,'text/csv');else f.setContent(f.getBlob().getDataAsString('UTF-8').replace(/\s*$/,'\n')+line);
}
function readSendLog_(){const f=getOptionalSingleFile_(getAppFolder_(),STUDENT_DATA_EMAIL.LOG_FILE);return f?readCsvObjects_(f).rows:[];}
function readCsvObjects_(file){const g=Utilities.parseCsv(file.getBlob().getDataAsString('UTF-8').replace(/^\uFEFF/,''));if(!g.length)return{headers:[],rows:[]};const h=g[0].map(x=>String(x||'').trim()),rows=g.slice(1).filter(r=>r.some(v=>String(v||'').trim()!=='')).map(r=>{const o={};h.forEach((k,i)=>o[k]=r[i]==null?'':String(r[i]));return o;});return{headers:h,rows:rows};}
function validateEmailArray_(arr,issues,label){const out=[];const seen=new Set();(Array.isArray(arr)?arr:[]).forEach(v=>{const e=normalizeEmail_(v),k=e.toLowerCase();if(!e||seen.has(k))return;seen.add(k);if(isValidEmail_(e))out.push(e);else issues.push(label+': '+e);});return out;}
function dedupeEmails_(a){const out=[],s=new Set();(a||[]).forEach(e=>{e=normalizeEmail_(e);const k=e.toLowerCase();if(e&&isValidEmail_(e)&&!s.has(k)){s.add(k);out.push(e);}});return out;}
function getConfig_(){const p=PropertiesService.getScriptProperties().getProperties(),c={teacherEmail:String(p.TEACHER_EMAIL||'').trim().toLowerCase(),teacherDisplayName:String(p.TEACHER_DISPLAY_NAME||'').trim()};if(!isValidEmail_(c.teacherEmail)||!c.teacherDisplayName)throw new Error('Missing/invalid TEACHER_EMAIL or TEACHER_DISPLAY_NAME Script Properties.');return c;}
function assertAuthorized_(){const c=getConfig_(),a=String(Session.getActiveUser().getEmail()||'').trim().toLowerCase();if(!a||a!==c.teacherEmail)throw new Error('Access blocked.');return true;}
function getOptionalSingleFile_(f,n){const it=f.getFilesByName(n);if(!it.hasNext())return null;const x=it.next();if(it.hasNext())throw new Error('Duplicate files named '+n);return x;}
function sha256Text_(t){return bytesToHex_(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,String(t),Utilities.Charset.UTF_8));}
function sha256Bytes_(b){return bytesToHex_(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,b));}
function bytesToHex_(b){return b.map(x=>('0'+((x<0?x+256:x).toString(16))).slice(-2)).join('');}
function csvLine_(v){return v.map(x=>{const s=String(x==null?'':x);return /[",\r\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;}).join(',');}
function safeNote_(v){const s=String(v==null?'':v).replace(/\r\n/g,'\n').trim();if(s.length>STUDENT_DATA_EMAIL.NOTE_MAX_LENGTH)throw new Error('A note is too long.');return s;}
function firstName_(n){const s=String(n||'').trim();if(!s)return'student';return s.includes(',')?(s.split(',')[1].trim().split(/\s+/)[0]||s):s.split(/\s+/)[0];}
function normalizeEmail_(v){return String(v||'').trim();}
function isValidEmail_(v){return /^[^\s@,;]+@[^\s@,;]+\.[^\s@,;]+$/.test(String(v||'').trim());}
function baseName_(p){const a=String(p||'').split('/');return a[a.length-1]||'report.pdf';}
function naturalCompare_(a,b){return String(a||'').localeCompare(String(b||''),undefined,{numeric:true,sensitivity:'base'});}
function safeError_(e){return String(e&&e.message?e.message:e||'Unknown error').slice(0,500);}
