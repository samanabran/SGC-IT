const { AccessToken, AgentDispatchClient } = require('livekit-server-sdk');

const ALLOWED_PERSONAS = new Set(['p1_faisal', 'p2_noura', 'p3_omar', 'p4_rajesh']);

module.exports = async (req, res) => {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const wsUrl = process.env.LIVEKIT_URL;
  const apiKey = process.env.LIVEKIT_API_KEY;
  const apiSecret = process.env.LIVEKIT_API_SECRET;
  const agentName = process.env.LIVEKIT_AGENT_NAME || 'test-agent';
  const enableDispatch = process.env.LIVEKIT_ENABLE_DISPATCH !== 'false';

  if (!wsUrl || !apiKey || !apiSecret) {
    return res.status(500).json({
      error: 'Missing server environment variables. Configure LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET in Vercel.'
    });
  }

  const persona = typeof req.query.persona === 'string' && ALLOWED_PERSONAS.has(req.query.persona)
    ? req.query.persona
    : 'p1_faisal';

  const identityBase = typeof req.query.identity === 'string' && req.query.identity.trim()
    ? req.query.identity.trim().slice(0, 40)
    : 'sales-user';

  const room = typeof req.query.room === 'string' && req.query.room.trim()
    ? req.query.room.trim().slice(0, 60)
    : `roleplay-${persona}-${Date.now()}`;

  const identity = `${identityBase}-${Math.floor(Math.random() * 100000)}`;

  const token = new AccessToken(apiKey, apiSecret, {
    identity,
    ttl: '15m',
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
    }
  }

  return res.status(200).json({
    wsUrl,
    room,
    persona,
    agentName,
    identity,
    token: await token.toJwt(),
    expiresIn: '15m',
    dispatch,
    dispatchError,
  });
};
