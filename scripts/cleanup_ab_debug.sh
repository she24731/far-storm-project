#!/bin/bash
# Cleanup script for A/B test debug code
# Run this AFTER confirming the system works correctly

echo "🧹 Cleaning up A/B test debug code..."

# Remove debug print statements from views.py
# This uses sed to remove the debug block
# Manual edit recommended instead

echo "⚠️  Manual cleanup required:"
echo ""
echo "1. Remove debug prints from core/views.py (lines 458-461):"
echo "   # TEMPORARY DEBUG LOGGING - Remove after debugging"
echo "   print(\"A/B DEBUG — force_param:\", force_param)"
echo "   print(\"A/B DEBUG — cookie_variant:\", cookie_variant)"
echo "   print(\"A/B DEBUG — final variant:\", variant)"
echo ""
echo "2. Remove debug <pre> block from templates/core/abtest.html (lines 21-24):"
echo "   {# TEMPORARY DEBUG BLOCK - Remove after confirming forced variant works #}"
echo "   <pre id=\"debug\" style=\"background: #f0f0f0; padding: 10px; border: 1px solid #ccc;\">"
echo "   variant=\"{{ variant }}\""
echo "   </pre>"
echo ""
echo "3. Commit and push:"
echo "   git add core/views.py templates/core/abtest.html"
echo "   git commit -m \"Remove A/B test debug code after verification\""
echo "   git push origin main"

