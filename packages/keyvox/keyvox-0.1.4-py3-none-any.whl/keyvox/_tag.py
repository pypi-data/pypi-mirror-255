class Tag:
    def __init__(self, instance):
        self.instance = instance
        self.base_url = self.instance.base_url

    def list(self, params={}):
        url = f"{self.base_url}/tags"
        tags = self.instance.fetch_data(url, params)
        return tags

    def retrieve(self, id_or_slug: str, params={}):
        url = f"{self.base_url}/tags/{id_or_slug}"
        tag = self.instance.fetch_data(url, params)
        return tag
