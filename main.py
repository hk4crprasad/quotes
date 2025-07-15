#!/usr/bin/env python3
"""
Gen Z Quote Generator - Simplified API with modular architecture
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi_mcp import FastApiMCP
import requests
import uvicorn
import os
from config import ACCESS_TOKEN, BASE_URL, INSTAGRAM_USER_ID
from instaupload import InstagramReelsAPI  , api_client
from models import QuickReelRequest, QuoteRequest, QuoteResponse, ReelUploadRequest, ReelUploadResponse, StatusResponse
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
         summary="Generate viral Gen Z motivational quotes with captions, images and videos",
         description="Generate viral quotes with AI-powered captions, hashtags, customizable themes, optional image generation, and video creation with AI-generated titles",
         response_model=QuoteResponse)
async def generate_quote(
    request: QuoteRequest,
    gen: ViralQuoteGenerator = Depends(get_generator)
) -> QuoteResponse:
    """
    Generate a single viral Gen Z motivational quote using AI, with optional image and video generation.
    
    This tool creates authentic, shareable quotes that resonate with today's generation.
    Uses LangChain and OpenAI to generate unique, viral-optimized content.
    Optionally generates beautiful motivational images using Azure OpenAI DALL-E.
    Optionally creates engaging videos using MoviePy for social media.
    
    Inputs:
    - theme: The quote theme - 'relationships', 'self-worth', 'money', 'boundaries', 'growth', or 'mixed'
    - target_audience: Target demographic - 'gen-z', 'millennials', 'empaths', 'introverts', 'overthinkers'
    - format_preference: Optional title format preference
    - image: Whether to generate an image (default: false)
    - image_style: Image style - 'paper', 'modern', 'minimal' (default: 'paper')
    - video: Whether to generate a video (requires image=true, default: false)
    - video_title: Custom video title (defaults to 'Daily Vibe')
    
    Returns:
    - A complete AI-generated quote with title, content, theme, audience, and timestamp
    - Image filename and URL (if image generation requested and successful)
    - Video filename and URL (if video generation requested and successful)
    
    Example:
    Input: {"theme": "relationships", "target_audience": "empaths", "image": true, "video": true}
    Output: {"title": "Maturity is when", "content": "...", "image_url": "...", "video_url": "..."}
    """
    if request.video and not request.image:
        # Video requires image, so enable image generation
        request.image = True
    
    if request.video and request.image:
        # Generate quote with image and video
        (quote, image_filename, image_blob_url, 
         video_filename, video_blob_url, error) = gen.generate_quote_with_video(
            theme=request.theme,
            target_audience=request.target_audience,
            format_preference=request.format_preference,
            image_style=request.image_style
        )
        
        return QuoteResponse(
            title=quote.title,
            content=quote.content,
            theme=quote.theme,
            target_audience=quote.target_audience,
            created_at=quote.created_at,
            caption=quote.caption,
            image_url=image_blob_url,
            image_filename=image_filename,
            video_url=video_blob_url,
            video_filename=video_filename
        )
    elif request.image:
        # Generate quote with image only
        quote, filename, blob_url, error = gen.generate_quote_with_image(
            theme=request.theme,
            target_audience=request.target_audience,
            format_preference=request.format_preference,
            image_style=request.image_style
        )
        
        return QuoteResponse(
            title=quote.title,
            content=quote.content,
            theme=quote.theme,
            target_audience=quote.target_audience,
            created_at=quote.created_at,
            caption=quote.caption,
            image_url=blob_url,
            image_filename=filename,
            video_url=None,
            video_filename=None
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
            caption=quote.caption,
            image_url=None,
            image_filename=None,
            video_url=None,
            video_filename=None
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
        "description": "Viral motivational quote generator with AI, MCP support, Azure Blob Storage, and video generation",
        "ai_powered": True,
        "model": "gpt-4.1-mini",
        "endpoints": {
            "generate": "POST /generate - Generate AI quote with optional image and video",
            "mcp": "GET /mcp - MCP endpoint for AI agents"
        },
        "themes": ["relationships", "self-worth", "money", "boundaries", "growth", "mixed"],
        "audiences": ["gen-z", "millennials", "empaths", "introverts", "overthinkers"],
        "features": {
            "text_generation": "AI-powered viral quotes",
            "image_generation": "Azure OpenAI DALL-E motivational images",
            "video_generation": "MoviePy social media videos with audio"
        },
        "image_storage": "Azure Blob Storage",
        "video_storage": "Azure Blob Storage",
        "blob_container": "891457b8-459e-47dd-9d36-49b8b8227668-azureml",
        "blob_folders": {
            "images": "image-gen",
            "videos": "video-gen"
        },
        "mcp_compatible": True,
        "storage": "stateless - no database"
    }


@app.get("/")
async def root():
    return {
        "message": "Instagram Reels API Server",
        "version": "1.0.0",
        "endpoints": {
            "POST /upload": "Upload a reel with full options",
            "POST /quick-upload": "Quick upload with just video_url and caption",
            "GET /status/{container_id}": "Check container status",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test API connectivity
        response = requests.get(
            f"{BASE_URL}/{INSTAGRAM_USER_ID}?fields=id&access_token={ACCESS_TOKEN}",
            timeout=10
        )
        if response.status_code == 200:
            return {"status": "healthy", "instagram_api": "connected"}
        else:
            return {"status": "unhealthy", "instagram_api": "failed"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/upload", response_model=ReelUploadResponse)
async def upload_reel(request: ReelUploadRequest):
    """
    Upload Instagram Reel with full options
    
    - **video_url**: Publicly accessible HTTPS URL to the video
    - **caption**: Caption for the reel
    - **share_to_feed**: Whether to show in both Feed and Reels tabs
    - **thumb_offset**: Thumbnail frame offset in milliseconds
    - **location_id**: Facebook Page ID for location tagging
    """
    try:
        result = api_client.upload_reel_complete(
            video_url=str(request.video_url),
            caption=request.caption,
            share_to_feed=request.share_to_feed,
            thumb_offset=request.thumb_offset,
            location_id=request.location_id
        )
        
        return ReelUploadResponse(
            success=True,
            message="Reel uploaded successfully!",
            container_id=result["container_id"],
            media_id=result["media_id"],
            status=result["status"]
        )
        
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg = f"Instagram API Error: {error_detail.get('error', {}).get('message', str(e))}"
            except:
                error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
        
        raise HTTPException(status_code=400, detail=error_msg)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/quick-upload", response_model=ReelUploadResponse)
async def quick_upload_reel(request: QuickReelRequest):
    """
    Quick upload Instagram Reel with just video URL and caption
    
    - **video_url**: Publicly accessible HTTPS URL to the video
    - **caption**: Caption for the reel
    """
    try:
        result = api_client.upload_reel_complete(
            video_url=str(request.video_url),
            caption=request.caption,
            share_to_feed=True
        )
        
        return ReelUploadResponse(
            success=True,
            message="Reel uploaded successfully!",
            container_id=result["container_id"],
            media_id=result["media_id"],
            status=result["status"]
        )
        
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg = f"Instagram API Error: {error_detail.get('error', {}).get('message', str(e))}"
            except:
                error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
        
        raise HTTPException(status_code=400, detail=error_msg)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/status/{container_id}", response_model=StatusResponse)
async def check_status(container_id: str):
    """
    Check the status of a media container
    
    - **container_id**: ID of the container to check
    """
    try:
        status = api_client.check_container_status(container_id)
        
        status_messages = {
            "FINISHED": "Container is ready for publishing",
            "IN_PROGRESS": "Container is still processing",
            "ERROR": "Container failed to process",
            "EXPIRED": "Container has expired",
            "UNKNOWN": "Unknown status"
        }
        
        return StatusResponse(
            success=True,
            status=status,
            message=status_messages.get(status, f"Status: {status}")
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to check status: {str(e)}")

@app.post("/container/create")
async def create_container_only(request: ReelUploadRequest):
    """
    Create container only (for manual publishing later)
    """
    try:
        result = api_client.create_reel_container(
            video_url=str(request.video_url),
            caption=request.caption,
            share_to_feed=request.share_to_feed,
            thumb_offset=request.thumb_offset,
            location_id=request.location_id
        )
        
        return {
            "success": True,
            "message": "Container created successfully",
            "container_id": result["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create container: {str(e)}")

@app.post("/container/{container_id}/publish")
async def publish_container(container_id: str):
    """
    Publish a ready container
    """
    try:
        # Check if container is ready
        status = api_client.check_container_status(container_id)
        if status != "FINISHED":
            raise HTTPException(
                status_code=400, 
                detail=f"Container not ready. Status: {status}"
            )
        
        result = api_client.publish_reel(container_id)
        
        return {
            "success": True,
            "message": "Reel published successfully",
            "media_id": result["id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to publish: {str(e)}")

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
✅ generate_viral_quote - Generate AI quotes with captions, hashtags, images and videos
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
     -d '{{"theme": "relationships", "target_audience": "empaths", "image": true, "video": true}}'

💾 Architecture: Modular, stateless, no database
🧠 AI: LangChain + OpenAI GPT-4.1-mini
🎨 Images: Azure OpenAI DALL-E + Azure Blob Storage
🎬 Videos: MoviePy + Azure Blob Storage with AI-generated titles
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
