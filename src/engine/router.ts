import type { RepoProfile } from "../models/repo-profile.ts";
import type { EngineContract } from "../rules/types.ts";

export interface ActiveModules {
  universal: string[];
  typed: string[];
  all: string[];
}

export function routeModules(
  profile: RepoProfile,
  contract: EngineContract,
  enabledOverrides: string[],
  disabledOverrides: string[],
): ActiveModules {
  const universal = [...contract.module_routing.universal_modules];
  const typed = new Set<string>();

  for (const category of profile.detected_categories) {
    const routes = contract.module_routing.category_routes[category];
    if (routes) {
      for (const mod of routes) typed.add(mod);
    }
  }

  // Merge enabled overrides
  for (const mod of enabledOverrides) {
    if (!universal.includes(mod) && !typed.has(mod)) {
      typed.add(mod);
    }
  }

  // Remove disabled overrides
  const disabledSet = new Set(disabledOverrides);
  const filteredUniversal = universal.filter((m) => !disabledSet.has(m));
  const filteredTyped = [...typed].filter((m) => !disabledSet.has(m));

  return {
    universal: filteredUniversal,
    typed: filteredTyped,
    all: [...filteredUniversal, ...filteredTyped],
  };
}
