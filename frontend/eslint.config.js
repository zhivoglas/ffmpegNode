import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default [
  { ignores: ['dist'] },

  // 1. Конфиг для Frontend (React + Browser)
  {
    files: ['src/**/*.{js,jsx}'], // Применяем только к папке src
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]', argsIgnorePattern: '^_' }],
    },
  },

  // 2. Конфиг для Electron Main Process (Node.js)
  {
    files: ['main.cjs', 'preload.cjs', '**/main/*.js'], // Укажите пути к файлам Electron
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'commonjs',
      globals: {
        ...globals.node,    // Добавляет process, __dirname и т.д.
        ...globals.mocha,   // Если есть тесты
      },
    },
    rules: {
      'no-unused-vars': ['warn', { argsIgnorePattern: '^e$' }], // Чтобы не ругался на (e) в эвентах
      'no-undef': 'error',
    },
  },
]
