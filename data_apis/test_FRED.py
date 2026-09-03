# for FRED pull data, and have it find dates for economic releases


class FRED:

    def __init__(self, key):
        self.key = key

    def build_url(self):
