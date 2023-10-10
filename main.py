import openai
from googlesearch import search
import requests
from bs4 import BeautifulSoup


openai.api_key = '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'

def fetch_from_wikipedia(ngo_name):
    #endpoint = "https://en.wikipedia.org/api/rest_v1/page/summary/"
    endpoint = "https://es.wikipedia.org/wiki/"
    
    response = requests.get(endpoint + ngo_name)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
        #data = response.json()
        #return data.get('extract', "No summary available.")
    else:
        return "No information found."

def summarize_with_openai(ngo, search_result):
    """
    Uses OpenAI to get a summarized answer for the provided search result.
    :param search_result: String containing the search result or information about the NGO.
    :return: Summarized information.
    """
    prompt = f"This is the first 300 words of the first website that came up in a search for an NGO in Chiapas, Mexico, called {ngo}. We are looking for NGOs that are involved in education and empowerment of communities. In English, try to extrapolate what this NGO does from the words provided in 2 sentences or less. It is possible the websites are irrelevant to the NGO. If unsure, say \"I am unsure because\" and explain in a short sentence why the info does not look related to an NGO:\n\n{search_result}"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=200
    )
    return response.choices[0].text.strip()

def google_top3(query):
    search_results = list(search(query, num=3, stop=3, pause=2))
    extracted_texts = []

    for result in search_results:
        page = requests.get(result)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Extracting text and splitting by spaces to get words
        words = soup.get_text().split()
        
        extracted_text = ' '.join(words[:300])
        extracted_texts.append(extracted_text)

    return (extracted_texts, search_results)

def read_ngo_file(file_name):
    """
    Reads the provided file and extracts individual NGO information.
    :param file_name: Name/path of the file.
    :return: List of NGOs with their details.
    """
    with open(file_name, 'r', encoding='utf-8') as file:
        content = file.read()
        # Splitting the content by two newlines to get individual NGOs' details
        ngo_chunks = content.split('\n\n')
        return ngo_chunks

def extract_ngo_name(ngo_chunk):
    """
    Extracts the NGO name from the chunk of its information.
    :param ngo_chunk: Information chunk of the NGO.
    :return: Name of the NGO.
    """
    # Splitting by newline and taking the first part to get the name
    return ngo_chunk.split('\n')[0]

def main():
    file_name = "ngos.txt"
    ngo_chunks = read_ngo_file(file_name)
    ngos = [extract_ngo_name(chunk) for chunk in ngo_chunks]

    # Table header
    print("| NGO | Summary | Links |")
    print("| --- | --- | --- |")

    for ngo in ngos:
        try:
            ngo_info, links = google_top3(ngo)
            #ngo_info = fetch_from_wikipedia(ngo)
            if ngo_info:
                summary = summarize_with_openai(ngo, ngo_info)
                md_links = ', '.join([f"[{i+1}]({link})" for i, link in enumerate(links)])
                print(f"| {ngo} | {summary} | {md_links} |")
            else:
                print(f"{ngo}: No information found on Google.")
        except Exception as e:
            print(f"| {ngo} | ERROR: {e} | |")
            #if e.code == 429 :
            #print(f"\nERROR [{ngo}]: {e}\n")
                #break

if __name__ == "__main__":
    main()
