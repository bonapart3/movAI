# movAI

Movie streaming locator - An AI-powered application to help locate movie streaming services

## Features

- 🎬 Find where movies are streaming
- 🤖 AI-powered recommendations
- 🔍 Smart search capabilities
- 📊 Streaming service comparisons

## Prerequisites

- Node.js (v18 or higher)
- npm or yarn

## Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/bonapart3/movAI.git
cd movAI
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` and add your API keys and configuration.

### Development

Run the development server with hot reload:
```bash
npm run dev
```

### Building

Build the TypeScript code:
```bash
npm run build
```

### Running in Production

```bash
npm start
```

## Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build TypeScript to JavaScript
- `npm start` - Run the production build
- `npm test` - Run tests
- `npm run test:watch` - Run tests in watch mode
- `npm run lint` - Lint the code
- `npm run lint:fix` - Lint and fix issues
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting

## Project Structure

```
movAI/
├── src/                 # Source files
│   ├── index.ts        # Application entry point
│   └── utils/          # Utility functions
├── tests/              # Test files
├── dist/               # Compiled JavaScript (generated)
├── public/             # Static assets
├── .env.example        # Example environment variables
├── package.json        # Project dependencies
├── tsconfig.json       # TypeScript configuration
└── README.md          # This file
```

## Testing

Run the test suite:
```bash
npm test
```

Run tests with coverage:
```bash
npm test -- --coverage
```

## Code Quality

This project uses:
- **TypeScript** for type safety
- **ESLint** for code linting
- **Prettier** for code formatting
- **Jest** for testing

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
