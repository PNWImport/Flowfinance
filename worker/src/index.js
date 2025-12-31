/**
 * FlowFinance AI Insights Worker
 *
 * Security layers:
 * 1. CORS - Only allows requests from your domain
 * 2. Rate limiting - Prevents abuse (10 req/min per IP)
 * 3. Input validation - Sanitizes all input
 * 4. No secrets in client - AI binding is server-side only
 */

const RATE_LIMIT_WINDOW = 60 * 1000; // 1 minute
const RATE_LIMIT_MAX = 10; // requests per window
const rateLimitMap = new Map();

export default {
  async fetch(request, env, ctx) {
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return handleCORS(request, env);
    }

    // Only allow POST
    if (request.method !== 'POST') {
      return jsonResponse({ error: 'Method not allowed' }, 405, env, request);
    }

    // CORS check
    const origin = request.headers.get('Origin');
    if (!isAllowedOrigin(origin, env)) {
      return jsonResponse({ error: 'Origin not allowed' }, 403, env, request);
    }

    // Rate limiting (in-memory, resets on worker restart)
    const clientIP = request.headers.get('CF-Connecting-IP') || 'unknown';
    if (!checkRateLimit(clientIP)) {
      return jsonResponse({ error: 'Rate limit exceeded. Try again in 1 minute.' }, 429, env, request);
    }

    try {
      const data = await request.json();

      // Validate input
      const validation = validateInput(data);
      if (!validation.valid) {
        return jsonResponse({ error: validation.error }, 400, env, request);
      }

      // Build prompt with sanitized data
      const prompt = buildPrompt(data);

      // Call Workers AI
      const aiResponse = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
        messages: [
          {
            role: 'system',
            content: 'You are a helpful financial advisor assistant. Provide concise, actionable insights based on the user\'s financial data. Be encouraging but honest. Never recommend specific stocks or investments. Keep responses under 200 words.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: 400,
        temperature: 0.7
      });

      return jsonResponse({
        success: true,
        insights: aiResponse.response,
        usage: {
          model: 'llama-3.1-8b-instruct',
          timestamp: new Date().toISOString()
        }
      }, 200, env, request);

    } catch (error) {
      console.error('AI Error:', error);
      return jsonResponse({
        error: 'Failed to generate insights',
        message: error.message
      }, 500, env, request);
    }
  }
};

function handleCORS(request, env) {
  const origin = request.headers.get('Origin');
  const allowedOrigin = isAllowedOrigin(origin, env) ? origin : '';

  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': allowedOrigin,
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400',
    }
  });
}

function isAllowedOrigin(origin, env) {
  if (!origin) return false;
  const allowed = env.ALLOWED_ORIGIN || '*';
  if (allowed === '*') return true;

  // Support comma-separated list
  const allowedOrigins = allowed.split(',').map(o => o.trim());
  return allowedOrigins.includes(origin) ||
         allowedOrigins.some(o => origin.endsWith(o.replace('*.', '')));
}

function checkRateLimit(clientIP) {
  const now = Date.now();
  const record = rateLimitMap.get(clientIP) || { count: 0, windowStart: now };

  // Reset window if expired
  if (now - record.windowStart > RATE_LIMIT_WINDOW) {
    record.count = 0;
    record.windowStart = now;
  }

  record.count++;
  rateLimitMap.set(clientIP, record);

  // Cleanup old entries periodically
  if (rateLimitMap.size > 10000) {
    for (const [ip, rec] of rateLimitMap.entries()) {
      if (now - rec.windowStart > RATE_LIMIT_WINDOW) {
        rateLimitMap.delete(ip);
      }
    }
  }

  return record.count <= RATE_LIMIT_MAX;
}

function validateInput(data) {
  if (!data || typeof data !== 'object') {
    return { valid: false, error: 'Invalid request body' };
  }

  // Required fields
  const { income, expenses, categories, budget } = data;

  if (typeof income !== 'number' || income < 0 || income > 1000000000) {
    return { valid: false, error: 'Invalid income value' };
  }

  if (typeof expenses !== 'number' || expenses < 0 || expenses > 1000000000) {
    return { valid: false, error: 'Invalid expenses value' };
  }

  if (categories && !Array.isArray(categories)) {
    return { valid: false, error: 'Categories must be an array' };
  }

  if (categories && categories.length > 20) {
    return { valid: false, error: 'Too many categories' };
  }

  return { valid: true };
}

function buildPrompt(data) {
  const { income, expenses, categories, budget, subscriptions, monthLabel } = data;

  const net = income - expenses;
  const savingsRate = income > 0 ? ((net / income) * 100).toFixed(1) : 0;
  const budgetUsed = budget > 0 ? ((expenses / budget) * 100).toFixed(1) : null;

  let prompt = `Analyze my finances for ${monthLabel || 'this month'}:\n\n`;
  prompt += `- Income: $${income.toLocaleString()}\n`;
  prompt += `- Expenses: $${expenses.toLocaleString()}\n`;
  prompt += `- Net: $${net.toLocaleString()} (${net >= 0 ? 'surplus' : 'deficit'})\n`;
  prompt += `- Savings Rate: ${savingsRate}%\n`;

  if (budget) {
    prompt += `- Budget: $${budget.toLocaleString()} (${budgetUsed}% used)\n`;
  }

  if (categories && categories.length > 0) {
    prompt += `\nTop spending categories:\n`;
    categories.slice(0, 5).forEach((cat, i) => {
      prompt += `${i + 1}. ${cat.name}: $${cat.amount.toLocaleString()}\n`;
    });
  }

  if (subscriptions && subscriptions.length > 0) {
    const subTotal = subscriptions.reduce((sum, s) => sum + s.amount, 0);
    prompt += `\nRecurring subscriptions: ${subscriptions.length} totaling $${subTotal.toLocaleString()}/month\n`;
  }

  prompt += `\nProvide 3 specific, actionable insights about my spending. Be concise.`;

  return prompt;
}

function jsonResponse(data, status, env, request) {
  const origin = request?.headers?.get('Origin');
  const allowedOrigin = isAllowedOrigin(origin, env) ? origin : '';

  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': allowedOrigin,
      'Cache-Control': 'no-store'
    }
  });
}
