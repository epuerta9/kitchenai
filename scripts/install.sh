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

# Copy development-kit directory to current location
echo -e "${BLUE}Copying development kit files...${NC}"
cp -r "$TMP_DIR/development-kit" .

# Clean up temporary directory
rm -rf "$TMP_DIR"

# Check if copy was successful
if [ -d "development-kit" ]; then
    echo -e "${GREEN}✅ KitchenAI Development Kit has been successfully installed!${NC}"
    echo -e "${BLUE}You can find the development kit in the ./development-kit directory${NC}"
else
    echo "Installation failed"
    exit 1
fi
# Copy .env.template to .env
echo -e "${BLUE}Creating .env file from template...${NC}"
cp development-kit/.env.template development-kit/.env

# Check if copy was successful
if [ -f "development-kit/.env" ]; then
    echo -e "${GREEN}✅ .env file created successfully${NC}"
else
    echo "Failed to create .env file"
    exit 1
fi
