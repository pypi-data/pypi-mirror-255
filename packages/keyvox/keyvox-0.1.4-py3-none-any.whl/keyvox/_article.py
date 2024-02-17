class Article:
    def __init__(self, instance):
        self.instance = instance
        self.base_url = self.instance.base_url

    def list(self, params={}):
        url = f"{self.base_url}/articles"
        articles = self.instance.fetch_data(url, params)
        return articles

    def retrieve(self, id_or_slug: str, params={}):
        url = f"{self.base_url}/articles/{id_or_slug}"
        article = self.instance.fetch_data(url, params)
        return article
