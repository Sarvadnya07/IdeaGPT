#!/usr/bin/env node
/**
 * Cross-platform Python runner for IdeaGPT Backend (apps/api)
 * Automatically locates the project virtualenv (Windows & POSIX)
 * or provides a clear, actionable diagnostic message if missing.
 */
const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const apiDir = __dirname;
const isWindows = process.platform === 'win32';

// Check for virtualenv python
const venvPythonWin = path.join(apiDir, 'venv', 'Scripts', 'python.exe');
const venvPythonPosix = path.join(apiDir, 'venv', 'bin', 'python');
const venvPython = isWindows ? venvPythonWin : venvPythonPosix;

let pythonExec = null;

if (fs.existsSync(venvPython)) {
  pythonExec = venvPython;
}


if (!pythonExec) {
  console.error('\n================================================================');
  console.error('❌ [IdeaGPT Backend Error] Python environment not initialized!');
  console.error('----------------------------------------------------------------');
  console.error(`Expected virtual environment at: ${path.relative(process.cwd(), venvPython)}`);
  console.error('Please run the following command from the repository root:');
  console.error('\n    pnpm setup\n');
  console.error('This will automatically create the virtualenv and install all dependencies.');
  console.error('================================================================\n');
  process.exit(1);
}

const args = process.argv.slice(2);
const result = spawnSync(pythonExec, args, {
  cwd: apiDir,
  stdio: 'inherit',
  env: {
    ...process.env,
    PYTHONUNBUFFERED: '1',
  },
});

process.exit(result.status !== null ? result.status : 1);
