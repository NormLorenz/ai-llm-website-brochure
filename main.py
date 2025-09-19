import json
import os
from typing import List, TypedDict
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI

# Load environment variables in a file called .env
load_dotenv(override=True)

# Get the OpenAI API key from the environment variable
api_key = os.getenv('OPENAI_API_KEY')

# Constants
MODEL = 'gpt-4o-mini'

# Initialize the OpenAI client
openai = OpenAI()

# Some websites need you to use proper headers when fetching them:
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


class Website:
    ### Represents a website fetched from a URL. ###
    def __init__(self, url: str) -> None:
        self.url: str
        self.title: str
        self.text: str
        self.body: bytes

        self.url = url
        response = requests.get(url, headers=headers)
        self.body = response.content
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"

        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""

        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"


class Link(TypedDict):
    type: str
    url: str


def main() -> None:
    ### High level entry point to run the website summarizer. ###
    # company_name, url, language = "OpenAI", "https://openai.com", "English"
    # company_name, url, language = "Anthropic", "https://anthropic.com", "English"
    # company_name, url, language = "Sullivan Excavating", "https://sullivanexcavatinginc.com", "German"
    company_name, url, language = "HuggingFace", "https://huggingface.co", "German"
    # company_name, url, language = "Edward Donner", "https://edwarddonner.com", "English"

    website: Website = Website(url)
    links: List[Link] = create_links(website)
    create_brochure(company_name, language, website, links)


def links_system_prompt() -> str:
    ### Constructs the system prompt for the OpenAI chat completion API. ###
    prompt = "You are provided with a list of links found on a webpage. You are able to decide which of the "
    prompt += "links would be most relevant to include in a brochure about the company, such as links to an "
    prompt += "About page, or a Company page, or Careers/Jobs pages. \n You should respond in JSON as in this example:"
    prompt += """
    {
        "links": [
            {"type": "about page", "url": "https://full.url/goes/here/about"},
            {"type": "careers page", "url": "https://another.full.url/careers"}
        ]
    }
    """
    return prompt


def links_user_prompt(website: Website) -> str:
    ### Constructs the user prompt for the OpenAI chat completion API. ###
    prompt = f"Here is the list of links on the website of {website.url} - "
    prompt += "please decide which of these are relevant web links for a brochure about the company, respond with "
    prompt += "the full https URL in JSON format (not markup). Do not include Terms of Service, Privacy, email links. \n"
    prompt += "Links (some might be relative links):\n"
    prompt += "\n".join(website.links)
    return prompt


def create_links(website: Website) -> List[Link]:
    ### Creates a list of relevant links for the brochure by using the OpenAI API. ###
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": links_system_prompt()},
            {"role": "user", "content": links_user_prompt(website)}
        ],
    )
    result = response.choices[0].message.content

    try:
        loads: List[Link] = json.loads(result)
        return loads
    except json.JSONDecodeError as e:
        return {"links": []}


def brochure_system_prompt() -> str:
    ### Constructs the system prompt for the OpenAI chat completion API. ###
    prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website "
    prompt += "and creates a short brochure about the company for prospective customers, investors and recruits. "
    prompt += "Respond in markdown. Include details of company culture, customers and careers/jobs if you have the information."
    return prompt


def brochure_user_prompt(company_name: str, language: str, website: Website, links: List[Link]) -> str:
    ### Constructs the user prompt for the OpenAI chat completion API. ###
    prompt = f"You are looking at a company called: {company_name}\n"
    prompt += f"Here are the contents of its landing page and other relevant pages; use this information "
    prompt += f"to build a short brochure of the company in markdown. Please translate it into {language}.\n"
    prompt += get_details(website, links)
    prompt = prompt[:5_000]  # Truncate if more than 5,000 characters
    return prompt


def get_details(website: Website, links: List[Link]) -> str:
    ### Fetches and returns the contents of the landing page and other relevant pages. ###
    result = "Landing page:\n"
    result += website.get_contents()
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()
    return result


def create_brochure(company_name: str, language: str, website: Website, links: List[Link]) -> None:
    ### Creates a brochure for the given company by fetching the website and using the OpenAI API. ###
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": brochure_system_prompt()},
            {"role": "user", "content": brochure_user_prompt(
                company_name, language, website, links)}
        ],
    )
    result = response.choices[0].message.content
    with open('BROCHURE.md', 'w', encoding='utf-8') as f:
        f.write(result)


if __name__ == "__main__":
    main()
