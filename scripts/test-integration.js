#!/usr/bin/env node
/**
 * IdeaGPT — PostgreSQL Integration Test Runner
 * Verifies PostgreSQL 18.x readiness, applies alembic migrations,
 * and executes native PostgreSQL integration tests.
 * Usage: node scripts/test-integration.js OR pnpm test:integration
 */

const { spawnSync } = require('child_process');
const path = require('path');
const net = require('net');

const rootDir = path.resolve(__dirname, '..');
const apiDir = path.join(rootDir, 'apps', 'api');

console.log('\n===============================================================');
console.log('🐘 IdeaGPT — PostgreSQL Integration Verification Pipeline');
console.log('===============================================================\n');

function runCmd(cmd, args, options = {}) {
  return spawnSync(cmd, args, {
    cwd: options.cwd || rootDir,
    stdio: options.stdio || 'inherit',
    encoding: 'utf-8',
    shell: options.shell !== undefined ? options.shell : process.platform === 'win32',
    ...options,
  });
}

// 1. Check PostgreSQL Port Connectivity
function checkPostgresPort(host = 'localhost', port = 5432, timeoutMs = 2000) {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    socket.setTimeout(timeoutMs);

    socket.once('connect', () => {
      socket.destroy();
      resolve(true);
    });

    socket.once('timeout', () => {
      socket.destroy();
      resolve(false);
    });

    socket.once('error', () => {
      resolve(false);
    });

    socket.connect(port, host);
  });
}

async function main() {
  process.stdout.write('[1/3] Checking PostgreSQL service on port 5432... ');
  const isPgReady = await checkPostgresPort('localhost', 5432);

  if (!isPgReady) {
    console.error('\n❌ PostgreSQL service is not reachable on localhost:5432.');
    console.error('Please ensure PostgreSQL 18 is running or run: docker compose up -d db');
    process.exit(1);
  }
  console.log('✓ (Online)');

  // 2. Run Alembic Upgrade Head to guarantee schema freshness
  process.stdout.write('[2/3] Verifying database schema with Alembic... \n');
  const alembicRes = runCmd('node', ['run-python.js', '-m', 'alembic', 'upgrade', 'head'], {
    cwd: apiDir,
  });

  if (alembicRes.status !== 0) {
    console.error('\n❌ Alembic migration check failed.');
    process.exit(alembicRes.status || 1);
  }
  console.log('✓ Schema up-to-date (head)');

  // 3. Run Pytest Integration Suite against PostgreSQL
  console.log('\n[3/3] Executing PostgreSQL integration test suite...');
  const pytestRes = runCmd('node', ['run-python.js', '-m', 'pytest', 'tests/integration', '-v'], {
    cwd: apiDir,
  });

  if (pytestRes.status !== 0) {
    console.error('\n❌ PostgreSQL integration tests failed.');
    process.exit(pytestRes.status || 1);
  }

  console.log('\n===============================================================');
  console.log('✅ ALL POSTGRESQL INTEGRATION TESTS PASSED (100% GREEN)');
  console.log('===============================================================\n');
}

main().catch((err) => {
  console.error('Integration test runner error:', err);
  process.exit(1);
});
