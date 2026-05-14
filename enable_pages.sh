#!/bin/bash

# This script uses gh CLI if available, or provides manual steps
if command -v gh &> /dev/null; then
    echo "Using GitHub CLI to enable Pages..."
    gh repo edit samanabran/SGC-IT --enable-github-pages
else
    echo "GitHub CLI not available"
    echo "Manual steps:"
    echo "1. Navigate to: https://github.com/samanabran/SGC-IT"
    echo "2. Click on 'Settings' (look for gear icon or tab at far right)"
    echo "3. Under 'Code and automation' section, click 'Pages'"
    echo "4. Under 'Source', select 'Deploy from a branch'"
    echo "5. Select 'main' from the branch dropdown"  
    echo "6. Leave folder as '/ (root)'"
    echo "7. Click 'Save'"
    echo ""
    echo "After ~2 minutes, your site will be live at:"
    echo "https://samanabran.github.io/SGC-IT/"
fi
