#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Flashcard Generator...${NC}\n"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv .venv

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install requirements
echo -e "${YELLOW}Installing required packages...${NC}"
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}Created .env file from .env.example${NC}"
        echo -e "${YELLOW}Please edit .env and add your OpenAI API key${NC}"
    else
        echo "OPENAI_API_KEY=your-api-key-here" > .env
        echo -e "${GREEN}Created .env file${NC}"
        echo -e "${YELLOW}Please edit .env and add your OpenAI API key${NC}"
    fi
fi

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}To start using Flashcard Generator:${NC}"
echo -e "1. Make sure to add your OpenAI API key to the .env file"
echo -e "2. Run: ${GREEN}python flashcard_generator.py${NC}" 