#!/bin/bash
# Test runner script

echo "================================"
echo "Running Transaction Monitor Tests"
echo "================================"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "pytest not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Run all tests with coverage
echo "Running all tests..."
pytest -v --cov=. --cov-report=html --cov-report=term-missing

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✅ All tests passed!"
    echo "================================"
    echo ""
    echo "Coverage report available at: htmlcov/index.html"
else
    echo ""
    echo "================================"
    echo "❌ Some tests failed!"
    echo "================================"
    exit 1
fi
