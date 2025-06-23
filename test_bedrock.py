#!/usr/bin/env python3
"""
Simple test script to verify AWS Bedrock integration with Claude.
"""

import asyncio
from src.crude_or_rude.nodes.claude import ClaudeDecisionNode


async def test_bedrock_claude():
    """Test that we can create a Claude node and basic functionality."""
    print("🧪 Testing AWS Bedrock Claude integration...")
    
    try:
        # Initialize Claude node (should use your AWS CLI configuration)
        claude = ClaudeDecisionNode()
        print("✅ Successfully initialized Claude node with AWS Bedrock")
        
        # Test basic model info
        print(f"📊 Model ID: {claude.llm.model_id}")
        print(f"🌍 Region: {claude.llm.region_name or 'Default from CLI'}")
        print(f"🎛️  Temperature: {claude.llm.model_kwargs.get('temperature', 0.7)}")
        print(f"🔢 Max tokens: {claude.llm.model_kwargs.get('max_tokens', 4000)}")
        
        print("\n✨ AWS Bedrock integration is ready!")
        print("💡 You can now run your crude-or-rude application with Claude 3.7 Sonnet via AWS Bedrock")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your AWS CLI is configured and has access to Bedrock")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_bedrock_claude())
    exit(0 if success else 1)
