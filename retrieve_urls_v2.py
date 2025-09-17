import requests
import pickle

NPMS_SEARCH_URL = "https://api.npms.io/v2/search"
NPMS_PACKAGE_URL = "https://api.npms.io/v2/package/"

def get_github_repo_url(metadata):
    repo = metadata.get('repository')
    if repo and repo.get('type') == 'git' and 'https://github.com' in repo.get('url', ''):
        url = repo['url']
        # Clean up the URL
        if url.startswith('git+'):
            url = url[4:]
        if url.endswith('.git'):
            url = url[:-4]
        return url
    return None

def main():
    repos = set()
    from_offset = 0
    size = 100  # npms.io allows up to 250 per page
    while len(repos) < 100:
        params = {
            "q": "not:deprecated not:unstable not:insecure",
            "size": size,
            "from": from_offset
        }
        resp = requests.get(NPMS_SEARCH_URL, params=params)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if not results:
            print("no response")
            break
        for result in results:
            pkg_name = result['package']['name']
            # Get detailed package info
            pkg_resp = requests.get(NPMS_PACKAGE_URL + pkg_name)
            if pkg_resp.status_code != 200:
                continue
            pkg_info = pkg_resp.json()
            metadata = pkg_info.get('collected', {}).get('metadata', {})
            repo_url = get_github_repo_url(metadata)
            if repo_url:
                repos.add(repo_url)
            if len(repos) >= 100:
                break
        from_offset += size
    print(f"Found {len(repos)} repositories:")
    for url in repos:
        print(url)
    with open("repos.pkl", "wb") as f:
        pickle.dump(repos, f)

if __name__ == "__main__":
    main()
