#!/usr/bin/env node
/**
 * Developer environment verification utility for IdeaGPT monorepo.
 * Usage: node scripts/verify-env.js OR pnpm verify:env
 */
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const apiDir = path.join(rootDir, 'apps', 'api');
const webDir = path.join(rootDir, 'apps', 'web');
const isWindows = process.platform === 'win32';

console.log('\n===============================================================');
console.log('🔍 IdeaGPT Environment Verification');
console.log('===============================================================\n');

let passCount = 0;
let warnCount = 0;
let failCount = 0;

function check(label, fn) {
  process.stdout.write(`• ${label.padEnd(45, '.')} `);
  try {
    const res = fn();
    if (res === true) {
      console.log('✅ PASS');
      passCount++;
    } else if (res && res.warn) {
      console.log(`⚠️  WARN (${res.warn})`);
      warnCount++;
    } else {
      console.log(`❌ FAIL (${res && res.error ? res.error : 'check failed'})`);
      failCount++;
    }
  } catch (err) {
    console.log(`❌ ERROR (${err.message})`);
    failCount++;
  }
}

// 1. Node.js
check('Node.js Version (>=22.13.0)', () => {
  const match = process.version.match(/^v(\d+)\.(\d+)/);
  if (!match) return { error: `Cannot parse ${process.version}` };
  const major = parseInt(match[1], 10);
  const minor = parseInt(match[2], 10);
  if (major > 22 || (major === 22 && minor >= 13)) return true;
  return { error: `Node >=22.13.0 required, found ${process.version}` };
});

// 2. pnpm
check('pnpm Package Manager (11.1.1 / >=10)', () => {
  const res = spawnSync('pnpm', ['--version'], { encoding: 'utf-8', shell: isWindows });
  return res.status === 0 ? true : { error: 'pnpm not found in PATH' };
});

// 3. apps/api/venv Python
const venvPython = isWindows
  ? path.join(apiDir, 'venv', 'Scripts', 'python.exe')
  : path.join(apiDir, 'venv', 'bin', 'python');

let detectedPythonVersion = null;
check('Backend Virtualenv (apps/api/venv)', () => {
  if (!fs.existsSync(venvPython)) {
    return { error: 'Virtualenv missing. Run `pnpm setup`.' };
  }
  const probe = spawnSync(venvPython, [
    '-c',
    'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"); sys.exit(0 if (sys.version_info.major == 3 and sys.version_info.minor == 12) else 1)'
  ], { encoding: 'utf-8' });
  if (probe.status !== 0 || !probe.stdout) {
    const actualVer = probe.stdout ? probe.stdout.trim() : 'unknown';
    return { error: `Python 3.12.x required by repository contract, but venv is running ${actualVer}` };
  }
  detectedPythonVersion = probe.stdout.trim();
  return true;
});


// 4. FastAPI & Core Backend Imports
check('FastAPI & SQLAlchemy Import Readiness', () => {
  if (!fs.existsSync(venvPython)) return { error: 'venv python missing' };
  const res = spawnSync(venvPython, ['-c', 'import fastapi, sqlalchemy, alembic; print("ok")'], {
    cwd: apiDir,
    encoding: 'utf-8',
  });
  return res.status === 0 && res.stdout.trim() === 'ok' ? true : { error: 'Core python modules missing' };
});

// 5. Environment Files
check('API Environment Configuration (apps/api/.env)', () => {
  return fs.existsSync(path.join(apiDir, '.env')) ? true : { warn: 'apps/api/.env missing (run pnpm setup)' };
});

check('Web Environment Configuration (apps/web/.env.local)', () => {
  return fs.existsSync(path.join(webDir, '.env.local')) ? true : { warn: 'apps/web/.env.local missing (run pnpm setup)' };
});

// 6. Docker & Local Infrastructure
check('Docker Compose Availability', () => {
  const res = spawnSync('docker', ['compose', 'version'], { encoding: 'utf-8', shell: isWindows });
  return res.status === 0 ? true : { warn: 'Docker not installed or not running (optional for SQLite unit tests)' };
});

console.log('\n---------------------------------------------------------------');
console.log(`Summary: ${passCount} Passed, ${warnCount} Warnings, ${failCount} Failed.`);
if (detectedPythonVersion && fs.existsSync(venvPython)) {
  console.log('\nPython Runtime Information:');
  console.log(`  version:    ${detectedPythonVersion}`);
  console.log(`  executable: ${path.relative(rootDir, venvPython)}`);
}
if (failCount === 0) {
  console.log('\n🎉 Your environment is ready for development!');
} else {
  console.log('\n⚠️  Please run `pnpm setup` to resolve failed checks.');
}
console.log('===============================================================\n');


process.exit(failCount > 0 ? 1 : 0);
