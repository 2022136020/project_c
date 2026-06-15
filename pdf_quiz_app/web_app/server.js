import "dotenv/config";
import express from "express";
import multer from "multer";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { createRequire } from "module";
import OpenAI from "openai";

const require = createRequire(import.meta.url);
const pdfParse = require("pdf-parse");

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;
const MAX_TEXT_CHARS = 20000;

const openai = new OpenAI({
  apiKey: process.env.OPENROUTER_API_KEY,
  baseURL: "https://openrouter.ai/api/v1",
  defaultHeaders: {
    "HTTP-Referer": "http://localhost:3000",
    "X-Title": "PDF Quiz App",
  },
});

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

const uploadsDir = path.join(__dirname, "uploads");
if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir, { recursive: true });

const upload = multer({
  storage: multer.diskStorage({
    destination: (req, file, cb) => cb(null, uploadsDir),
    filename: (req, file, cb) => cb(null, `${Date.now()}-${file.originalname}`),
  }),
  fileFilter: (req, file, cb) => {
    if (file.mimetype === "application/pdf") cb(null, true);
    else cb(new Error("PDF 파일만 업로드 가능합니다."));
  },
  limits: { fileSize: 50 * 1024 * 1024 },
});

async function extractPdfText(filePath) {
  const buffer = fs.readFileSync(filePath);
  const data = await pdfParse(buffer);
  return data.text || "";
}

async function extractQuestionsWithAI(text, pdfNames) {
  const truncated = text.length > MAX_TEXT_CHARS
    ? text.slice(0, MAX_TEXT_CHARS) + "\n...(이하 생략)"
    : text;

  const prompt = `다음 PDF 텍스트에서 퀴즈 문제를 모두 추출해 JSON 배열로 반환하세요.

반환 형식:
[
  {
    "type": "multiple_choice",
    "question": "문제 내용",
    "choices": ["선택지1", "선택지2", "선택지3", "선택지4"],
    "answer": "2",
    "explanation": "해설"
  },
  {
    "type": "short_answer",
    "question": "문제 내용",
    "choices": [],
    "answer": "정답",
    "explanation": ""
  },
  {
    "type": "true_false",
    "question": "문제 내용",
    "choices": [],
    "answer": "true",
    "explanation": ""
  }
]

규칙:
- type: "multiple_choice"(객관식), "short_answer"(단답/서술), "true_false"(OX)
- 객관식: choices 배열 필수, answer는 정답 번호 문자열("1","2","3","4","5")
- 단답형: choices는 빈 배열, answer는 정답 텍스트
- OX: choices는 빈 배열, answer는 "true" 또는 "false"
- 정답 불명확 시 answer는 빈 문자열
- JSON 배열만 반환, 다른 텍스트 없이
- 문제 없으면 []

PDF 내용:
${truncated}`;

  const response = await openai.chat.completions.create({
    model: "anthropic/claude-3.5-haiku",
    messages: [{ role: "user", content: prompt }],
    temperature: 0.1,
    max_tokens: 4096,
  });

  const content = response.choices[0].message.content.trim();
  const jsonMatch = content.match(/\[[\s\S]*\]/);
  if (!jsonMatch) throw new Error("AI 응답에서 JSON을 찾을 수 없습니다.");

  const raw = JSON.parse(jsonMatch[0]);
  const validTypes = new Set(["multiple_choice", "short_answer", "true_false"]);

  return raw
    .filter((q) => q && typeof q.question === "string" && q.question.trim().length > 3)
    .map((q, i) => ({
      id: i + 1,
      type: validTypes.has(q.type) ? q.type : "short_answer",
      question: q.question.trim(),
      choices: Array.isArray(q.choices) ? q.choices.map(String) : [],
      answer: String(q.answer ?? "").trim(),
      explanation: String(q.explanation ?? "").trim(),
      source: pdfNames.join(", "),
    }));
}

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.post("/api/upload", upload.array("pdfs", 10), async (req, res) => {
  if (!req.files || req.files.length === 0) {
    return res.status(400).json({ error: "PDF 파일을 업로드해주세요." });
  }

  const files = req.files;

  try {
    let combinedText = "";
    const pdfNames = [];

    for (const file of files) {
      try {
        const text = await extractPdfText(file.path);
        if (text.trim()) {
          combinedText += `\n\n=== ${file.originalname} ===\n${text}`;
          pdfNames.push(file.originalname);
        }
      } catch (e) {
        console.error(`PDF 파싱 오류 (${file.originalname}):`, e.message);
      }
    }

    if (!combinedText.trim()) {
      return res
        .status(422)
        .json({ error: "PDF에서 텍스트를 추출할 수 없습니다. 스캔된 이미지 PDF는 지원하지 않습니다." });
    }

    const questions = await extractQuestionsWithAI(combinedText, pdfNames);

    if (questions.length === 0) {
      return res
        .status(422)
        .json({ error: "문제를 찾을 수 없습니다. 문제가 포함된 PDF를 업로드해주세요." });
    }

    res.json({ success: true, questions, total: questions.length, pdf_name: pdfNames });
  } catch (err) {
    console.error("처리 오류:", err.message);
    res.status(500).json({ error: `서버 오류: ${err.message}` });
  } finally {
    files.forEach((f) => fs.unlink(f.path, () => {}));
  }
});

// 에러 핸들러
app.use((err, req, res, _next) => {
  res.status(400).json({ error: err.message });
});

app.listen(PORT, () => {
  console.log(`서버 실행 중: http://localhost:${PORT}`);
});
