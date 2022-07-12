class SourceResult:
    def __init__(self, name, new_data: dict, html, complete=True, error=""):
        self.name = name
        self.new_data: dict = new_data
        self.html = html
        self.complete = complete
        self.error = ""