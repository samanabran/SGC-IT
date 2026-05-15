const path = require('path');
const { spawn } = require('child_process');

const START_RATE_LIMIT_MS = 30_000;
const MAX_FAILED_ATTEMPTS = 5;
const FAILED_LOCKOUT_MS = 5 * 60_000;
const lastStartByClient = new Map();
const failedAuthByClient = new Map();

function cleanEnv(value) {
  return typeof value === 'string' ? value.trim() : '';
}

function isLoopbackAddress(value) {
  const normalized = cleanEnv(value).toLowerCase();
  return normalized === 'localhost'
    || normalized === '127.0.0.1'
    || normalized === '::1'
    || normalized === '::ffff:127.0.0.1';
}

function isAllowedOrigin(origin) {
  if (!origin) {
    return false;
  }

  try {
    const url = new URL(origin);
    return isLoopbackAddress(url.hostname);
  } catch (error) {
    return false;
  }
}

function isLocalRequest(req) {
  const origin = cleanEnv(req.headers.origin);
  const remoteAddress = cleanEnv(req.socket && req.socket.remoteAddress);
  if (!isLoopbackAddress(remoteAddress)) {
    return false;
  }

  if (origin && !isAllowedOrigin(origin)) {
    return false;
  }

  return true;
}

function getDefaultPythonExecutable() {
  if (process.platform === 'win32') {
    return path.join(process.cwd(), '.venv', 'Scripts', 'python.exe');
  }

  return path.join(process.cwd(), '.venv', 'bin', 'python');
}

function getClientKey(req) {
  return cleanEnv(req.socket && req.socket.remoteAddress) || 'unknown';
}

function hasValidRateLimit(req) {
  const now = Date.now();
  const clientKey = getClientKey(req);
  const previous = lastStartByClient.get(clientKey) || 0;

  if (now - previous < START_RATE_LIMIT_MS) {
    return false;
  }

  lastStartByClient.set(clientKey, now);
  return true;
}

function isClientLockedOut(req) {
  const now = Date.now();
  const clientKey = getClientKey(req);
  const entry = failedAuthByClient.get(clientKey);

  return Boolean(entry && entry.lockedUntil > now);
}

function recordAuthFailure(req) {
  const now = Date.now();
  const clientKey = getClientKey(req);
  const entry = failedAuthByClient.get(clientKey) || { count: 0, lockedUntil: 0 };
  const nextCount = entry.count + 1;

  if (nextCount >= MAX_FAILED_ATTEMPTS) {
    failedAuthByClient.set(clientKey, {
      count: 0,
      lockedUntil: now + FAILED_LOCKOUT_MS,
    });
    return;
  }

  failedAuthByClient.set(clientKey, {
    count: nextCount,
    lockedUntil: 0,
  });
}

function clearAuthFailures(req) {
  const clientKey = getClientKey(req);
  failedAuthByClient.delete(clientKey);
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Serverless runtimes cannot keep long-lived worker processes alive.
  if (process.env.VERCEL === '1') {
    return res.status(501).json({
      error: 'Auto terminal start is not supported on Vercel serverless runtime.'
    });
  }

  const isEnabled = cleanEnv(process.env.ROLEPLAY_WORKER_START_ENABLED).toLowerCase() === 'true';
  if (!isEnabled) {
    return res.status(403).json({
      error: 'Auto worker start is disabled. Set ROLEPLAY_WORKER_START_ENABLED=true to enable.'
    });
  }

  if (!isLocalRequest(req)) {
    return res.status(403).json({
      error: 'Worker start is only allowed from localhost requests.'
    });
  }

  if (isClientLockedOut(req)) {
    return res.status(429).json({
      error: 'Too many failed auth attempts. Try again in a few minutes.'
    });
  }

  const requiredToken = cleanEnv(process.env.ROLEPLAY_WORKER_START_TOKEN);
  if (!requiredToken) {
    return res.status(500).json({
      error: 'ROLEPLAY_WORKER_START_TOKEN is required for worker start.'
    });
  }

  const providedToken = cleanEnv(req.headers['x-worker-start-token']);
  if (requiredToken !== providedToken) {
    recordAuthFailure(req);
    return res.status(401).json({ error: 'Unauthorized worker-start request.' });
  }

  clearAuthFailures(req);

  if (!hasValidRateLimit(req)) {
    return res.status(429).json({
      error: `Rate limit: wait ${Math.floor(START_RATE_LIMIT_MS / 1000)} seconds before starting again.`
    });
  }

  const workerDir = cleanEnv(process.env.ROLEPLAY_WORKER_DIR)
    || path.join(process.cwd(), 'livekit-sales-roleplay');
  const pythonExecutable = cleanEnv(process.env.ROLEPLAY_WORKER_PYTHON)
    || getDefaultPythonExecutable();
  const workerEntry = cleanEnv(process.env.ROLEPLAY_WORKER_ENTRY) || 'agent.py';
  const workerMode = cleanEnv(process.env.ROLEPLAY_WORKER_MODE) || 'dev';

  try {
    const child = spawn(pythonExecutable, [workerEntry, workerMode], {
      cwd: workerDir,
      detached: true,
      stdio: 'ignore',
    });

    child.unref();

    return res.status(200).json({
      started: true,
      pid: child.pid || null,
    });
  } catch (error) {
    return res.status(500).json({
      error: `Unable to start roleplay worker command: ${error.message}`,
    });
  }
};