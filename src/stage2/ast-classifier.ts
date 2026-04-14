import type { Parser } from "web-tree-sitter";

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

export function classifyMatchContext(
  parser: Parser,
  sourceCode: string,
  lineNumber: number,
  _matchText: string,
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

    // Find the deepest named node at this line
    let node = rootNode.descendantForPosition({ row, column: 0 });
    if (!node) {
      return { classification: "ambiguous", reason: "No node found at line", nodeType: "unknown" };
    }

    // Walk up the ancestor chain (up to 5 levels) to find a classifiable node
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

    return {
      classification: "ambiguous",
      reason: `Match is in ${node.type} context — unable to determine intent`,
      nodeType: node.type,
    };
  } finally {
    tree.delete();
  }
}
