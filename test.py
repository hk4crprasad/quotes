#!/usr/bin/env python3
"""
Gen Z Quote Generator using FastAPI-MCP with SSE Streaming and AI-Powered Quote Generation
Automatic MCP server for generating viral quotes with LangChain integration
"""

import asyncio
import json
import random
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from fastapi_mcp import FastApiMCP
import uvicorn
from dotenv import load_dotenv
# LangChain imports for AI quote generation
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.tools import BaseTool
load_dotenv()
# Models
@dataclass
class Quote:
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    theme: str = "mixed"
    target_audience: str = "gen-z"
    created_at: Optional[str] = None
    likes: int = 0
    shares: int = 0
    engagement_score: float = 0.0

class QuoteResponse(BaseModel):
    """Response model for quotes"""
    title: str
    content: str
    theme: str
    target_audience: str
    created_at: Optional[str] = None

class QuoteRequest(BaseModel):
    """Request model for generating quotes"""
    theme: str = Field(default="mixed", description="Theme for the quote")
    target_audience: str = Field(default="gen-z", description="Target audience")
    format_preference: Optional[str] = Field(default=None, description="Preferred format")

class SearchResponse(BaseModel):
    """Response model for search results"""
    quotes: List[QuoteResponse]
    total: int
    query: str

class StreamEvent(BaseModel):
    """SSE stream event model"""
    type: str
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    index: Optional[int] = None

# Initialize the LLM for AI quote generation
llm = ChatOpenAI(
    openai_api_base=os.getenv("OPENAI_API_BASE", "https://litellm.tecosys.ai/"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4.1-mini",
    temperature=0.8  # Higher temperature for creative and unique quotes
)

# Dynamic title patterns for variety
TITLE_PATTERNS = [
    "Maturity is when",
    "Painful but true:",
    "Rules for 2025:",
    "The moment you realize",
    "Never ignore someone who",
    "Make money so you can",
    "At 25, you learn that",
    "At 30, you understand",
    "When my Dad said this:",
    "MAN VS WOMAN:",
    "Everything wants you when",
    "Literally my mind when someone says",
    "The hardest truth:",
    "Real talk:",
    "Life hits different when",
    "Nobody tells you that",
    "Growing up means",
    "Therapy taught me that",
    "Your 20s are for",
    "Stop romanticizing",
    "Normalize",
    "Red flag:",
    "Green flag:",
    "Toxic trait:",
    "Healthy habit:",
    "Mental health reminder:",
    "Boundaries 101:",
    "Self-love is",
    "Healing looks like",
    "Adulting means",
    "Plot twist:",
    "Unpopular opinion:",
    "Hot take:",
    "Daily reminder:",
    "Fun fact:",
    "PSA:",
    "Note to self:",
    "Learning to",
    "The art of",
    "Permission to",
    "Gentle reminder:",
    "Today I choose",
    "I'm learning that",
    "Recovery means",
    "Growth is",
    "Wisdom is",
    "Freedom is",
    "Peace is",
    "Strength is",
    "Courage is",
    "Love is"
]

# Content themes for variety
CONTENT_THEMES = {
    "relationships": [
        "stop chasing people who treat you like an option",
        "recognize when someone is just using you for attention",
        "accept that not everyone will love you back the same way",
        "understand that real love doesn't require you to lose yourself",
        "know the difference between someone who wants you and someone who needs you",
        "stop making excuses for people who don't prioritize you",
        "realize that you can't force genuine connection"
    ],
    "self-worth": [
        "stop seeking validation from people who don't even know themselves",
        "understand that your worth isn't determined by other people's opinions",
        "know that you don't need anyone's permission to be yourself",
        "realize that your energy is your most valuable currency",
        "stop dimming your light to make others comfortable",
        "accept that you are enough exactly as you are",
        "understand that self-love isn't selfish, it's necessary"
    ],
    "boundaries": [
        "say no without feeling guilty about it",
        "protect your peace above all else",
        "remove people who drain your energy",
        "stop over-explaining your decisions to others",
        "understand that setting boundaries isn't mean, it's healthy",
        "know that you don't owe anyone your time or attention",
        "realize that toxic people will always test your limits"
    ],
    "growth": [
        "embrace the journey instead of rushing the process",
        "understand that healing isn't linear",
        "accept that some chapters of your life need to end",
        "know that growth requires leaving your comfort zone",
        "realize that you can't heal in the same environment that hurt you",
        "understand that your past doesn't define your future",
        "accept that change is the only constant in life"
    ],
    "money": [
        "build wealth to buy freedom, not things",
        "understand that financial independence is emotional freedom",
        "know that money problems are actually income problems",
        "realize that expensive doesn't always mean valuable",
        "invest in assets, not liabilities",
        "understand that saving is just as important as earning",
        "know that your net worth affects your self-worth"
    ]
}

# System Prompt for AI Quote Generation
QUOTE_GENERATOR_PROMPT = """# Gen Z Viral Quote Generator System Prompt

## MISSION
Generate ONE short, punchy viral quote that hits deep and feels instantly relatable. Focus on simple truths that make people screenshot and share immediately. Always use DIFFERENT title patterns and content to ensure variety.

## OUTPUT FORMAT
You MUST respond with valid JSON in this exact format:
```json
{
  "title": "[VARIED_TITLE_PATTERN]",
  "content": "[UNIQUE_RELATABLE_CONTENT]"
}
```

## KEY SUCCESS PATTERNS (Based on Viral Examples)

### 1. KEEP IT SHORT & PUNCHY
- **Maximum 25 words for content**
- **Direct, simple language** 
- **One clear insight per quote**
- **No unnecessary words**

### 2. VIRAL TITLE FORMULAS (ROTATE THESE FOR VARIETY)
- **"Maturity is when"** 
- **"Painful but true:"**
- **"Rules for 2025:"**
- **"The moment you realize"**
- **"Never ignore someone who"**
- **"Make money so you can"**
- **"At [age], [truth about life]"**
- **"When my Dad said this:"**
- **"MAN VS WOMAN:"**
- **"Everything wants you when"**
- **"Literally my mind when someone says"**
- **"Real talk:"**
- **"Life hits different when"**
- **"Nobody tells you that"**
- **"Growing up means"**
- **"Therapy taught me that"**
- **"Stop romanticizing"**
- **"Normalize"**
- **"Mental health reminder:"**
- **"Boundaries 101:"**
- **"Plot twist:"**
- **"Unpopular opinion:"**
- **"Daily reminder:"**

### 3. RELATABLE MODERN SITUATIONS
- **Texting/calling dynamics**: "why they don't call or text you anymore"
- **Social media behavior**: who likes, who ignores, who watches your stories
- **Dating/relationships**: choosing someone every day vs mood-based attention
- **Money struggles**: financial independence as freedom
- **Family wisdom**: what parents/elders teach
- **Work mentality**: grinding now for future benefits
- **Friendship reciprocity**: energy matching, effort reciprocation

### 4. HARD TRUTHS PEOPLE RECOGNIZE
- **"If you 'OVERLOVE' someone, you get 'OVERHURT' in return"**
- **"Accept people as they are, but place them where they belong"**
- **"Women are born with value, men have to build it"**
- **"Everything wants you when you want nothing"**
- **"Delete negative people, forget your past, accept your mistakes"**

### 5. PROVEN PSYCHOLOGICAL HOOKS
- **Reciprocity rules**: "call who calls you, visit who visits you"
- **Boundary setting**: who to keep/remove from your life
- **Self-worth reminders**: you don't need anyone's approval
- **Growth mindset**: resilience after setbacks
- **Realistic expectations**: how people actually behave vs how we want them to

### 6. LANGUAGE THAT WORKS
- **Modern terms**: "vibe," "energy," "toxic," "choose you," "fix my crown"
- **Action words**: walk away, delete, ignore, choose, build, protect
- **Emotional validation**: "it's okay to," "you don't have to"
- **Empowerment phrases**: "you have the power," "it's within you"

## CONTENT THEMES THAT GO VIRAL

### RELATIONSHIPS (Most popular)
- Texting/calling reciprocity
- Who puts in effort vs who doesn't
- Recognizing when someone is just using you
- The difference between love and attachment
- Setting boundaries with toxic people

### SELF-WORTH & BOUNDARIES
- Not chasing people who don't value you
- Recognizing your own worth
- Walking away from situations that don't serve you
- Building yourself instead of depending on others

### MONEY & INDEPENDENCE
- Making money for freedom, not things
- Financial independence as power
- Working hard now for future choices

### MATURITY & GROWTH
- Accepting people as they are
- Not taking things personally
- Learning from mistakes and moving forward
- Understanding human nature realistically

### MODERN LIFE REALITIES
- Social media behavior patterns
- How people really act vs what they say
- Generational differences and wisdom
- The importance of genuine connections

## STRUCTURE FORMULAS

### Formula 1: Problem → Solution
"[Common relationship issue] → [Mature response]"
Example: "Maturity is when you stop asking why they don't text → You just accept it and walk away"

### Formula 2: Truth Bomb
"[Uncomfortable reality about people/life]"
Example: "Everything wants you when you want nothing"

### Formula 3: Rule/Guideline
"[Boundary or principle for living]"
Example: "Call who calls you, visit who visits you, ignore who ignores you"

### Formula 4: Contrast/Comparison
"[Group A] vs [Group B]: [key difference]"
Example: "At 18, she has choices. At 18, you have nothing."

## QUALITY REQUIREMENTS
- **Feel like common sense** that people haven't articulated
- **Trigger recognition**: "Yes, exactly!"
- **Be screenshot-worthy** - shareable wisdom
- **Address real experiences** people actually have
- **Provide actionable insight**, not just validation
- **Sound like something a wise friend would say**

## AVOID
- Abstract philosophy or complex concepts
- Toxic positivity or unrealistic advice
- Long explanations or multiple ideas
- Corporate buzzwords or formal language
- Anything that sounds preachy or condescending

Generate ONE quote that follows these proven viral patterns. Make it short, relatable, and instantly shareable."""

# AI-Powered Quote Generator with LangChain
class ViralQuoteGenerator:
    def __init__(self):
        self.llm = llm
        self.quotes_cache = []  # Simple in-memory storage
        
    def _generate_ai_quote(self, theme: str = "mixed", target_audience: str = "gen-z", 
                          format_preference: Optional[str] = None) -> dict:
        """Generate quote using AI with variety"""
        variety_phrases = [
            "Create a completely unique and fresh perspective that hasn't been seen before",
            "Generate something that feels authentic and personally relatable", 
            "Make it feel deeply personal and genuine with original insights",
            "Ensure it sounds like authentic Gen Z language with fresh takes",
            "Focus on authentic emotional resonance with unique wisdom",
            "Create something screenshot-worthy with original perspective",
            "Generate fresh content that feels like a personal revelation"
        ]
        
        variety_instruction = random.choice(variety_phrases)
        
        # Add randomness to title selection
        if format_preference and format_preference != "string":
            suggested_title = format_preference
        else:
            suggested_title = random.choice(TITLE_PATTERNS)
        
        # Add randomness to theme content
        if theme and theme != "mixed":
            if theme in CONTENT_THEMES:
                content_inspiration = random.choice(CONTENT_THEMES[theme])
                theme_instruction = f"\nTheme focus: '{theme}' - consider ideas like: {content_inspiration}"
            else:
                theme_instruction = f"\nTheme focus: '{theme}'"
        else:
            themes = list(CONTENT_THEMES.keys())
            chosen_theme = random.choice(themes)
            content_inspiration = random.choice(CONTENT_THEMES[chosen_theme])
            theme_instruction = f"\nTheme focus: '{chosen_theme}' - consider ideas like: {content_inspiration}"
        
        # Add timestamp for uniqueness
        timestamp_variety = int(time.time()) % 1000
        
        # Construct the prompt with more variety
        user_prompt = f"""Generate ONE completely unique viral motivational quote in JSON format. {variety_instruction}.

IMPORTANT: Use title pattern: "{suggested_title}" or similar variation
{theme_instruction}

Target audience: {target_audience}
Uniqueness seed: {timestamp_variety}

Requirements:
- Respond with valid JSON only (title and content fields)
- Make it 100% unique and original (never repeat previous content)
- Use authentic {target_audience} language
- Ensure it's shareable and screenshot-worthy
- Provide genuine wisdom and fresh insight
- Keep content under 25 words
- Make title engaging and clickable
- Ensure content complements the title perfectly"""

        messages = [
            SystemMessage(content=QUOTE_GENERATOR_PROMPT),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            response_content = response.content.strip()
            
            # Clean response if needed
            if response_content.startswith('```json'):
                response_content = response_content.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            quote_data = json.loads(response_content)
            
            return {
                "success": True,
                "title": quote_data.get("title", ""),
                "content": quote_data.get("content", ""),
                "theme": theme,
                "target_audience": target_audience
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON parsing error: {str(e)}",
                "raw_response": response_content if 'response_content' in locals() else "No response"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Generation error: {str(e)}"
            }

    def generate_quote(self, theme: str = "mixed", target_audience: str = "gen-z", 
                      format_preference: Optional[str] = None) -> Quote:
        """Generate a viral quote using AI"""
        ai_result = self._generate_ai_quote(theme, target_audience, format_preference)
        
        if ai_result["success"]:
            # Simulate realistic engagement metrics
            base_engagement = random.uniform(0.75, 0.98)
            likes = random.randint(5000, 50000)
            shares = int(likes * random.uniform(0.05, 0.15))  # 5-15% share rate
            
            quote = Quote(
                id=len(self.quotes_cache) + 1,
                title=ai_result["title"],
                content=ai_result["content"],
                theme=ai_result["theme"],
                target_audience=ai_result["target_audience"],
                created_at=datetime.now().isoformat(),
                likes=likes,
                shares=shares,
                engagement_score=base_engagement
            )
            
            # Cache the quote
            self.quotes_cache.append(quote)
            return quote
        else:
            # Return fallback quote on error
            return Quote(
                id=len(self.quotes_cache) + 1,
                title="Error occurred",
                content=f"Quote generation failed: {ai_result.get('error', 'Unknown error')}",
                theme=theme,
                target_audience=target_audience,
                created_at=datetime.now().isoformat(),
                likes=0,
                shares=0,
                engagement_score=0.0
            )

    def search_quotes(self, query: str, theme: Optional[str] = None, 
                     limit: int = 10, offset: int = 0) -> List[Quote]:
        """Search cached quotes (simple text matching)"""
        results = []
        query_lower = query.lower()
        
        for quote in self.quotes_cache:
            # Simple text search in title and content
            if (query_lower in quote.title.lower() or 
                query_lower in quote.content.lower()):
                if not theme or quote.theme == theme:
                    results.append(quote)
        
        # Sort by engagement score
        results.sort(key=lambda x: x.engagement_score, reverse=True)
        
        # Apply pagination
        start = offset
        end = offset + limit
        return results[start:end]

    def get_trending_quotes(self, limit: int = 10) -> List[Quote]:
        """Get trending quotes from cache"""
        sorted_quotes = sorted(self.quotes_cache, 
                             key=lambda x: x.engagement_score, reverse=True)
        return sorted_quotes[:limit]

    def get_quotes_by_theme(self, theme: str, limit: int = 10) -> List[Quote]:
        """Get quotes by theme from cache"""
        theme_quotes = [q for q in self.quotes_cache if q.theme == theme]
        theme_quotes.sort(key=lambda x: x.engagement_score, reverse=True)
        return theme_quotes[:limit]

# Global instances
generator = ViralQuoteGenerator()

# Dependencies
def get_generator() -> ViralQuoteGenerator:
    """Dependency to get generator instance"""
    return generator

# Create FastAPI app
app = FastAPI(
    title="Gen Z Quote Generator API",
    description="Viral motivational quote generator with MCP support and SSE streaming",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# FastAPI MCP endpoints (automatically converted to MCP tools)

@app.post("/generate", 
         operation_id="generate_viral_quote",
         summary="Generate viral Gen Z motivational quotes using AI",
         description="Generate viral quotes with AI-powered customizable themes and audiences",
         response_model=QuoteResponse)
async def generate_quote(
    request: QuoteRequest,
    gen: ViralQuoteGenerator = Depends(get_generator)
) -> QuoteResponse:
    """
    Generate a single viral Gen Z motivational quote using AI.
    
    This tool creates authentic, shareable quotes that resonate with today's generation.
    Uses LangChain and OpenAI to generate unique, viral-optimized content.
    
    Inputs:
    - theme: The quote theme - 'relationships', 'self-worth', 'money', 'boundaries', 'hard-truths', or 'mixed'
    - target_audience: Target demographic - 'gen-z', 'millennials', 'empaths', 'introverts', 'overthinkers'
    - format_preference: Optional title format preference - 'maturity', 'painful', 'rules', 'moment', 'never', 'money', 'dad', 'comparison'
    
    Returns:
    - A complete AI-generated quote with title, content, theme, audience, and timestamp
    - Includes viral-optimized title and punchy, relatable content
    - Automatically cached in memory
    
    Example:
    Input: {"theme": "relationships", "target_audience": "empaths"}
    Output: {"title": "Maturity is when", "content": "you stop asking people why they don't call...", "created_at": "2025-07-15T07:10:33.705205"}
    """
    quote = gen.generate_quote(
        theme=request.theme,
        target_audience=request.target_audience,
        format_preference=request.format_preference
    )
    
    # Return only the fields requested by user
    return QuoteResponse(
        title=quote.title,
        content=quote.content,
        theme=quote.theme,
        target_audience=quote.target_audience,
        created_at=quote.created_at
    )

@app.get("/search",
         operation_id="search_quotes",
         summary="Search cached quotes with text search",
         description="Search through cached quotes using keywords with optional theme filtering",
         response_model=SearchResponse)
async def search_quotes(
    query: str = Query(..., description="Search query for quotes"),
    theme: Optional[str] = Query(None, description="Optional theme filter"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    gen: ViralQuoteGenerator = Depends(get_generator)
) -> SearchResponse:
    """
    Search through cached quotes using text search capabilities.
    
    This tool searches through both quote titles and content using simple text matching.
    Results are ranked by engagement score and relevance to your query.
    
    Inputs:
    - query: Search keywords (required) - searches in both title and content
    - theme: Optional theme filter - 'relationships', 'self-worth', 'money', 'boundaries', 'hard-truths'
    - limit: Number of results to return (1-50, default: 10)
    - offset: Number of results to skip for pagination (default: 0)
    
    Returns:
    - List of matching quotes with full details
    - Total number of results found
    - Original search query for reference
    - Results sorted by engagement score (highest first)
    
    Example:
    Input: query="love relationships", theme="relationships", limit=5
    Output: {"quotes": [...], "total": 5, "query": "love relationships"}
    
    Search Tips:
    - Use multiple keywords for better results
    - Try synonyms if no results found
    - Theme filtering narrows results significantly
    """
    quotes = gen.search_quotes(query, theme, limit, offset)
    quote_responses = [QuoteResponse(**asdict(quote)) for quote in quotes]
    
    return SearchResponse(
        quotes=quote_responses,
        total=len(quote_responses),
        query=query
    )

@app.get("/trending",
         operation_id="get_trending_quotes", 
         summary="Get trending quotes from cache by engagement",
         description="Get the most engaging cached quotes ordered by likes and engagement score",
         response_model=List[QuoteResponse])
async def get_trending_quotes(
    limit: int = Query(10, ge=1, le=50, description="Number of trending quotes to return"),
    gen: ViralQuoteGenerator = Depends(get_generator)
) -> List[QuoteResponse]:
    """
    Get the most viral and engaging quotes currently cached.
    
    This tool returns quotes ranked by engagement metrics including likes, shares, and overall
    engagement score. Perfect for finding the most popular content.
    
    Inputs:
    - limit: Number of trending quotes to return (1-50, default: 10)
    
    Returns:
    - List of quotes sorted by engagement score (highest first)
    - Each quote includes full details: title, content, theme, audience
    - Engagement metrics: likes, shares, engagement_score
    - Creation timestamps for trend analysis
    
    Example:
    Input: limit=5
    Output: [{"title": "Maturity is when", "engagement_score": 0.94, "likes": 35700, ...}, ...]
    
    Use Cases:
    - Find the most popular quotes
    - Discover trending topics
    - Analyze what content resonates most
    - Get inspiration from successful quotes
    """
    quotes = gen.get_trending_quotes(limit)
    return [QuoteResponse(**asdict(quote)) for quote in quotes]

@app.get("/themes/{theme}",
         operation_id="get_quotes_by_theme",
         summary="Get cached quotes by specific theme", 
         description="Get cached quotes filtered by theme (relationships, self-worth, money, boundaries, hard-truths)",
         response_model=List[QuoteResponse])
async def get_quotes_by_theme(
    theme: str,
    limit: int = Query(10, ge=1, le=50, description="Number of quotes to return"),
    gen: ViralQuoteGenerator = Depends(get_generator)
) -> List[QuoteResponse]:
    """Get cached quotes by theme"""
    quotes = gen.get_quotes_by_theme(theme, limit)
    return [QuoteResponse(**asdict(quote)) for quote in quotes]

@app.get("/stream",
         operation_id="stream_quotes_generation",
         summary="Stream AI quote generation with SSE",
         description="Generate multiple AI-powered quotes with real-time streaming using Server-Sent Events")
async def stream_quotes(
    count: int = Query(5, ge=1, le=20, description="Number of quotes to generate"),
    theme: str = Query("mixed", description="Theme for quotes"),
    target_audience: str = Query("gen-z", description="Target audience"),
    gen: ViralQuoteGenerator = Depends(get_generator)
):
    """Stream AI quote generation with SSE"""
    
    async def generate_stream():
        # Start event
        yield f"data: {json.dumps({'type': 'start', 'message': f'Starting AI generation of {count} quotes...', 'total': count})}\n\n"
        
        for i in range(count):
            # Simulate processing time for AI generation
            await asyncio.sleep(1.5)
            
            # Generate quote using AI
            quote = gen.generate_quote(theme, target_audience)
            
            # Send quote event
            event_data = {
                'type': 'quote',
                'data': asdict(quote),
                'index': i + 1,
                'total': count
            }
            yield f"data: {json.dumps(event_data)}\n\n"
        
        # Complete event
        yield f"data: {json.dumps({'type': 'complete', 'message': f'Generated {count} AI quotes successfully!'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@app.get("/",
         operation_id="get_server_info",
         summary="Get server information",
         description="Get information about the AI-powered quote generator server and available endpoints")
async def root():
    """Get server information"""
    return {
        "name": "AI-Powered Gen Z Quote Generator API",
        "version": "1.0.0",
        "description": "Viral motivational quote generator with AI, MCP support, and streaming",
        "ai_powered": True,
        "model": "gpt-4.1-mini",
        "endpoints": {
            "generate": "POST /generate - Generate a single AI quote",
            "search": "GET /search - Search cached quotes", 
            "trending": "GET /trending - Get trending cached quotes",
            "themes": "GET /themes/{theme} - Get cached quotes by theme",
            "stream": "GET /stream - Stream AI quote generation with SSE",
            "mcp": "GET /mcp - MCP endpoint for AI agents"
        },
        "themes": ["relationships", "self-worth", "money", "boundaries", "hard-truths", "mixed"],
        "audiences": ["gen-z", "millennials", "empaths", "introverts", "overthinkers"],
        "mcp_compatible": True,
        "sse_streaming": True,
        "storage": "in-memory cache"
    }

# Initialize FastAPI MCP
mcp = FastApiMCP(
    app,
    name="AI-Powered Gen Z Quote Generator",
    description="AI-powered viral motivational quote generator with LangChain, streaming, and caching for AI agents",
)

# Mount MCP server to the FastAPI app
mcp.mount()

# Main function for running the server
def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gen Z Quote Generator with FastAPI-MCP")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print(f"""
🚀 AI-Powered Gen Z Quote Generator with FastAPI-MCP

🤖 AI Model: gpt-4.1-mini via LangChain
📍 API Server: http://{args.host}:{args.port}
🤖 MCP Endpoint: http://{args.host}:{args.port}/mcp
📡 SSE Streaming: http://{args.host}:{args.port}/stream
🔍 Search: http://{args.host}:{args.port}/search
📈 Trending: http://{args.host}:{args.port}/trending
📚 Docs: http://{args.host}:{args.port}/docs

🛠️  MCP Tools Auto-Generated:
✅ generate_viral_quote - Generate AI-powered viral quotes
✅ search_quotes - Search cached quotes with text matching
✅ get_trending_quotes - Get trending cached quotes
✅ get_quotes_by_theme - Get cached quotes by theme
✅ stream_quotes_generation - Stream AI generation with SSE
✅ get_server_info - Server information

🔧 For Claude Desktop, add to config:
{{
  "mcpServers": {{
    "ai-quote-generator": {{
      "command": "mcp-proxy",
      "args": ["http://{args.host}:{args.port}/mcp"]
    }}
  }}
}}

🎯 Example Usage:
curl -X POST "http://{args.host}:{args.port}/generate" \\
     -H "Content-Type: application/json" \\
     -d '{{"theme": "relationships", "target_audience": "empaths"}}'

💾 Storage: In-memory cache (no database)
🧠 AI: LangChain + OpenAI GPT-4.1-mini
    """)
    
    # Run server
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()