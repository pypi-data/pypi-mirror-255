import requests
import json

REFERENCE_COUNT = 8
SERPER_SEARCH_ENDPOINT = "https://google.serper.dev/search"
DEFAULT_SEARCH_ENGINE_TIMEOUT = 5

def search_with_serper(query: str, subscription_key: str,response_url_num = 6):
    """
    Search with serper and return the contexts.
    """
    payload = json.dumps({
        "q": query,
        "gl": "cn",
        "hl": "zh-cn",
        "num": (
            REFERENCE_COUNT
            if REFERENCE_COUNT % response_url_num == 0
            else (REFERENCE_COUNT // response_url_num + 1) * response_url_num
        ),
    })
    headers = {"X-API-KEY": subscription_key, "Content-Type": "application/json"}
    print(f"""
    logger.info(
        f"{payload} {headers} {subscription_key} {query} {SERPER_SEARCH_ENDPOINT}"
    )
    """)

    response = requests.post(
        SERPER_SEARCH_ENDPOINT,
        headers=headers,
        data=payload,
        timeout=DEFAULT_SEARCH_ENGINE_TIMEOUT,
    )
    if not response.ok:
        print(f"""
        logger.error(f"{response.status_code} {response.text}")
        raise HTTPException(response.status_code, "Search engine error.")
        """)

    json_content = response.json()
    try:
        # convert to the same format as bing/google
        contexts = []
        if json_content.get("knowledgeGraph"):
            url = json_content["knowledgeGraph"].get("descriptionUrl") or json_content["knowledgeGraph"].get("website")
            snippet = json_content["knowledgeGraph"].get("description")
            if url and snippet:
                contexts.append({
                    "name": json_content["knowledgeGraph"].get("title",""),
                    "url": url,
                    "snippet": snippet
                })
        if json_content.get("answerBox"):
            url = json_content["answerBox"].get("url")
            snippet = json_content["answerBox"].get("snippet") or json_content["answerBox"].get("answer")
            if url and snippet:
                contexts.append({
                    "name": json_content["answerBox"].get("title",""),
                    "url": url,
                    "snippet": snippet
                })
        contexts += [
            {"name": c["title"], "url": c["link"], "snippet": c.get("snippet","")}
            for c in json_content["organic"]
        ]
        return contexts[:REFERENCE_COUNT]
    except KeyError:
        print(f"""
        logger.error(f"Error encountered: {json_content}")
        """)

        return []

search_api_key = "b0853795d4b9c4a282d639c31919d72d53943a66"

search_function = lambda query: search_with_serper(
                query,
                search_api_key,
            )

query = "什么是酶切位点"
contexts = search_function(query)
print(contexts)





