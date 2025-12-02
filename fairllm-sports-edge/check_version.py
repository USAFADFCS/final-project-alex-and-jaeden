#!/usr/bin/env python3
"""
Check which version of agentic_workflow you have
"""
import sys
sys.path.insert(0, 'src')

print("Checking your agentic_workflow.py version...\n")

try:
    from fairllm_agent.agentic_workflow import SportsEdgeFlow
    
    # Check if it has LLM capabilities
    workflow = SportsEdgeFlow()
    
    # Check if agents have LLM methods
    if hasattr(workflow.agents[0], 'invoke_llm'):
        print("✅ You have the LLM VERSION!")
        print("   Your agentic_workflow.py includes Phi-3-mini integration")
        print("\nYou're all set! You can:")
        print("  - Run: python3 demo_llm.py")
        print("  - Or: python3 demo.py (for fast version)")
    else:
        print("⚠️  You have the ORIGINAL VERSION (rule-based)")
        print("   This is fast but doesn't use LLMs")
        print("\n📥 You need to download: agentic_workflow_llm.py")
        print("   And import from it instead")
        
    print("\n" + "="*60)
    print("Agents loaded:", [a.name for a in workflow.agents])
    print("="*60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Make sure you're in the fairllm-sports-edge directory")
    print("  2. Check that src/fairllm_agent/agentic_workflow.py exists")
