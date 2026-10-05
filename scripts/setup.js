#!/usr/bin/env node
/**
 * IdeaGPT Golden Path Bootstrap & Setup Script
 * Idempotent, cross-platform setup for IdeaGPT monorepo.
 * Usage: node scripts/setup.js OR pnpm setup
 */
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const apiDir = path.join(rootDir, 'apps', 'api');
const webDir = path.join(rootDir, 'apps', 'web');
const isWindows = process.platform === 'win32';

console.log('\n===============================================================');
console.log('🚀 IdeaGPT — Golden Path Development Environment Setup');
console.log('===============================================================\n');

function runCmd(cmd, args, options = {}) {
  const res = spawnSync(cmd, args, {
    cwd: options.cwd || rootDir,
    stdio: options.stdio || 'inherit',
    encoding: 'utf-8',
    shell: options.shell !== undefined ? options.shell : false,
    ...options,
  });
  return res;
}

// ---------------------------------------------------------------------------
// 1. Check Node.js Version (>= 22.13.0)
// ---------------------------------------------------------------------------
process.stdout.write('[1/6] Checking Node.js runtime... ');
const nodeVersionMatch = process.version.match(/^v(\d+)\.(\d+)/);
const nodeMajor = nodeVersionMatch ? parseInt(nodeVersionMatch[1], 10) : 0;
const nodeMinor = nodeVersionMatch ? parseInt(nodeVersionMatch[2], 10) : 0;
if (nodeMajor < 22 || (nodeMajor === 22 && nodeMinor < 13)) {
  console.error(`\n❌ Node.js >=22.13.0 is required. Current version: ${process.version}`);
  console.error('Please upgrade Node.js from https://nodejs.org/');
  process.exit(1);
}
console.log(`✓ (${process.version})`);

// ---------------------------------------------------------------------------
// 2. Check pnpm
// ---------------------------------------------------------------------------
process.stdout.write('[2/6] Checking pnpm package manager... ');
const pnpmCmd = isWindows ? 'cmd.exe' : 'pnpm';
const pnpmArgs = isWindows ? ['/d', '/s', '/c', 'pnpm', '--version'] : ['--version'];
const pnpmCheck = runCmd(pnpmCmd, pnpmArgs, { stdio: 'pipe' });
if (pnpmCheck.status !== 0 || !pnpmCheck.stdout) {
  console.error('\n❌ pnpm is not installed or not in PATH.');
  console.error('Please install pnpm via: npm install -g pnpm');
  process.exit(1);
}
const pnpmVersion = pnpmCheck.stdout.trim();
console.log(`✓ (v${pnpmVersion})`);


// ---------------------------------------------------------------------------
// 3. Detect System Python (Authoritative: 3.12)
// ---------------------------------------------------------------------------
process.stdout.write('[3/6] Detecting Python 3.12 runtime... ');
const venvDir = path.join(apiDir, 'venv');
const venvPythonWin = path.join(venvDir, 'Scripts', 'python.exe');
const venvPythonPosix = path.join(venvDir, 'bin', 'python');
const venvPython = isWindows ? venvPythonWin : venvPythonPosix;

const candidateCommands = isWindows
  ? [['py', ['-3.12']], ['python3.12', []], ['py', []], ['python', []]]
  : [['python3.12', []], ['python3', []], ['python', []]];

let selectedPythonCmd = null;
let selectedPythonArgs = [];
let pythonVersionOutput = '';

for (const [cmd, args] of candidateCommands) {
  const probeArgs = [...args, '-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"); sys.exit(0 if (sys.version_info.major == 3 and sys.version_info.minor == 12) else 1)'];
  const probe = runCmd(cmd, probeArgs, { stdio: 'pipe' });
  if (probe.status === 0 && probe.stdout) {
    selectedPythonCmd = cmd;
    selectedPythonArgs = args;
    pythonVersionOutput = probe.stdout.trim();
    break;
  }
}

if (!selectedPythonCmd) {
  console.error('\n❌ Python 3.12 was not found on your system.');
  console.error('The repository contract strictly requires Python 3.12 to match CI, Docker, and production.');
  console.error('Please install Python 3.12 from: https://www.python.org/downloads/release/python-3120/');
  process.exit(1);
}
const fullPythonName = selectedPythonArgs.length > 0 ? `${selectedPythonCmd} ${selectedPythonArgs.join(' ')}` : selectedPythonCmd;
console.log(`✓ (${fullPythonName} -> Python ${pythonVersionOutput})`);

// ---------------------------------------------------------------------------
// 4. Safe Environment File Bootstrapping
// ---------------------------------------------------------------------------
console.log('[4/6] Bootstrapping environment templates...');

function safeCopyEnv(srcRel, destRel) {
  const src = path.join(rootDir, srcRel);
  const dest = path.join(rootDir, destRel);
  if (!fs.existsSync(dest)) {
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, dest);
      console.log(`    ✓ Created ${destRel} from template (secrets safe)`);
    } else {
      console.log(`    ⚠ Template ${srcRel} missing; skipped creating ${destRel}`);
    }
  } else {
    console.log(`    ✓ Preserved existing ${destRel} (secrets untouched)`);
  }
}

safeCopyEnv('apps/api/.env.example', 'apps/api/.env');
safeCopyEnv('apps/web/.env.example', 'apps/web/.env.local');
safeCopyEnv('.env.example', '.env');

// ---------------------------------------------------------------------------
// 5. Python Virtual Environment Setup (apps/api/venv)
// ---------------------------------------------------------------------------
console.log('[5/6] Initializing Python virtual environment in apps/api/venv...');

let needCreateVenv = !fs.existsSync(venvPython);
if (fs.existsSync(venvPython)) {
  const venvProbe = runCmd(venvPython, ['-c', 'import sys; sys.exit(0 if (sys.version_info.major == 3 and sys.version_info.minor == 12) else 1)'], { stdio: 'pipe' });
  if (venvProbe.status !== 0) {
    console.log('    ⚠ Existing virtual environment is not Python 3.12. Recreating...');
    try {
      fs.rmSync(venvDir, { recursive: true, force: true });
    } catch (e) {}
    needCreateVenv = true;
  }
}

if (needCreateVenv) {
  console.log(`    Creating virtual environment using ${fullPythonName}...`);
  const createArgs = [...selectedPythonArgs, '-m', 'venv', 'venv'];
  const createVenv = runCmd(selectedPythonCmd, createArgs, { cwd: apiDir });
  if (createVenv.status !== 0 || !fs.existsSync(venvPython)) {
    console.error(`\n❌ Failed to create virtualenv in ${venvDir}`);
    console.error('Please verify your Python venv module is installed.');
    process.exit(1);
  }
  console.log('    ✓ Virtual environment created successfully.');
} else {
  console.log('    ✓ Existing Python 3.12 virtual environment verified.');
}


console.log('    Installing / verifying backend dependencies (requirements-dev.txt)...');
const pipInstall = runCmd(venvPython, ['-m', 'pip', 'install', '-r', 'requirements-dev.txt'], { cwd: apiDir });
if (pipInstall.status !== 0) {
  console.error('\n❌ Failed to install Python dependencies from requirements-dev.txt');
  process.exit(1);
}
console.log('    ✓ Backend dependencies up to date.');

// ---------------------------------------------------------------------------
// 6. Docker & Optional Infrastructure Check
// ---------------------------------------------------------------------------
process.stdout.write('[6/6] Checking local infrastructure (Docker/PostgreSQL/Redis)... ');
const dockerCmd = isWindows ? 'cmd.exe' : 'docker';
const dockerArgs = isWindows ? ['/d', '/s', '/c', 'docker', 'compose', 'version'] : ['compose', 'version'];
const dockerCheck = runCmd(dockerCmd, dockerArgs, { stdio: 'pipe' });
if (dockerCheck.status === 0) {

  console.log('✓ Docker Compose available.');
  console.log('    Tip: Run `pnpm db:up` to launch local PostgreSQL 15 & Redis 7.');
} else {
  console.log('ℹ Docker not detected.');
  console.log('    Local unit tests and mock development operate via SQLite automatically.');
}

console.log('\n===============================================================');
console.log('🎉 IdeaGPT Developer Environment Setup Complete!');
console.log('===============================================================');
console.log('\nCanonical developer commands:');
console.log('  pnpm dev         → Start Next.js (port 3000) & FastAPI (port 8000)');
console.log('  pnpm test        → Run full test suite (backend pytest + frontend vitest)');
console.log('  pnpm typecheck   → Run TypeScript static verification');
console.log('  pnpm lint        → Run monorepo linters');
console.log('  pnpm build       → Build production monorepo bundles');
console.log('  pnpm clean       → Clean temporary caches & build artifacts');
console.log('  pnpm db:up       → Start local PostgreSQL & Redis in Docker (optional)');
console.log('===============================================================\n');
