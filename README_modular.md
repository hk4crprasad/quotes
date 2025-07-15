# Gen Z Quote Generator - Modular Architecture

A clean, modular AI-powered viral quote generator that creates authentic Gen Z motivational quotes using LangChain and OpenAI.

## 🏗️ Architecture

The application follows a clean modular architecture:

```
quotes/
├── main.py              # FastAPI application and entry point
├── models.py            # Data models (Quote, QuoteRequest, QuoteResponse)
├── config.py            # Configuration, constants, and prompts
├── quote_generator.py   # AI quote generation service
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
└── .env.example         # Environment variables template
```

## 🚀 Features

- **AI-Powered**: Uses GPT-4.1-mini via LangChain for authentic quote generation
- **Modular Design**: Clean separation of concerns
- **Viral Optimization**: Designed for maximum shareability
- **MCP Compatible**: Works with AI agents via Model Context Protocol
- **Stateless**: No database required - pure generation service
- **Variety**: Dynamic title patterns and content themes for uniqueness

## 📦 Installation

1. **Clone and setup**:
```bash
cd quotes
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

3. **Run the server**:
```bash
python main.py --host localhost --port 8091
```

## 🎯 Usage

### Generate a Quote

```bash
curl -X POST "http://localhost:8091/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "theme": "relationships",
       "target_audience": "gen-z",
       "format_preference": "Maturity is when"
     }'
```

### Response Format

```json
{
  "title": "Maturity is when",
  "content": "you stop asking people why they don't call or text you anymore. You just notice the change and accept it, no drama, no fights. You just walk away with a smile.",
  "theme": "relationships",
  "target_audience": "gen-z",
  "created_at": "2025-07-15T07:10:33.705205"
}
```

## 🛠️ API Endpoints

- **POST /generate** - Generate a viral quote
- **GET /** - Server information
- **GET /mcp** - MCP endpoint for AI agents
- **GET /docs** - Interactive API documentation

## 🎨 Themes

- `relationships` - Love, dating, boundaries
- `self-worth` - Self-esteem, validation, confidence  
- `money` - Financial independence, wealth building
- `boundaries` - Personal limits, saying no
- `growth` - Personal development, healing
- `mixed` - Random theme selection

## 👥 Target Audiences

- `gen-z` - Gen Z language and concerns
- `millennials` - Millennial perspectives
- `empaths` - Highly sensitive individuals
- `introverts` - Introvert-specific content
- `overthinkers` - For analytical minds

## 🔧 MCP Integration

For Claude Desktop, add to your config:

```json
{
  "mcpServers": {
    "ai-quote-generator": {
      "command": "mcp-proxy", 
      "args": ["http://localhost:8091/mcp"]
    }
  }
}
```

## 📁 Module Details

### `models.py`
- Data classes and Pydantic models
- Request/response schemas
- Type definitions

### `config.py`
- Environment configuration
- Title patterns and content themes
- AI prompts and constants

### `quote_generator.py`
- Core AI generation logic
- LangChain integration
- Quote creation service

### `main.py`
- FastAPI application
- API endpoints
- MCP integration
- Server startup

## 🌟 Key Features

- **Random Variety**: Each generation uses different title patterns and content
- **Viral Optimization**: Prompts designed for maximum shareability
- **Clean Architecture**: Easy to extend and maintain
- **No Database**: Stateless service, no persistence needed
- **AI-Powered**: GPT-4.1-mini for authentic, creative content

## 🔄 Development

The modular design makes it easy to:
- Add new themes in `config.py`
- Modify AI prompts in `config.py`
- Extend the API in `main.py`
- Enhance generation logic in `quote_generator.py`

## 📊 Example Output Variations

The system generates varied, authentic quotes like:

- **"Maturity is when"** - "you stop chasing people who treat you like an option."
- **"Real talk:"** - "Your energy is your most valuable currency. Spend it wisely."
- **"Plot twist:"** - "The person who's meant for you will never make you question your worth."
