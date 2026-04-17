import { parse as parseYaml } from "yaml";

export interface K8sPolicyRule {
  apiGroups?: string[];
  resources?: string[];
  verbs?: string[];
  resourceNames?: string[];
}

export interface ParsedK8sResource {
  apiVersion?: string;
  kind?: string;
  name?: string;
  namespace?: string;
  /** For Role / ClusterRole: the rules array */
  rules?: K8sPolicyRule[];
  /** Whether any rule contains wildcard ("*") in verbs or resources */
  hasWildcardRules: boolean;
  raw: Record<string, unknown>;
}

const RBAC_KINDS = new Set(["Role", "ClusterRole", "RoleBinding", "ClusterRoleBinding"]);

function hasWildcard(rules: K8sPolicyRule[]): boolean {
  for (const rule of rules) {
    if (
      rule.verbs?.includes("*") ||
      rule.resources?.includes("*") ||
      rule.apiGroups?.includes("*")
    ) {
      return true;
    }
  }
  return false;
}

function parseRules(raw: unknown): K8sPolicyRule[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((r) => {
    if (!r || typeof r !== "object") return {};
    const rule = r as Record<string, unknown>;
    return {
      apiGroups: Array.isArray(rule.apiGroups)
        ? (rule.apiGroups as string[])
        : undefined,
      resources: Array.isArray(rule.resources)
        ? (rule.resources as string[])
        : undefined,
      verbs: Array.isArray(rule.verbs) ? (rule.verbs as string[]) : undefined,
      resourceNames: Array.isArray(rule.resourceNames)
        ? (rule.resourceNames as string[])
        : undefined,
    };
  });
}

function parseDocument(raw: unknown): ParsedK8sResource | null {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null;
  const doc = raw as Record<string, unknown>;

  const kind = typeof doc.kind === "string" ? doc.kind : undefined;
  const apiVersion = typeof doc.apiVersion === "string" ? doc.apiVersion : undefined;

  const metadata = doc.metadata as Record<string, unknown> | undefined;
  const name = typeof metadata?.name === "string" ? metadata.name : undefined;
  const namespace =
    typeof metadata?.namespace === "string" ? metadata.namespace : undefined;

  const rules = RBAC_KINDS.has(kind ?? "") ? parseRules(doc.rules) : undefined;
  const wildcardRules = rules ? hasWildcard(rules) : false;

  return {
    apiVersion,
    kind,
    name,
    namespace,
    rules,
    hasWildcardRules: wildcardRules,
    raw: doc,
  };
}

/**
 * Parse a Kubernetes YAML file (may contain multiple documents separated by ---).
 * Returns a ParsedK8sResource for each document.
 * Detects Role/ClusterRole definitions with wildcard rules.
 */
export function parseK8sYaml(content: string): ParsedK8sResource[] {
  // Split on YAML document separators
  const documents = content.split(/^---\s*$/m);
  const results: ParsedK8sResource[] = [];

  for (const doc of documents) {
    const trimmed = doc.trim();
    if (!trimmed) continue;

    let parsed: unknown;
    try {
      parsed = parseYaml(trimmed);
    } catch {
      continue;
    }

    const resource = parseDocument(parsed);
    if (resource) {
      results.push(resource);
    }
  }

  return results;
}
