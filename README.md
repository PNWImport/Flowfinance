# FlowFinance Pro

A powerful, privacy-first personal finance management app that runs entirely in your browser. No servers, no accounts, no data collection - your financial data stays on your device.

![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![PWA Ready](https://img.shields.io/badge/PWA-ready-purple.svg)
![Desktop & Mobile](https://img.shields.io/badge/platform-Desktop%20%26%20Mobile-orange.svg)

## Features

### Core Functionality
- **Transaction Tracking** - Add income and expenses with categories, dates, and descriptions
- **Monthly Overview** - Navigate between months to see historical data
- **Budget Management** - Set monthly budgets with visual progress tracking
- **Smart Insights** - AI-powered analysis of your spending patterns
- **Subscription Detection** - Automatically identifies recurring charges (Netflix, Spotify, etc.)

### Data Management
- **Multi-Format Import** - CSV, Excel (XLSX/XLS), OFX/QFX (bank exports), QIF (Quicken), Mint, Chase
- **CSV Export** - Export all transactions for backup or analysis
- **Offline Storage** - Uses IndexedDB for persistent local storage
- **No Cloud Required** - All data stays on your device

### User Experience
- **Responsive Design** - Optimized for desktop, tablet, AND mobile
- **Desktop Mode** - Full sidebar navigation with proper dashboard layout
- **Mobile Mode** - Full-width layout with touch gestures and quick month navigation
- **Quick Month Jump** - Buttons for "3M Ago", "Last Month", "This Month", "Today"
- **Dark Theme** - Easy on the eyes, designed for extended use
- **Swipe to Delete** - Intuitive touch gestures for transaction management (mobile)
- **Keyboard Navigation** - Full keyboard support for desktop users
- **AI Insights** - Optional Cloudflare Workers AI integration for financial analysis

### Accessibility (WCAG 2.1 AA)
- Full keyboard navigation with visible focus indicators
- Screen reader compatible with ARIA labels
- Skip navigation link for keyboard users
- Focus trap in modals with Escape key support
- High contrast mode support
- Reduced motion support
- Minimum 44px touch targets

## Quick Start

### Option 1: Direct Use
Simply open `flowfinance-beast.html` in any modern browser. That's it!

```bash
# Clone the repository
git clone https://github.com/PNWImport/Flowfinance.git

# Open in browser
open flowfinance-beast.html
# or
xdg-open flowfinance-beast.html  # Linux
start flowfinance-beast.html      # Windows
```

### Option 2: Serve Locally
For PWA features and better caching:

```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx serve .

# Using PHP
php -S localhost:8000
```

Then visit `http://localhost:8000/flowfinance-beast.html`

### Option 3: Deploy to Web
Upload `flowfinance-beast.html` to any static hosting:
- GitHub Pages
- Netlify
- Vercel
- Cloudflare Pages
- Any web server

## Usage Guide

### Adding Transactions
1. Tap the **+** button in the bottom navigation
2. Select **Income** or **Expense**
3. Enter description, amount, date, and category
4. Tap **Add Transaction**

### Setting a Budget
1. Tap **Set Budget** in Quick Actions or the **Edit** link
2. Enter your monthly spending limit
3. Watch the progress ring track your spending

### Importing Data
1. Tap the **Import** button (📥) in the header
2. Select your file format
3. Choose your bank export file
4. Transactions are automatically categorized

### Navigating Months
- Use the **◀** and **▶** arrows to move between months
- All data is preserved and instantly accessible

### Deleting Transactions
- On mobile: Swipe left on any transaction, then release
- Keyboard: Focus the transaction and use the delete action

## Technical Details

### Architecture
- **Single HTML File** - Complete application in one portable file
- **Vanilla JavaScript** - No frameworks, minimal dependencies
- **IndexedDB** - Browser-native database for persistence
- **CSS Custom Properties** - Themeable design system

### Browser Support
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

### External Dependencies
- [SheetJS (xlsx)](https://sheetjs.com/) - Excel file parsing (loaded from CDN with SRI)

### Security
- Content Security Policy (CSP) headers
- Subresource Integrity (SRI) for external scripts
- Input sanitization for XSS prevention
- CSV injection protection on export
- URL validation for AI endpoints
- Category validation against allowed list
- No external data transmission
- No cookies or tracking

### Testing
- **Comprehensive Test Suite** - HTML, security, accessibility, performance checks
- **Stress Testing** - Parser limits, edge cases, large data handling
- **Red Team Security** - XSS, injection, prototype pollution, ReDoS testing

### Performance
- LRU caching for database queries
- Lazy loading for transaction lists
- Cached chart rendering
- Optimized re-renders with signature checking

## File Structure

```
Flowfinance/
├── flowfinance-beast.html   # Complete application (~135KB)
├── README.md                # This file
├── CHANGELOG.md             # Version history
├── LICENSE                  # MIT License
├── .gitignore               # Git ignore patterns
├── tests/                   # Test suite
│   ├── test_suite.py        # Comprehensive test suite
│   ├── stress_test.py       # Parser stress testing
│   └── redteam_test.py      # Security red team tests
└── worker/                  # Cloudflare AI Worker (optional)
    ├── src/index.js         # Worker source code
    ├── wrangler.toml        # Worker configuration
    └── README.md            # Worker documentation
```

## Privacy

FlowFinance Pro is designed with privacy as a core principle:

- **No accounts** - No sign-up, no login
- **No servers** - Runs entirely in your browser
- **No tracking** - No analytics, no cookies
- **No data collection** - Your data never leaves your device
- **Local storage only** - Uses IndexedDB in your browser

To clear all data, use your browser's "Clear site data" function.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development
Since this is a single HTML file, development is straightforward:

1. Edit `flowfinance-beast.html`
2. Refresh browser to see changes
3. Test on multiple devices/browsers
4. Submit PR with clear description

### Code Style
- Use 2-space indentation
- Prefer `const` over `let`
- Use template literals for HTML
- Add ARIA labels for accessibility
- Test with keyboard navigation

### Running Tests
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install beautifulsoup4

# Run test suite (95%+ quality score expected)
python tests/test_suite.py flowfinance-beast.html

# Run stress tests
python tests/stress_test.py

# Run security red team tests
python tests/redteam_test.py flowfinance-beast.html
```

## AI Insights (Optional)

FlowFinance can optionally connect to a Cloudflare Worker for AI-powered financial insights:

1. Deploy the worker from `worker/` directory
2. Click the 🤖 AI Insights button in the app
3. Enter your Worker URL
4. Get personalized spending analysis

See [worker/README.md](worker/README.md) for setup instructions.

**Security**: No financial data is stored on the server - it's processed and discarded immediately.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Icons: Native emoji for maximum compatibility
- Font: System UI fonts for native feel
- Inspiration: Mint, YNAB, and other great finance apps

---

**Made with care for your financial privacy.**
