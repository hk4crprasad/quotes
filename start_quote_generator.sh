#!/bin/bash

# AI-Powered Gen Z Quote Generator Startup Script

echo "🚀 Starting AI-Powered Gen Z Quote Generator..."

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import fastapi, langchain_openai, fastapi_mcp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip3 install -r requirements.txt
fi

# Set default port if not provided
PORT=${1:-8000}

echo "🎯 Starting server on port $PORT..."
echo "📍 API: http://localhost:$PORT"
echo "🤖 MCP: http://localhost:$PORT/mcp"
echo "📚 Docs: http://localhost:$PORT/docs"
echo ""

# Start the server
python3 test.py --host 0.0.0.0 --port $PORT --reload
