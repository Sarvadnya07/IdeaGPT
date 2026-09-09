#!/usr/bin/env node
/**
 * Cross-platform artifact and cache cleanup script for IdeaGPT monorepo.
 * Usage: node scripts/clean.js [--deep]
 */
const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const isDeep = process.argv.includes('--deep');

const safeArtifacts = [
  path.join(rootDir, '.turbo'),
  path.join(rootDir, '.pytest_cache'),
  path.join(rootDir, 'apps', 'web', '.next'),
  path.join(rootDir, 'apps', 'web', '.turbo'),
  path.join(rootDir, 'apps', 'web', 'test-results'),
  path.join(rootDir, 'apps', 'web', 'playwright-report'),
  path.join(rootDir, 'apps', 'api', '.pytest_cache'),
  path.join(rootDir, 'apps', 'api', '__pycache__'),
  path.join(rootDir, 'apps', 'api', 'app', '__pycache__'),
  path.join(rootDir, 'apps', 'api', 'tests', '__pycache__'),
  path.join(rootDir, 'test.db'),
  path.join(rootDir, 'apps', 'api', 'test.db'),
  path.join(rootDir, 'apps', 'api', 'alembic_test.db'),
];

console.log(`\n🧹 Cleaning IdeaGPT build artifacts & caches${isDeep ? ' (DEEP MODE)' : ''}...`);

const protectedPatterns = [
  /\.env(\..+)?$/i,
  /pnpm-lock\.yaml$/i,
  /package\.json$/i,
  /requirements.*\.txt$/i,
  /[/\\]alembic[/\\]versions[/\\][^/\\]+\.py$/i,
  /[/\\]app[/\\][^/\\]+\.py$/i,
];


function isProtected(targetPath) {
  return protectedPatterns.some((pattern) => pattern.test(targetPath));
}

for (const target of safeArtifacts) {
  if (isProtected(target)) {
    console.warn(`  🛡️ SKIPPED (Protected path): ${path.relative(rootDir, target)}`);
    continue;
  }
  if (fs.existsSync(target)) {
    try {
      fs.rmSync(target, { recursive: true, force: true });
      console.log(`  ✓ Removed: ${path.relative(rootDir, target)}`);
    } catch (err) {
      console.warn(`  ⚠ Could not remove ${path.relative(rootDir, target)}: ${err.message}`);
    }
  }
}


if (isDeep) {
  console.log('\n[Deep Clean] Removing node_modules and venv...');
  const deepTargets = [
    path.join(rootDir, 'node_modules'),
    path.join(rootDir, 'apps', 'web', 'node_modules'),
    path.join(rootDir, 'apps', 'api', 'node_modules'),
    path.join(rootDir, 'packages', 'ui', 'node_modules'),
    path.join(rootDir, 'packages', 'typescript-config', 'node_modules'),
    path.join(rootDir, 'apps', 'api', 'venv'),
  ];
  for (const target of deepTargets) {
    if (fs.existsSync(target)) {
      try {
        fs.rmSync(target, { recursive: true, force: true });
        console.log(`  ✓ Removed: ${path.relative(rootDir, target)}`);
      } catch (err) {
        console.warn(`  ⚠ Could not remove ${path.relative(rootDir, target)}: ${err.message}`);
      }
    }
  }
  console.log('\nDeep clean complete. Run `pnpm setup` to restore your environment.');
} else {
  console.log('\n✓ Clean complete. Source code, secrets (.env), and dependencies preserved.');
}
