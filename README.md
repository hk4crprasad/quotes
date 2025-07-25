# AI-Powered Gen Z Quote Generator

<div align="center">
  <img src="logo.svg" alt="AI-Powered Gen Z Quote Generator" width="400"/>
</div>

An intelligent viral quote generator that creates authentic, shareable motivational content for social media platforms. Built with AI, image generation, and video creation capabilities.

## ✨ Features

- 🤖 **AI-Powered Quote Generation**: Uses GPT-4.1-mini via LangChain to create viral-optimized quotes
- 🎨 **Image Generation**: Azure OpenAI DALL-E integration for motivational images  
- 🎬 **Video Creation**: Automated video generation with MoviePy and audio
- 📱 **Instagram Reels Integration**: Direct upload to Instagram with comprehensive API support
- 🎯 **Multiple Themes**: Relationships, self-worth, money, boundaries, growth, and mixed content
- 👥 **Target Audiences**: Gen-Z, millennials, empaths, introverts, overthinkers
- ☁️ **Cloud Storage**: Azure Blob Storage for images and videos
- 🔗 **MCP Support**: Model Context Protocol for AI agent integration
- ⚡ **FastAPI Backend**: RESTful API with interactive documentation

## 🚀 Quick Start

### 📋 Prerequisites

- Python 3.11+
- Azure OpenAI account (for image generation)
- Azure Blob Storage account  
- Instagram Business account (for Reels upload)

### 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd quotes
   ```

2. **Install dependencies using uv:**
   ```bash
   pip install uv
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

### 🔧 Environment Variables

Create a `.env` file with:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://litellm.tecosys.ai/

# Azure OpenAI (for image generation)
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_KEY=your_azure_key
DEPLOYMENT_NAME=your_deployment_name

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_CONTAINER_NAME=your_container_name

# Instagram API
ACCESS_TOKEN=your_instagram_access_token
```

### 🏃‍♂️ Running the Application

#### 💻 Local Development
```bash
python main.py --host localhost --port 8000 --reload
```

#### 🐳 Using Docker
```bash
docker build -t quote-generator .
docker run -p 8091:8091 --env-file .env quote-generator
```

#### 📝 Using the provided script
```bash
./start_quote_generator.sh
```

## 🔌 API Endpoints

### 💬 Quote Generation
- `POST /generate` - Generate quotes with optional image and video
- `GET /` - Server information and feature overview

### 📱 Instagram Reels
- `POST /upload` - Upload reel with full options
- `POST /quick-upload` - Quick upload with video URL and caption
- `GET /status/{container_id}` - Check upload status
- `GET /health` - Health check

### 🔗 MCP Integration
- `GET /mcp` - Model Context Protocol endpoint for AI agents

## 💡 Usage Examples

### 🎨 Generate a Quote with Image and Video
```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "theme": "relationships",
       "target_audience": "empaths",
       "image": true,
       "video": true,
       "image_style": "paper"
     }'
```

### 📱 Quick Instagram Reel Upload
```bash
curl -X POST "http://localhost:8000/quick-upload" \
     -H "Content-Type: application/json" \
     -d '{
       "video_url": "https://example.com/video.mp4",
       "caption": "Motivational quote of the day! #motivation"
     }'
```

## 📁 Project Structure

```
quotes/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and constants
├── models.py              # Pydantic models for API
├── quote_generator.py     # Core quote generation logic
├── image_generator.py     # Image generation with DALL-E
├── video_generator.py     # Video creation with MoviePy
├── instaupload.py         # Instagram Reels API integration
├── title.py               # Video title generation
├── Dockerfile             # Docker configuration
├── requirements.txt       # Python dependencies
└── pyproject.toml         # Project metadata
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT and DALL-E APIs
- Azure for cloud services
- FastAPI for the excellent web framework
- MoviePy for video processing capabilities