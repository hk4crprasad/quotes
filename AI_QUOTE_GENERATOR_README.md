# 🤖 AI-Powered Gen Z Quote Generator with FastAPI-MCP

An intelligent viral motivational quote generator that uses **LangChain + OpenAI GPT-4.1-mini** to create authentic, shareable Gen Z quotes. Features **FastAPI-MCP integration** for AI agents, **Server-Sent Events (SSE) streaming**, and **in-memory caching**.

## ✨ Features

- 🧠 **AI-Powered Generation**: Uses LangChain + OpenAI GPT-4.1-mini for creative, unique quotes
- 🔄 **MCP Compatible**: Automatic Model Context Protocol server for AI agents
- 📡 **Real-time Streaming**: Server-Sent Events for live quote generation
- 🎯 **Theme-based**: Relationships, self-worth, boundaries, money, hard-truths, and more
- 👥 **Audience Targeting**: Gen Z, millennials, empaths, introverts, overthinkers
- 💾 **In-Memory Caching**: Fast retrieval without database overhead
- 🔍 **Search & Filter**: Find quotes by content, theme, and engagement
- 📈 **Engagement Metrics**: Realistic likes, shares, and scoring

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
# Using the startup script (recommended)
./start_quote_generator.sh

# Or directly with Python
python3 test.py --host 0.0.0.0 --port 8000
```

### 3. Test AI Generation

```bash
# Test the AI quote generator
python3 test_ai_quote.py
```

## 🔗 API Endpoints

### Core Generation
- **POST /generate** - Generate AI-powered viral quotes
- **GET /stream** - Stream multiple quotes with SSE
- **GET /search** - Search cached quotes with text matching
- **GET /trending** - Get highest engagement cached quotes
- **GET /themes/{theme}** - Get quotes by specific theme

### MCP Integration
- **GET /mcp** - Model Context Protocol endpoint for AI agents
- **GET /** - Server information and capabilities

## 🎯 Usage Examples

### Generate a Single Quote

```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "theme": "relationships",
       "target_audience": "empaths",
       "format_preference": "truth-bomb"
     }'
```

### Stream Multiple Quotes

```bash
curl "http://localhost:8000/stream?count=5&theme=self-worth"
```

### Search Cached Quotes

```bash
curl "http://localhost:8000/search?query=love%20relationships&theme=relationships"
```

## 🤖 AI Configuration

The system uses **LangChain** with **OpenAI GPT-4.1-mini** via Tecosys LiteLLM:

```python
llm = ChatOpenAI(
    openai_api_base="https://litellm.tecosys.ai/",
    openai_api_key="sk-LLPrAbLPEaAJIduZjOyRzw",
    model="gpt-4.1-mini",
    temperature=0.8  # High creativity for unique quotes
)
```

## 🛠️ MCP Integration for Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "ai-quote-generator": {
      "command": "mcp-proxy",
      "args": ["http://localhost:8000/mcp"]
    }
  }
}
```

## 🎨 Supported Themes

- **relationships** - Dating, friendships, family dynamics
- **self-worth** - Confidence, boundaries, self-respect  
- **money** - Financial independence, success mindset
- **boundaries** - Healthy limits, saying no, protecting peace
- **hard-truths** - Uncomfortable realities, wisdom
- **mixed** - Random theme selection

## 👥 Target Audiences

- **gen-z** - Digital natives (18-26)
- **millennials** - Older millennials (27-40) 
- **empaths** - Highly sensitive, caring individuals
- **introverts** - Quiet, introspective personalities
- **overthinkers** - Analytical, anxious minds

## 📊 Engagement Simulation

The system generates realistic engagement metrics:

- **Likes**: 5,000 - 50,000 range
- **Shares**: 5-15% of likes (viral sharing rate)
- **Engagement Score**: 0.75 - 0.98 (algorithmic ranking)
- **Timestamps**: ISO format with creation time

## 🧪 Testing

```bash
# Test AI generation functionality
python3 test_ai_quote.py

# Test server endpoints
curl http://localhost:8000/
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d '{}'
```

## 🔧 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │────│  LangChain LLM   │────│  OpenAI GPT-4   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                                               
         ├── MCP Server (AI Agents)                     
         ├── SSE Streaming (Real-time)                  
         ├── REST API (Standard)                        
         └── In-Memory Cache (Fast Storage)             
```

## 📝 Key Files

- **test.py** - Main FastAPI application with AI integration
- **test_ai_quote.py** - Test script for AI functionality  
- **start_quote_generator.sh** - Startup script
- **requirements.txt** - Python dependencies

## 🌟 AI Quote Examples

**Input**: `{"theme": "relationships", "target_audience": "empaths"}`

**Output**:
```json
{
  "title": "Definition of real love",
  "content": "Real love is choosing the same person on your worst days, not just when the vibe's right.",
  "theme": "relationships",
  "engagement_score": 0.83,
  "likes": 24500,
  "shares": 2940
}
```

## 🔄 Storage

- **Type**: In-memory cache (no database)
- **Persistence**: Session-based (resets on restart)
- **Performance**: Ultra-fast retrieval
- **Scalability**: Suitable for development and testing

## 🚦 Status

✅ **Fully Functional**
- AI quote generation with LangChain
- FastAPI-MCP integration
- SSE streaming capabilities
- Search and filtering
- Engagement simulation

## 💡 Future Enhancements

- Persistent storage (Redis/PostgreSQL)
- User authentication and personal libraries
- Advanced AI fine-tuning
- Social media integration
- Analytics dashboard

---

**🎯 Ready to generate viral quotes with AI?** 
Start the server and let the creativity flow! 🚀
