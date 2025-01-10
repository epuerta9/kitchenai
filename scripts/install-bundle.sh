#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting KitchenAI Development Kit installation...${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install git first."
    exit 1
fi

# Create a temporary directory
TMP_DIR=$(mktemp -d)

# Clone the repository
echo -e "${BLUE}Cloning KitchenAI repository...${NC}"
git clone https://github.com/epuerta9/kitchenai.git "$TMP_DIR"

# Check if clone was successful
if [ $? -ne 0 ]; then
    echo "Failed to clone repository"
    rm -rf "$TMP_DIR"
    exit 1
fi

# Copy necessary files to current directory
echo -e "${BLUE}Copying configuration files...${NC}"
cp "$TMP_DIR/docker-compose.yml" .
cp "$TMP_DIR/.env.template" .env

# Create necessary directories
mkdir -p .kitchenai
mkdir -p dynamic
mkdir -p chroma_db

# Copy helper scripts
cp "$TMP_DIR/scripts/restart-stream.sh" .
chmod +x restart-stream.sh

# Clean up temporary directory
rm -rf "$TMP_DIR"

# Check if installation was successful
if [ -f "docker-compose.yml" ] && [ -f ".env" ]; then
    echo -e "${GREEN}✅ KitchenAI Development Kit has been successfully installed!${NC}"
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "1. Export your OpenAI API key: export OPENAI_API_KEY=your-key-here"
    echo -e "2. Start the environment: docker compose up"
    echo -e "3. Create a KitchenAI bucket at localhost:9001"
    echo -e "4. Connect to kitchenai-local container using VSCode DevContainers"
else
    echo "Installation failed"
    exit 1
fi
