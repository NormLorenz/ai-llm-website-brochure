from typing import Any, List, Dict
import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI


class Website:
    ### Represents a website fetched from a URL. ###
    def __init__(self, url: str) -> None:
        self.url: str
        self.title: str
        self.text: str

        # Some websites need you to use proper headers when fetching
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        }

        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)


# Load environment variables in a file called .env
load_dotenv(override=True)

# Get the OpenAI API key from the environment variable
api_key = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client
openai = OpenAI()


def main() -> None:
    ### High level entry point to run the website summarizer. ###
    url = input("Enter a URL to summarize: ")
    display_summary(url)


# Define our system prompt
system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."


def user_prompt_for(website: Website) -> str:
    ### Constructs the user prompt for the OpenAI chat completion API. ###
    user_prompt = f"You are looking at a website titled {website.title}"
    user_prompt += "\nThe contents of this website is as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt


def messages_for(website: Website) -> List[Dict[str, str]]:
    ###  Constructs the message payload for the OpenAI chat completion API. ###
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]


def summarize(url: str) -> str:
    ### Summarizes the website at the given URL using the OpenAI API. ###
    website = Website(url)
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_for(website)
    )
    return response.choices[0].message.content


def display_summary(url: str) -> None:
    ###  Writes to a markdown file the summary of the website at the given URL. ###
    summary = summarize(url)
    with open('BROCHURE.md', 'w', encoding='utf-8') as f:
        f.write(summary)


if __name__ == "__main__":
    main()
