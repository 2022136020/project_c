import pdfParse from 'pdf-parse/lib/pdf-parse.js';
import fs from 'fs';
const buf = fs.readFileSync('C:/project_c/tmp_pdfs/06주차_API연동_냉장고를부탁해.pdf');
const data = await pdfParse(buf);
const text = data.text;
const sectionMatches = [...text.matchAll(/셀프\s*체크[^\n]*/g)];
sectionMatches.forEach(m => {
  console.log(`pos ${m.index}: ${m[0].trim()}`);
});
console.log('---');
// 문제 N. 위치
const qMatches = [...text.matchAll(/문제\s*\d+\./g)];
qMatches.forEach(m => console.log(`  q pos ${m.index}: ${text.slice(m.index, m.index+50).replace(/\n/g,'↵')}`));
