// Flat ESLint config for FlowFinance.
// Two zones: the embedded inline script (browser, classic <script>) and the worker (module).

const browserGlobals = {
  window: 'readonly', document: 'readonly', console: 'readonly',
  navigator: 'readonly', localStorage: 'readonly', sessionStorage: 'readonly',
  indexedDB: 'readonly', IDBKeyRange: 'readonly',
  Blob: 'readonly', URL: 'readonly', File: 'readonly', FileReader: 'readonly',
  fetch: 'readonly', crypto: 'readonly',
  setTimeout: 'readonly', clearTimeout: 'readonly',
  setInterval: 'readonly', clearInterval: 'readonly',
  requestAnimationFrame: 'readonly', cancelAnimationFrame: 'readonly',
  Image: 'readonly', alert: 'readonly', confirm: 'readonly', prompt: 'readonly',
  Intl: 'readonly', TextEncoder: 'readonly', TextDecoder: 'readonly',
  atob: 'readonly', btoa: 'readonly',
  XMLHttpRequest: 'readonly', AbortController: 'readonly',
  IntersectionObserver: 'readonly', MutationObserver: 'readonly', ResizeObserver: 'readonly',
  FormData: 'readonly', performance: 'readonly', Worker: 'readonly',
  getComputedStyle: 'readonly', matchMedia: 'readonly',
  location: 'readonly', history: 'readonly',
  SpeechRecognition: 'readonly', webkitSpeechRecognition: 'readonly',
  XLSX: 'readonly', visualViewport: 'readonly',
  // App globals exposed only via window.* assignment:
  goalTracker: 'readonly', netWorthTracker: 'readonly'
};

const workerGlobals = {
  Response: 'readonly', Request: 'readonly', Blob: 'readonly', URL: 'readonly',
  fetch: 'readonly', console: 'readonly', Date: 'readonly', JSON: 'readonly',
  Map: 'readonly', crypto: 'readonly',
  setTimeout: 'readonly', clearTimeout: 'readonly'
};

const sharedRules = {
  'no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
  'no-undef': 'error',
  'prefer-const': 'warn',
  eqeqeq: ['warn', 'always'],
  'no-var': 'error',
  'no-empty': ['warn', { allowEmptyCatch: true }],
  'no-redeclare': 'warn'
};

export default [
  {
    files: ['.app-extracted.js'],
    languageOptions: { ecmaVersion: 2023, sourceType: 'script', globals: browserGlobals },
    rules: sharedRules
  },
  {
    files: ['worker/**/*.js'],
    languageOptions: { ecmaVersion: 2023, sourceType: 'module', globals: workerGlobals },
    rules: sharedRules
  }
];
