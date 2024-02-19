class Conjugator:
    
    def __init__(self, verb, tense='present', lang='fr'):
        self.result = []
        self.tense = tense
        self.lang = lang
    
    def retrieve_page(self):
        pass