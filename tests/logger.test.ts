import { logger } from '../src/utils/logger';

describe('Logger', () => {
  beforeEach(() => {
    // Clear console mocks before each test
    jest.spyOn(console, 'log').mockImplementation();
    jest.spyOn(console, 'error').mockImplementation();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should log info messages', () => {
    logger.info('Test message');
    expect(console.log).toHaveBeenCalled();
  });

  it('should log error messages', () => {
    logger.error('Error message');
    expect(console.error).toHaveBeenCalled();
  });

  it('should log warn messages', () => {
    logger.warn('Warning message');
    expect(console.log).toHaveBeenCalled();
  });
});
