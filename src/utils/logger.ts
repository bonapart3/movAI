type LogLevel = 'info' | 'warn' | 'error' | 'debug';

class Logger {
  private logLevel: LogLevel;

  constructor() {
    this.logLevel = (process.env.LOG_LEVEL as LogLevel) || 'info';
  }

  private log(level: LogLevel, message: string, ...args: unknown[]) {
    const timestamp = new Date().toISOString();
    const formattedMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;

    // eslint-disable-next-line no-console
    console[level === 'error' ? 'error' : 'log'](formattedMessage, ...args);
  }

  info(message: string, ...args: unknown[]) {
    this.log('info', message, ...args);
  }

  warn(message: string, ...args: unknown[]) {
    this.log('warn', message, ...args);
  }

  error(message: string, ...args: unknown[]) {
    this.log('error', message, ...args);
  }

  debug(message: string, ...args: unknown[]) {
    if (this.logLevel === 'debug') {
      this.log('debug', message, ...args);
    }
  }
}

export const logger = new Logger();
