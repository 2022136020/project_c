import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { createRequire } from "module";
import fs from "fs";

const require = createRequire(import.meta.url);
const pdfParse = require("pdf-parse");

// MCP 서버 초기화
const server = new Server(
  { name: "pdf-reader", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// ─────────────────────────────────────────────
// 도구 목록 등록
// ─────────────────────────────────────────────
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "read_pdf_text",
        description: "PDF 파일 전체 텍스트를 추출합니다.",
        inputSchema: {
          type: "object",
          properties: {
            file_path: {
              type: "string",
              description: "읽을 PDF 파일의 절대 경로 또는 상대 경로",
            },
          },
          required: ["file_path"],
        },
      },
      {
        name: "get_pdf_metadata",
        description: "PDF 파일의 메타데이터(페이지 수, 텍스트 길이)를 반환합니다.",
        inputSchema: {
          type: "object",
          properties: {
            file_path: {
              type: "string",
              description: "조회할 PDF 파일의 절대 경로 또는 상대 경로",
            },
          },
          required: ["file_path"],
        },
      },
      {
        name: "extract_page_range",
        description: "PDF 파일의 특정 페이지 범위에 해당하는 텍스트를 추출합니다.",
        inputSchema: {
          type: "object",
          properties: {
            file_path: {
              type: "string",
              description: "PDF 파일의 절대 경로 또는 상대 경로",
            },
            start_page: {
              type: "number",
              description: "시작 페이지 번호 (1-based)",
            },
            end_page: {
              type: "number",
              description: "끝 페이지 번호 (1-based, inclusive)",
            },
          },
          required: ["file_path", "start_page", "end_page"],
        },
      },
    ],
  };
});

// ─────────────────────────────────────────────
// 공통 유틸리티
// ─────────────────────────────────────────────

/**
 * 파일 존재 여부를 확인하고 Buffer를 반환합니다.
 * @param {string} filePath
 * @returns {Buffer}
 */
function readFileBuffer(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`파일을 찾을 수 없습니다: ${filePath}`);
  }
  return fs.readFileSync(filePath);
}

/**
 * pdf-parse를 호출하되, 페이지별 텍스트를 수집하는 옵션을 추가합니다.
 * pageTexts 배열에 각 페이지 텍스트가 순서대로 쌓입니다.
 * @param {Buffer} buffer
 * @returns {{ data: object, pageTexts: string[] }}
 */
async function parsePdf(buffer) {
  const pageTexts = [];

  const options = {
    // pdf-parse의 pagerender 콜백: 페이지마다 호출됨
    pagerender(pageData) {
      return pageData.getTextContent().then((textContent) => {
        const pageText = textContent.items.map((item) => item.str).join(" ");
        pageTexts.push(pageText);
        return pageText;
      });
    },
  };

  const data = await pdfParse(buffer, options);
  return { data, pageTexts };
}

// ─────────────────────────────────────────────
// 도구 핸들러
// ─────────────────────────────────────────────
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    // ── 1. read_pdf_text ──────────────────────
    if (name === "read_pdf_text") {
      const { file_path } = args;

      const buffer = readFileBuffer(file_path);
      // 줄바꿈 보존을 위해 커스텀 pagerender 없이 기본 pdf-parse 사용
      const data = await pdfParse(buffer);

      return {
        content: [
          {
            type: "text",
            text: data.text || "(텍스트를 추출할 수 없습니다.)",
          },
        ],
      };
    }

    // ── 2. get_pdf_metadata ───────────────────
    if (name === "get_pdf_metadata") {
      const { file_path } = args;

      const buffer = readFileBuffer(file_path);
      const { data } = await parsePdf(buffer);

      const metadata = {
        pages: data.numpages,
        text_length: (data.text || "").length,
      };

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(metadata, null, 2),
          },
        ],
      };
    }

    // ── 3. extract_page_range ─────────────────
    if (name === "extract_page_range") {
      const { file_path, start_page, end_page } = args;

      if (start_page < 1) {
        throw new Error("start_page는 1 이상이어야 합니다.");
      }
      if (end_page < start_page) {
        throw new Error("end_page는 start_page 이상이어야 합니다.");
      }

      const buffer = readFileBuffer(file_path);
      const { data, pageTexts } = await parsePdf(buffer);

      const totalPages = data.numpages;

      if (start_page > totalPages) {
        throw new Error(
          `start_page(${start_page})가 총 페이지 수(${totalPages})를 초과합니다.`
        );
      }

      // pageTexts가 정상적으로 채워진 경우 사용, 아니면 전체 텍스트 반환
      let resultText;
      if (pageTexts.length > 0) {
        const clampedEnd = Math.min(end_page, totalPages);
        // 1-based → 0-based 인덱스
        const selected = pageTexts.slice(start_page - 1, clampedEnd);
        resultText = selected.join("\n\n--- 페이지 구분 ---\n\n");

        if (resultText.trim() === "") {
          resultText = "(지정한 페이지 범위에서 텍스트를 추출할 수 없습니다.)";
        }
      } else {
        // pagerender 콜백이 작동하지 않은 경우 전체 텍스트로 대체
        resultText = data.text || "(텍스트를 추출할 수 없습니다.)";
      }

      return {
        content: [
          {
            type: "text",
            text: resultText,
          },
        ],
      };
    }

    // ── 알 수 없는 도구 ───────────────────────
    throw new Error(`알 수 없는 도구: ${name}`);
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `오류: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// ─────────────────────────────────────────────
// 서버 시작
// ─────────────────────────────────────────────
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  // stdio transport 사용 시 console.error로만 로깅 (stdout은 MCP 프로토콜 전용)
  console.error("PDF Reader MCP 서버가 시작되었습니다.");
}

main().catch((error) => {
  console.error("서버 시작 실패:", error);
  process.exit(1);
});
