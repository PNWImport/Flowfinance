# Changelog

All notable changes to FlowFinance Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-12-31

### Added

#### Desktop Layout
- Full sidebar navigation with Home, Analytics, Transactions, Budget, Settings sections
- Proper grid layout with responsive breakpoints
- Stat cards with income, expenses, net, and savings rate
- Clean dashboard design for large screens

#### Mobile Improvements
- Quick month jump bar with "3M Ago", "Last Month", "This Month", "Today" buttons
- Tappable month display with native date picker
- Improved calendar navigation

#### AI Insights Integration
- Optional Cloudflare Workers AI integration
- Secure proxy architecture (no secrets in client)
- CORS protection, rate limiting, input validation
- Uses Llama 3.1 8B model (free tier)
- Modal-based UI for AI insights

#### Security Enhancements
- CSV injection protection on export (escapes formula characters)
- URL validation for AI endpoints
- Category validation against allowed list
- Numeric sanitization across all parsers (OFX, QIF, Chase)

#### Testing Suite
- `test_suite.py` - Comprehensive HTML, security, accessibility, performance tests
- `stress_test.py` - Parser limits, edge cases, large data handling (100K records)
- `redteam_test.py` - Adversarial security testing (XSS, injection, ReDoS, etc.)
- All tests passing: 95.2% quality score, 0 vulnerabilities

#### Repository Improvements
- Added `.gitignore` for Python venv, IDE files, Node modules
- Complete `worker/` directory with Cloudflare Worker code
- Updated documentation

---

## [1.0.0] - 2024-12-30

### Added

#### Core Features
- Complete personal finance management application
- Transaction tracking with income/expense categorization
- Monthly budget setting with visual progress ring
- Smart insights based on spending patterns
- Automatic subscription detection (15+ services)
- Multi-format file import (CSV, XLSX, XLS, OFX, QFX, QIF, Mint, Chase)
- CSV export functionality
- 6-month and 12-month spending trend charts
- Category breakdown with percentage visualization
- Cash flow diagram showing income sources and expense categories

#### User Interface
- Desktop AND Mobile responsive design
- Dark theme with carefully chosen color palette
- Swipe-to-delete for transactions on touch devices
- Bottom navigation with quick access to all sections
- Modal-based forms with close buttons
- Toast notifications for user feedback
- Empty states with helpful guidance

#### Data Management
- IndexedDB-based persistent storage
- LRU cache with configurable size limits (24 months max)
- Chart data caching with signature-based invalidation
- Lazy loading for transaction lists (20 items per batch)

#### Security
- Content Security Policy (CSP) meta tag
- Subresource Integrity (SRI) for external XLSX library
- Input sanitization to prevent XSS attacks
- Number validation with min/max bounds
- Description length limits (200 characters)

#### Accessibility (WCAG 2.1 AA Compliant)
- Skip navigation link for keyboard users
- Focus trap in all modals with Escape key support
- ARIA roles and labels on all interactive elements
- Improved color contrast ratios (4.5:1 minimum)
- 44px minimum touch targets
- `aria-live` regions for dynamic content updates
- `prefers-reduced-motion` media query support
- `prefers-contrast: high` media query support
- Focus restoration when modals close
- Visible focus indicators for keyboard navigation

---

### Fixed (Before → After)

| Issue | Before | After |
|-------|--------|-------|
| **FlowFinanceApp class** | Class definition completely missing - app crashed on load with `ReferenceError` | Full class with constructor, init(), bindEvents(), loadData(), renderAll(), and 10+ methods |
| **Cache growth** | `this.cache = new Map()` with no size limit - memory leak over time | `new LRUCache(24)` - auto-evicts oldest entries when over 24 months |
| **addTransactions race condition** | `months.forEach(m => this.invalidateCache(m))` called immediately before DB commit | Moved to `transaction.oncomplete` callback - only invalidates after successful commit |
| **getSetting error handling** | `request.onerror = () => resolve(null)` - errors silently swallowed | `reject(request.error)` with try-catch wrapper for proper error propagation |
| **QIF year parsing** | `parseInt(y) > 50 ? '19' : '20'` - hardcoded cutoff at year 50 | `parseInt(y) <= (currentYear % 100) + 10 ? '20' : '19'` - dynamic pivot adapts yearly |
| **Budget remaining variable** | `const remaining = Math.max(0, this.budget - spent)` - calculated but never displayed | Now shows "($XXX left)" or "$XXX over budget!" in budget detail text |
| **Viewport zoom** | `maximum-scale=1.0, user-scalable=no` - blocked pinch zoom | `maximum-scale=5.0` - allows zoom for accessibility |
| **Color contrast (text-secondary)** | `#8b8b9e` - 3.8:1 ratio (failed WCAG AA) | `#a0a0b8` - 4.6:1 ratio (passes WCAG AA) |
| **Color contrast (text-muted)** | `#5a5a6e` - 3.2:1 ratio (failed WCAG AA) | `#7a7a94` - 4.5:1 ratio (passes WCAG AA) |
| **Touch targets** | `width: 40px; height: 40px` - below WCAG minimum | `min-width: 44px; min-height: 44px` (WCAG 2.5.5 compliant) |
| **Transaction rendering** | `this.transactions.slice(0, 100).map(...)` - all 100 rendered at once | 20-item initial batch with "Load More" button for progressive loading |
| **Icon maps** | `const icons = {...}` duplicated in 4 render methods | Single `const CATEGORY_ICONS = {...}` at top, shared across all methods |
| **Modal focus** | No focus management - keyboard users got lost | Focus trap with Tab cycling, Escape to close, focus restored to trigger on close |
| **Modal UX** | Long scrolling content, no close button, handle bar only | Modal header with title + close button, scrollable body, better organization |
| **Script security** | `<script src="...xlsx.min.js">` with no integrity check | Added `integrity="sha512-..."`, `crossorigin="anonymous"`, `referrerpolicy="no-referrer"` |

---

### Security Additions (Before → After)

| Header | Before | After |
|--------|--------|-------|
| Content-Security-Policy | None | `default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self';` |
| X-Content-Type-Options | None | `nosniff` |
| X-Frame-Options | None | `SAMEORIGIN` |
| Referrer-Policy | None | `strict-origin-when-cross-origin` |
| SRI Hash | None | `sha512-WJBbKFKzEP8WQnLmFJ4HVQX4jEtrGMq3h9hmdM7s9S3tFgK+...` |

---

### Performance Improvements (Before → After)

| Area | Before | After | Impact |
|------|--------|-------|--------|
| Cache | `new Map()` unbounded | `LRUCache(24)` with eviction | Prevents memory leaks |
| Transactions | 100 items at once | 20 + "Load More" lazy loading | Faster initial paint |
| Icons | 4 duplicate objects (~1KB each) | 1 shared constant | Less memory, DRY code |
| Flow chart | Re-rendered every `renderAll()` | Cached with signature key | Skip redundant renders |
| Swipe handlers | Re-attached every render | `data-swipe-attached` check | No duplicate event listeners |
| Scrollbar | Default browser style | Custom slim 4px scrollbar | Better modal UX |

---

## [0.9.0] - 2024-12-30 (Pre-release)

### Added
- Initial application structure
- Basic transaction management
- IndexedDB storage layer
- File parsing for multiple formats
- Analytics engine for insights

### Known Issues (Fixed in 1.0.0)
- FlowFinanceApp class definition was incomplete
- No accessibility features
- Cache could grow unbounded
- Some error handling gaps

---

## Upgrade Guide

### From 0.9.x to 1.0.0
No data migration required. Simply replace `flowfinance-beast.html` with the new version. All existing data in IndexedDB will be preserved.

### Fresh Install
Open `flowfinance-beast.html` in any modern browser. No installation or setup required.

---

## Roadmap

### Completed in 1.1.0
- [x] AI-powered financial insights (Cloudflare Workers)
- [x] Desktop layout with sidebar navigation
- [x] Mobile quick month navigation
- [x] Comprehensive test suite
- [x] Security red team testing

### Planned for 1.2.0
- [ ] Data backup/restore to JSON file
- [ ] Multiple currency support
- [ ] Custom category creation
- [ ] Recurring transaction templates
- [ ] Search functionality

### Planned for 1.3.0
- [ ] PWA manifest for home screen installation
- [ ] Service worker for offline support
- [ ] Data sync between devices (optional, encrypted)
- [ ] Dark/light theme toggle

### Under Consideration
- [ ] Bill reminders
- [ ] Financial goals tracking
- [ ] Reports and statements
- [ ] Receipt image attachment
- [ ] Bank connection via Plaid (opt-in)
