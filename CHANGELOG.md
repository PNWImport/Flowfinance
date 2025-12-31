# Changelog

All notable changes to FlowFinance Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-31

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
- Mobile-first responsive design
- Dark theme with carefully chosen color palette
- Swipe-to-delete for transactions on touch devices
- Bottom navigation with quick access to all sections
- Modal-based forms for adding transactions and settings
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

#### Performance
- Single HTML file architecture (no build step required)
- Shared CATEGORY_ICONS constant (eliminated 4 duplications)
- DocumentFragment for efficient batch DOM updates
- Optimized swipe handler attachment (prevents re-binding)
- Cached flow chart rendering

### Fixed
- Missing FlowFinanceApp class definition (critical bug)
- Race condition in bulk transaction imports
- Unbounded cache growth causing memory issues
- Two-digit year parsing in QIF files (now uses dynamic pivot)
- Error swallowing in getSetting database calls
- Unused `remaining` variable in budget display

### Security
- Added CSP headers to prevent XSS attacks
- Added SRI hash for XLSX CDN resource
- Added `crossorigin` and `referrerpolicy` attributes

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

### Planned for 1.1.0
- [ ] Data backup/restore to JSON file
- [ ] Multiple currency support
- [ ] Custom category creation
- [ ] Recurring transaction templates
- [ ] Search functionality

### Planned for 1.2.0
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
