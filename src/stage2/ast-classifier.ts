import type { Parser, Node } from "web-tree-sitter";

export type AstClassification = "dismiss" | "confirm" | "ambiguous";

export interface ClassificationResult {
  classification: AstClassification;
  reason: string;
  nodeType: string;
}

const DISMISS_NODE_TYPES = new Set([
  "string",
  "string_literal",
  "interpreted_string_literal",
  "raw_string_literal",
  "template_string",
  "template_literal_type",
  "string_content",
  "string_fragment",
  "comment",
  "line_comment",
  "block_comment",
  "verbatim_string_literal",
  "interpolated_string_expression",
]);

const CONFIRM_NODE_TYPES = new Set([
  "call_expression",
  "call",
  "invocation_expression",
  "member_access_expression",
  "import_statement",
  "import_from_statement",
  "use_declaration",
  "import_declaration",
  "using_directive",
  "assignment_expression",
  "assignment_statement",
]);

function classifyNodeType(nodeType: string): AstClassification | null {
  if (DISMISS_NODE_TYPES.has(nodeType)) return "dismiss";
  if (CONFIRM_NODE_TYPES.has(nodeType)) return "confirm";
  return null;
}

function classifyAtPosition(
  rootNode: Node,
  row: number,
  column: number,
): ClassificationResult | null {
  const node = rootNode.descendantForPosition({ row, column });
  if (!node) return null;

  let current = node;
  for (let i = 0; i < 5; i++) {
    const classification = classifyNodeType(current.type);
    if (classification !== null) {
      const reason = classification === "dismiss"
        ? `Match is inside ${current.type} — not executable code`
        : `Match is part of ${current.type} — potentially dangerous`;
      return { classification, reason, nodeType: current.type };
    }
    if (!current.parent) break;
    current = current.parent;
  }

  return null;
}

export function classifyMatchContext(
  parser: Parser,
  sourceCode: string,
  lineNumber: number,
  matchText: string,
): ClassificationResult {
  let tree;
  try {
    tree = parser.parse(sourceCode);
  } catch {
    return { classification: "ambiguous", reason: "Failed to parse source code", nodeType: "error" };
  }

  if (!tree) {
    return { classification: "ambiguous", reason: "Parser returned no tree", nodeType: "error" };
  }

  try {
    // tree-sitter rows are 0-indexed, findings are 1-indexed
    const row = lineNumber - 1;
    const rootNode = tree.rootNode;

    // Find the column where the match text appears on this line
    const lines = sourceCode.split("\n");
    const line = lines[row] ?? "";

    // If we have match text, find its column; otherwise sample multiple positions
    const columns: number[] = [];
    if (matchText) {
      let searchFrom = 0;
      while (true) {
        const idx = line.indexOf(matchText, searchFrom);
        if (idx === -1) break;
        columns.push(idx + Math.floor(matchText.length / 2));
        searchFrom = idx + 1;
      }
    }
    if (columns.length === 0) {
      // Sample multiple positions across the line
      const trimmedStart = line.length - line.trimStart().length;
      columns.push(trimmedStart, Math.floor(line.length / 2));
    }

    // Classify at each column position; return the first definitive result
    let bestResult: ClassificationResult | null = null;
    for (const col of columns) {
      const result = classifyAtPosition(rootNode, row, col);
      if (result) {
        // Dismiss and confirm are definitive
        if (result.classification === "dismiss" || result.classification === "confirm") {
          return result;
        }
        if (!bestResult) bestResult = result;
      }
    }

    if (bestResult) return bestResult;

    const node = rootNode.descendantForPosition({ row, column: 0 });
    return {
      classification: "ambiguous",
      reason: `Match is in ${node?.type ?? "unknown"} context — unable to determine intent`,
      nodeType: node?.type ?? "unknown",
    };
  } finally {
    tree.delete();
  }
}
