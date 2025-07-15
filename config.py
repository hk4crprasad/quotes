#!/usr/bin/env python3
"""
Configuration and constants for the Gen Z Quote Generator
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LLM Configuration
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://litellm.tecosys.ai/")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4.1-mini"
TEMPERATURE = 0.8

# Azure OpenAI Image Generation Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://hara-md2td469-westus3.cognitiveservices.azure.com/")
AZURE_DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "gpt-image-1")
AZURE_API_VERSION = os.getenv("OPENAI_API_VERSION", "2025-04-01-preview")
AZURE_SUBSCRIPTION_KEY = os.getenv("AZURE_OPENAI_API_KEY")

# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
AZURE_BLOB_FOLDER = os.getenv("AZURE_BLOB_FOLDER", "image-gen")

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

# Image generation style templates
IMAGE_STYLE_TEMPLATES = {
    "paper": """
Design a square motivational quote image with a realistic paper-like texture as the background. 
Use bold black serif or clean font for the quote. Highlight key parts of the text in yellow, 
as if marked with a highlighter. Place the quote in the center of the image, and in the bottom-right corner, 
write "—hara point" in a smaller, minimalist font. At the bottom center, include the line: "Share this if you agree." 
The overall style should match an inspirational Instagram quote post with a warm, authentic, and thoughtful aesthetic.
Quote: {quote_text}
""",
    "modern": """
Create a modern, minimalist square quote image with a clean gradient background. 
Use a contemporary sans-serif font in dark text for the quote. 
Center the quote with proper spacing and add "—hara point" in the bottom-right corner in a subtle font. 
Include "Share this if you agree" at the bottom center. 
Style should be clean, professional, and Instagram-ready.
Quote: {quote_text}
""",
    "minimal": """
Design a simple, elegant square quote image with a solid color or subtle texture background. 
Use clean typography with the quote prominently centered. 
Add "—hara point" attribution in the bottom-right and "Share this if you agree" at the bottom center. 
Keep the design minimalist and focused on the text.
Quote: {quote_text}
"""
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
