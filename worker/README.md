# FlowFinance AI Worker

Cloudflare Worker that provides AI-powered financial insights using Workers AI (free tier).

## Security Model

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  FlowFinance    │ ───► │  CF Worker       │ ───► │  Workers AI     │
│  (HTML Client)  │      │  (Secure Edge)   │      │  (Llama 3.1 8B) │
│                 │      │                  │      │                 │
│  No secrets!    │      │  ✓ CORS          │      │  No API key     │
│  Public code    │      │  ✓ Rate limit    │      │  needed - it's  │
│                 │      │  ✓ Validation    │      │  auto-bound     │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

**Why this is secure:**
1. **No API keys in client** - The HTML app has zero secrets
2. **CORS protection** - Worker only accepts requests from your domain
3. **Rate limiting** - 10 requests/minute per IP prevents abuse
4. **Input validation** - All data is sanitized before processing
5. **Workers AI binding** - No API key needed, access is automatic

## Setup

### 1. Install Wrangler CLI

```bash
npm install -g wrangler
wrangler login
```

### 2. Configure your domain

Edit `wrangler.toml`:

```toml
[vars]
ALLOWED_ORIGIN = "https://your-domain.com"
# For local testing: ALLOWED_ORIGIN = "*"
```

### 3. Deploy

```bash
cd worker
wrangler deploy
```

You'll get a URL like: `https://flowfinance-ai.YOUR-SUBDOMAIN.workers.dev`

### 4. Update FlowFinance App

Add your Worker URL to the app (see client integration below).

## Free Tier Limits

- **10,000 neurons/day** - roughly 100-300 requests
- **No credit card required**
- **Global edge deployment** - fast everywhere

## API Usage

### Request

```bash
POST https://flowfinance-ai.YOUR-SUBDOMAIN.workers.dev

Content-Type: application/json

{
  "income": 5000,
  "expenses": 3500,
  "budget": 4000,
  "monthLabel": "December 2024",
  "categories": [
    { "name": "Food", "amount": 800 },
    { "name": "Housing", "amount": 1500 },
    { "name": "Transport", "amount": 400 }
  ],
  "subscriptions": [
    { "name": "Netflix", "amount": 15.99 },
    { "name": "Spotify", "amount": 9.99 }
  ]
}
```

### Response

```json
{
  "success": true,
  "insights": "Based on your December finances:\n\n1. **Strong savings rate** - You're saving 30% of income ($1,500). This exceeds the recommended 20%.\n\n2. **Food spending is high** - At $800 (23% of expenses), consider meal prepping to reduce by $200/month.\n\n3. **Subscription audit** - Your $26/month in subscriptions is reasonable, but review if you use both streaming services equally.",
  "usage": {
    "model": "llama-3.1-8b-instruct",
    "timestamp": "2024-12-31T10:30:00.000Z"
  }
}
```

## Client Integration

Add this to your FlowFinance app:

```javascript
async function getAIInsights() {
  const response = await fetch('https://flowfinance-ai.YOUR-SUBDOMAIN.workers.dev', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      income: this.analytics.totalIncome,
      expenses: this.analytics.totalExpenses,
      budget: this.budget,
      monthLabel: this.currentMonth,
      categories: this.analytics.getTopCategories(5),
      subscriptions: this.analytics.getSubscriptions()
    })
  });

  const data = await response.json();
  if (data.success) {
    this.showAIInsights(data.insights);
  }
}
```

## Local Development

```bash
wrangler dev
# Opens local server at http://localhost:8787
```

For local testing, set `ALLOWED_ORIGIN = "*"` in wrangler.toml.

## Cost

**$0** - Workers AI free tier is sufficient for personal use.

If you exceed free tier:
- Workers AI: $0.011 per 1,000 neurons
- Typical request: ~30-50 neurons
- 1,000 requests ≈ $0.50
