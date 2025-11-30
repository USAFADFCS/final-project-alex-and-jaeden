#!/bin/bash
# Quick setup and demo script for FairLLM Sports Edge Analysis

echo "=================================================="
echo "FairLLM Sports Edge Analysis - Quick Setup"
echo "=================================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt --break-system-packages

echo ""
echo "Running tests..."
python3 -m pytest tests/ -v

echo ""
echo "=================================================="
echo "Running Demo..."
echo "=================================================="
echo ""

# Run single game analysis
echo "1. Single Game Analysis:"
python3 -m fairllm_agent.cli_enhanced \
    --odds data/samples/odds_demo.json \
    --forecast data/samples/forecast_demo.json \
    --out edge_report.json

echo ""
echo "2. Batch Processing:"
python3 -m fairllm_agent.cli_enhanced \
    --batch data/samples/batch_test.json \
    --out batch_results.json

echo ""
echo "3. Running Evaluation:"
python3 -m fairllm_agent.evaluate \
    --reports batch_results.json \
    --out evaluation_metrics.json

echo ""
echo "=================================================="
echo "Setup and Demo Complete!"
echo "=================================================="
echo ""
echo "Generated files:"
echo "  • edge_report.json - Single game analysis"
echo "  • batch_results.json - Batch analysis results"
echo "  • evaluation_metrics.json - Performance metrics"
echo ""
echo "Next steps:"
echo "  • Review README_COMPLETE.md for full documentation"
echo "  • Run 'python3 demo.py' for interactive demonstration"
echo "  • Review Project_Report.docx for academic write-up"
echo ""