#!/bin/bash

# Script to check file structure before building Docker image
set -e

echo "Checking file structure..."

# Check if pyproject.toml exists in proxy-lite
if [ -f "proxy-lite/pyproject.toml" ]; then
    echo "✅ proxy-lite/pyproject.toml exists"
else
    echo "❌ proxy-lite/pyproject.toml MISSING"
    echo "Creating minimal pyproject.toml file..."
    mkdir -p proxy-lite
    cat > proxy-lite/pyproject.toml << EOL
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "proxy-lite"
version = "0.0.1"
EOL
    echo "✅ Created minimal pyproject.toml"
fi

# Check if src directory exists in proxy-lite
if [ -d "proxy-lite/src" ]; then
    echo "✅ proxy-lite/src directory exists"
else
    echo "❌ proxy-lite/src directory MISSING"
    mkdir -p proxy-lite/src
    echo "✅ Created proxy-lite/src directory"
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

echo ""
echo "File structure check complete."
echo "You can now run docker/build.sh to build the Docker image." 