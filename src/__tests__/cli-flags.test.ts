import { test, expect, describe } from "bun:test";
import { AuditRequestSchema } from "../models/audit-request.ts";

function parseRequest(overrides: Record<string, unknown> = {}) {
  return AuditRequestSchema.parse({
    repo_target: "owner/repo",
    ...overrides,
  });
}

describe("CLI depth flags", () => {
  test("defaults to depth_mode='auto'", () => {
    const req = parseRequest();
    expect(req.depth_mode).toBe("auto");
  });

  test("depth_mode='quick' is accepted", () => {
    const req = parseRequest({ depth_mode: "quick" });
    expect(req.depth_mode).toBe("quick");
  });

  test("depth_mode='deep' is accepted", () => {
    const req = parseRequest({ depth_mode: "deep" });
    expect(req.depth_mode).toBe("deep");
  });

  test("invalid depth_mode is rejected", () => {
    expect(() => parseRequest({ depth_mode: "invalid" })).toThrow();
  });
});
