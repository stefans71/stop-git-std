import { Parser, Language } from "web-tree-sitter";
import { join } from "path";

const EXTENSION_MAP: Record<string, string> = {
  ".ts": "typescript",
  ".tsx": "typescript",
  ".js": "javascript",
  ".jsx": "javascript",
  ".mjs": "javascript",
  ".cjs": "javascript",
  ".py": "python",
  ".rs": "rust",
  ".go": "go",
  ".cs": "c_sharp",
};

const languageCache = new Map<string, Language>();
let initialized = false;

async function ensureInit(): Promise<void> {
  if (initialized) return;
  await Parser.init();
  initialized = true;
}

function getWasmPath(grammarName: string): string {
  return join(
    import.meta.dir,
    "..",
    "..",
    "node_modules",
    "tree-sitter-wasms",
    "out",
    `tree-sitter-${grammarName}.wasm`,
  );
}

async function loadLanguage(grammarName: string): Promise<Language | null> {
  const cached = languageCache.get(grammarName);
  if (cached) return cached;

  try {
    const wasmPath = getWasmPath(grammarName);
    const lang = await Language.load(wasmPath);
    languageCache.set(grammarName, lang);
    return lang;
  } catch (err) {
    console.warn(`[ast] Failed to load grammar "${grammarName}": ${err}`);
    return null;
  }
}

export function getGrammarName(filePath: string): string | null {
  const ext = "." + (filePath.split(".").pop()?.toLowerCase() ?? "");
  return EXTENSION_MAP[ext] ?? null;
}

export async function getParserForFile(filePath: string): Promise<Parser | null> {
  const grammarName = getGrammarName(filePath);
  if (!grammarName) return null;

  await ensureInit();

  const language = await loadLanguage(grammarName);
  if (!language) return null;

  const parser = new Parser();
  parser.setLanguage(language);
  return parser;
}
