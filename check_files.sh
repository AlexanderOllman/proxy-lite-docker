#!/bin/bash

# Script to check file structure before building Docker image
set -e

echo "Checking file structure..."

# Flag to track if any check fails
ANY_CHECK_FAILED=false

# Check if pyproject.toml exists in proxy-lite
if [ -f "proxy-lite/pyproject.toml" ]; then
    echo "✅ proxy-lite/pyproject.toml exists"
else
    echo "❌ proxy-lite/pyproject.toml MISSING"
    ANY_CHECK_FAILED=true
fi

# Check if src directory exists in proxy-lite
if [ -d "proxy-lite/src" ]; then
    echo "✅ proxy-lite/src directory exists"
else
    echo "❌ proxy-lite/src directory MISSING"
    ANY_CHECK_FAILED=true
fi

# Check if Dockerfile exists
if [ -f "Dockerfile" ]; then
    echo "✅ Dockerfile exists"
else
    echo "❌ Dockerfile MISSING"
    if [ -f "docker/Dockerfile" ]; then
        echo "Found docker/Dockerfile, copying to root..."
        cp docker/Dockerfile .
        echo "✅ Copied Dockerfile to root"
    else
        echo "❌ No Dockerfile found in docker/ directory either"
    fi
fi

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt exists"
else
    echo "❌ requirements.txt MISSING"
fi

# If any check failed, remove proxy-lite directory and clone from GitHub
if [ "$ANY_CHECK_FAILED" = true ]; then
    echo ""
    echo "Some checks failed. Removing proxy-lite directory and cloning fresh from GitHub..."
    
    # Remove existing proxy-lite directory if it exists
    if [ -d "proxy-lite" ]; then
        rm -rf proxy-lite
        echo "Removed existing proxy-lite directory"
    fi
    
    # Clone the repository from GitHub
    echo "Cloning proxy-lite from GitHub..."
    git clone https://github.com/convergence-ai/proxy-lite.git
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully cloned proxy-lite repository"
    else
        echo "❌ Failed to clone repository. Please check your internet connection and try again."
        exit 1
    fi
fi

echo ""
echo "File structure check complete."
echo "You can now run docker/build.sh to build the Docker image." 