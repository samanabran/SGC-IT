const crypto = require('crypto');
const { AccessToken, AgentDispatchClient } = require('livekit-server-sdk');

const ALLOWED_PERSONAS = new Set(['p1_faisal', 'p2_noura', 'p3_omar', 'p4_rajesh']);

function cleanEnv(value) {
  return typeof value === 'string' ? value.trim() : '';
}

function sanitizeSegment(value, fallback, maxLength) {
  if (typeof value !== 'string') {
    return fallback;
  }

  const cleaned = value.trim().replace(/[^a-zA-Z0-9_-]/g, '-').slice(0, maxLength);
  return cleaned || fallback;
}

function logEvent(level, event, data) {
  const logger = level === 'error' ? console.error : console.log;
  logger(JSON.stringify({ event, ...data }));
}

module.exports = async (req, res) => {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  res.setHeader('Cache-Control', 'no-store, max-age=0');
  res.setHeader('Pragma', 'no-cache');

  const wsUrl = cleanEnv(process.env.LIVEKIT_URL);
  const apiKey = cleanEnv(process.env.LIVEKIT_API_KEY);
  const apiSecret = cleanEnv(process.env.LIVEKIT_API_SECRET);
  const agentName = sanitizeSegment(process.env.LIVEKIT_AGENT_NAME, 'test-agent', 60);
  const enableDispatch = process.env.LIVEKIT_ENABLE_DISPATCH !== 'false';
  const ttl = cleanEnv(process.env.LIVEKIT_TOKEN_TTL) || '15m';

  if (!/^\d+[smh]$/.test(ttl)) {
    return res.status(500).json({
      error: 'LIVEKIT_TOKEN_TTL must use number + s/m/h format, for example 15m or 1h.'
    });
  }

  if (!wsUrl || !apiKey || !apiSecret) {
    return res.status(500).json({
      error: 'Missing server environment variables. Configure LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET in Vercel.'
    });
  }

  if (!/^wss?:\/\//.test(wsUrl)) {
    return res.status(500).json({
      error: 'LIVEKIT_URL must start with ws:// or wss://.'
    });
  }

  const persona = typeof req.query.persona === 'string' && ALLOWED_PERSONAS.has(req.query.persona)
    ? req.query.persona
    : 'p1_faisal';

  const identityBase = sanitizeSegment(req.query.identity, 'sales-user', 40);

  const room = sanitizeSegment(req.query.room, `roleplay-${persona}-${Date.now()}`, 60);

  const identity = `${identityBase}-${crypto.randomUUID().slice(0, 8)}`;

  const token = new AccessToken(apiKey, apiSecret, {
    identity,
    ttl,
    metadata: JSON.stringify({ persona })
  });

  token.addGrant({
    room,
    roomJoin: true,
    canPublish: true,
    canSubscribe: true,
    canPublishData: true
  });

  let dispatch = null;
  let dispatchError = null;
  if (enableDispatch) {
    try {
      const apiHost = wsUrl.replace(/^wss:\/\//, 'https://').replace(/^ws:\/\//, 'http://');
      const dispatchClient = new AgentDispatchClient(apiHost, apiKey, apiSecret);
      const dispatchMetadata = JSON.stringify({
        persona,
        user_id: identity,
      });
      dispatch = await dispatchClient.createDispatch(room, agentName, { metadata: dispatchMetadata });
    } catch (error) {
      dispatchError = `Failed to dispatch agent '${agentName}': ${error.message}`;
      logEvent('error', 'roleplay_dispatch_failed', {
        room,
        persona,
        identity,
        agentName,
        message: error.message,
        timestamp: new Date().toISOString(),
      });
    }
  }

  let jwt;
  try {
    jwt = await token.toJwt();
  } catch (error) {
    logEvent('error', 'roleplay_token_failed', {
      room,
      persona,
      identity,
      message: error.message,
      timestamp: new Date().toISOString(),
    });
    return res.status(500).json({
      error: 'Failed to generate access token.'
    });
  }

  logEvent('info', 'roleplay_token_issued', {
    room,
    persona,
    identity,
    dispatchCreated: Boolean(dispatch),
    dispatchError: dispatchError || null,
    timestamp: new Date().toISOString(),
  });

  return res.status(200).json({
    wsUrl,
    room,
    persona,
    identity,
    token: jwt,
    expiresIn: ttl,
    dispatchId: dispatch ? dispatch.id : null,
    dispatchCreated: Boolean(dispatch),
    dispatchError,
  });
};
