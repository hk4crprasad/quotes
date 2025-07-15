#!/usr/bin/env python3
"""
Gen Z Quote Generator - Simplified API with modular architecture
"""

from fastapi import FastAPI, Depends
from fastapi_mcp import FastApiMCP
import uvicorn
import os

from models import QuoteRequest, QuoteResponse
from quote_generator import ViralQuoteGenerator


# Create FastAPI app
app = FastAPI(
    title="Gen Z Quote Generator API",
    description="AI-powered viral motivational quote generator",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global generator instance
generator = ViralQuoteGenerator()


def get_generator() -> ViralQuoteGenerator:
    """Dependency to get generator instance"""
    return generator


@app.post("/generate", 
         operation_id="generate_viral_quote",
         summary="Generate viral Gen Z motivational quotes with optional images",
         description="Generate viral quotes with AI-powered customizable themes and optional image generation",
         response_model=QuoteResponse)
async def generate_quote(
    request: QuoteRequest,
    gen: ViralQuoteGenerator = Depends(get_generator)
) -> QuoteResponse:
    """
    Generate a single viral Gen Z motivational quote using AI, with optional image generation.
    
    This tool creates authentic, shareable quotes that resonate with today's generation.
    Uses LangChain and OpenAI to generate unique, viral-optimized content.
    Optionally generates beautiful motivational images using Azure OpenAI DALL-E.
    
    Inputs:
    - theme: The quote theme - 'relationships', 'self-worth', 'money', 'boundaries', 'growth', or 'mixed'
    - target_audience: Target demographic - 'gen-z', 'millennials', 'empaths', 'introverts', 'overthinkers'
    - format_preference: Optional title format preference
    - image: Whether to generate an image (default: false)
    - image_style: Image style - 'paper', 'modern', 'minimal' (default: 'paper')
    
    Returns:
    - A complete AI-generated quote with title, content, theme, audience, and timestamp
    - Image filename and URL (if image generation requested and successful)
    
    Example:
    Input: {"theme": "relationships", "target_audience": "empaths", "image": true}
    Output: {"title": "Maturity is when", "content": "you stop asking people why they don't call...", "image_url": "/images/quote_123.jpeg"}
    """
    if request.image:
        # Generate quote with image
        quote, filename, blob_url, error = gen.generate_quote_with_image(
            theme=request.theme,
            target_audience=request.target_audience,
            format_preference=request.format_preference,
            image_style=request.image_style
        )
        
        # Use blob URL directly
        image_url = blob_url if blob_url else None
        
        return QuoteResponse(
            title=quote.title,
            content=quote.content,
            theme=quote.theme,
            target_audience=quote.target_audience,
            created_at=quote.created_at,
            image_url=image_url,
            image_filename=filename
        )
    else:
        # Just generate quote without image
        quote = gen.generate_quote(
            theme=request.theme,
            target_audience=request.target_audience,
            format_preference=request.format_preference
        )
        
        return QuoteResponse(
            title=quote.title,
            content=quote.content,
            theme=quote.theme,
            target_audience=quote.target_audience,
            created_at=quote.created_at,
            image_url=None,
            image_filename=None
        )


@app.get("/",
         operation_id="get_server_info",
         summary="Get server information",
         description="Get information about the AI-powered quote generator server")
async def root():
    """Get server information"""
    return {
        "name": "AI-Powered Gen Z Quote Generator API",
        "version": "1.0.0",
        "description": "Viral motivational quote generator with AI, MCP support, and Azure Blob Storage",
        "ai_powered": True,
        "model": "gpt-4.1-mini",
        "endpoints": {
            "generate": "POST /generate - Generate AI quote with optional image",
            "mcp": "GET /mcp - MCP endpoint for AI agents"
        },
        "themes": ["relationships", "self-worth", "money", "boundaries", "growth", "mixed"],
        "audiences": ["gen-z", "millennials", "empaths", "introverts", "overthinkers"],
        "image_storage": "Azure Blob Storage",
        "blob_container": "891457b8-459e-47dd-9d36-49b8b8227668-azureml",
        "blob_folder": "image-gen",
        "mcp_compatible": True,
        "storage": "stateless - no database"
    }


# Initialize FastAPI MCP
mcp = FastApiMCP(
    app,
    name="AI-Powered Gen Z Quote Generator",
    description="AI-powered viral motivational quote generator with LangChain for AI agents",
)

# Mount MCP server to the FastAPI app
mcp.mount()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gen Z Quote Generator with FastAPI-MCP")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print(f"""
🚀 AI-Powered Gen Z Quote Generator (Modular Architecture)

🤖 AI Model: gpt-4.1-mini via LangChain
📍 API Server: http://{args.host}:{args.port}
🤖 MCP Endpoint: http://{args.host}:{args.port}/mcp
📚 Docs: http://{args.host}:{args.port}/docs

🛠️  MCP Tools Available:
✅ generate_viral_quote - Generate AI-powered viral quotes with optional images
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
     -d '{{"theme": "relationships", "target_audience": "empaths", "image": true}}'

💾 Architecture: Modular, stateless, no database
🧠 AI: LangChain + OpenAI GPT-4.1-mini
    """)
    
    # Run server
    uvicorn.run(
        "main:app",  #
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
