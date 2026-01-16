# Testing Guide

This document describes how to run and write tests for the Transaction Monitor Bot.

## Test Structure

The test suite is organized as follows:

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and shared fixtures
├── test_monitors.py         # Unit tests for network monitors
├── test_telegram_bot.py     # Unit tests for Telegram bot
└── test_integration.py      # Integration tests for complete system
```

## Running Tests

### Run All Tests

```bash
# Using the test runner script
chmod +x run_tests.sh
./run_tests.sh

# Or directly with pytest
pytest
```

### Run Specific Test Files

```bash
# Test only monitors
pytest tests/test_monitors.py

# Test only Telegram bot
pytest tests/test_telegram_bot.py

# Test only integration
pytest tests/test_integration.py
```

### Run Specific Test Classes or Functions

```bash
# Run specific test class
pytest tests/test_monitors.py::TestTONMonitor

# Run specific test function
pytest tests/test_monitors.py::TestTONMonitor::test_get_price_usd
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage Report

```bash
# Terminal output with coverage
pytest --cov=. --cov-report=term-missing

# HTML coverage report
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in your browser
```

## Test Categories

### Unit Tests

Unit tests test individual components in isolation:

- **Monitor Tests** (`test_monitors.py`):
  - Price fetching and caching
  - Transaction parsing
  - Duplicate detection
  - Network-specific logic

- **Telegram Bot Tests** (`test_telegram_bot.py`):
  - Message formatting
  - Address/hash shortening
  - Alert sending
  - Error handling

### Integration Tests

Integration tests verify that components work together (`test_integration.py`):

- Bot initialization with all monitors
- Complete transaction detection flow
- Error handling across components
- Configuration loading

## Test Fixtures

Common test fixtures are defined in `conftest.py`:

- `mock_env`: Mock environment variables
- `mock_telegram_bot`: Mock Telegram bot instance
- `sample_transaction_data`: Sample transaction data for all networks
- `mock_price_api_response`: Mock price API responses

## Writing New Tests

### Example: Testing a New Monitor

```python
import pytest
from aioresponses import aioresponses
from monitors.your_monitor import YourMonitor

class TestYourMonitor:
    @pytest.mark.asyncio
    async def test_get_price_usd(self):
        monitor = YourMonitor(min_usd=100000, rpc_url='https://test.com')

        with aioresponses() as m:
            m.get(
                'https://api.coingecko.com/api/v3/simple/price',
                payload={'your_token': {'usd': 1.5}}
            )

            price = await monitor.get_current_price_usd()
            assert price == 1.5
```

### Example: Testing Async Functions

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected_value
```

### Example: Mocking HTTP Requests

```python
from aioresponses import aioresponses

@pytest.mark.asyncio
async def test_api_call():
    with aioresponses() as m:
        m.get('https://api.example.com/data', payload={'value': 123})

        result = await fetch_from_api()
        assert result['value'] == 123
```

## Continuous Integration

To run tests in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Install dependencies
  run: pip install -r requirements.txt

- name: Run tests
  run: pytest --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Test Coverage Goals

Current test coverage includes:

- ✅ Monitor base class functionality
- ✅ All network monitors (TON, Everscale, Venom, Humanode)
- ✅ Price fetching and caching
- ✅ Transaction parsing and filtering
- ✅ Duplicate detection
- ✅ Telegram message formatting
- ✅ Telegram notifications
- ✅ Bot initialization
- ✅ Error handling
- ✅ Configuration loading

Aim for >80% code coverage for production readiness.

## Manual Testing

### Testing with Real APIs (Development)

1. Create a test environment file:
```bash
cp .env.example .env.test
```

2. Set lower threshold for testing:
```env
MIN_TRANSACTION_USD=1000  # Lower threshold to catch more transactions
POLL_INTERVAL_SECONDS=30  # Faster polling for testing
```

3. Run the bot:
```bash
python main.py
```

### Testing Telegram Notifications

1. Send a test notification:
```python
import asyncio
from telegram_bot import TelegramNotifier
from monitors.base_monitor import Transaction

async def test_notification():
    notifier = TelegramNotifier('YOUR_TOKEN', 'YOUR_CHAT_ID')

    tx = Transaction(
        network='TON',
        tx_hash='test_hash_123',
        amount_usd=150000.0,
        sender='test_sender',
        receiver='test_receiver',
        timestamp=1705000000,
        amount_native=60000.0
    )

    await notifier.send_transaction_alert(tx)

asyncio.run(test_notification())
```

## Debugging Tests

### Run with Debug Output

```bash
pytest -v -s  # -s shows print statements
```

### Run with Python Debugger

```python
def test_something():
    import pdb; pdb.set_trace()  # Debugger will stop here
    result = some_function()
    assert result == expected
```

### Check Test Logs

```bash
# Run with detailed logging
pytest --log-cli-level=DEBUG
```

## Troubleshooting

### Tests Failing Due to Network Issues

If tests fail due to network timeouts:
- Check your internet connection
- The tests use mocked APIs by default, but some may require network access
- Increase timeout values in test configuration

### Import Errors

If you see import errors:
```bash
# Ensure you're in the project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Async Test Issues

If async tests hang or fail:
- Ensure you have `pytest-asyncio` installed
- Check that `asyncio_mode = auto` is in `pytest.ini`
- Use `@pytest.mark.asyncio` decorator on async test functions

## Performance Testing

To test bot performance under load:

```python
import pytest
import asyncio
from monitors.ton_monitor import TONMonitor

@pytest.mark.asyncio
async def test_concurrent_requests():
    monitor = TONMonitor(min_usd=100000, api_key='test')

    # Simulate 10 concurrent requests
    tasks = [monitor.get_latest_transactions() for _ in range(10)]
    results = await asyncio.gather(*tasks)

    assert len(results) == 10
```

## Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Use Fixtures**: Reuse common setup with pytest fixtures
3. **Mock External APIs**: Don't rely on real API calls in tests
4. **Test Edge Cases**: Include tests for error conditions
5. **Keep Tests Fast**: Mock slow operations
6. **Clear Test Names**: Use descriptive test function names
7. **Document Complex Tests**: Add comments explaining test logic

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [aioresponses](https://github.com/pnuckowski/aioresponses)
- [Coverage.py](https://coverage.readthedocs.io/)
