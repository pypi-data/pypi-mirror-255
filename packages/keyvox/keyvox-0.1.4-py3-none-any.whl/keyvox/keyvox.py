from requests import get, Response
from keyvox._article import Article
from keyvox._tag import Tag
from keyvox._author import Author

class KeyVox:
    def __init__(self, api_key: str, base_url: str = 'https://keyvox.dev/api'):
        self.api_key = api_key
        self.base_url = base_url
        self.articles = Article(self)
        self.tags = Tag(self)
        self.authors = Author(self)

    def fetch_data(self, url: str, params: dict) -> Response:
        try:
            response = get(
                url=url,
                headers={
                    'key': self.api_key,
                    'lang': 'python'
                },
                params=params
            )

            return response.json()
        except Exception as error:
            print(error)
