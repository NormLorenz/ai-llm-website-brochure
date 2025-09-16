# ai-llm-website-summary

This project is a Python application that summarizes the contents of any website using OpenAI's language models. It fetches a website, extracts its main text content, and generates a concise summary in Markdown format.

## Features
- Fetches and parses website content using BeautifulSoup
- Removes irrelevant elements (scripts, styles, images, inputs)
- Uses OpenAI's API to generate a summary
- Outputs the summary in Markdown
- Command-line interface for user input

## How it works
1. The user provides a website URL.
2. The app fetches and parses the website, extracting the main text and title.
3. It constructs a prompt and sends it to OpenAI's chat completion API.
4. The model returns a Markdown summary as a markdown file called SUMMARY.md.

## Setup Steps

1. **Clone the repository**
   ```ps
   git clone https://github.com/NormLorenz/ai-llm-website-summary.git
   cd ai-llm-website-summary
   ```
2. **Install uv (if not already installed)**
   ```ps
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. **Install dependencies using pyproject.toml and uv.lock**
   ```ps
   uv sync
   ```
4. **Set up your OpenAI API key**
   - Create a `.env` file in the project root.
   - Add your API key: OPENAI_API_KEY=your_openai_api_key_here
5. **Run the application**
   ```ps
   uv run main.py
   ```
6. **Enter a website URL when prompted**
   - The summary will be saved to `SUMMARY.md`.

## Requirements
- Python 3.8+
- OpenAI API key (set in a `.env` file)
- Packages: requests, beautifulsoup4, python-dotenv, openai, IPython

## Example
```
Enter a URL to summarize: https://sullivanexcavatinginc.com
```
