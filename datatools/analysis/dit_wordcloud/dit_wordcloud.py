import random
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
# TODO handle for stopwords during install.
# nltk.download('stopwords') or python -m nltk.downloader stopwords



try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML

from datatools.utils.nlp import striphtml, striptradegov

class Dit_wordcloud():
    def __init__(self):
        self.jargon_stopwords = set()
        self.people_stopwords = set()
        self.stop_words = set(stopwords.words('english'))
        self.tokenizer = RegexpTokenizer(r'\w+')

        self.dit_colors =  [
            (205, 22, 50),
            (183, 0, 28),
            (230, 47, 75),
            (255, 77, 100),
            (0, 94, 165),
            (30, 124, 195),
            (60, 154, 225),
        ]

    def add_stopwords(self, **kwargs):
        ''''
        optional kwargs
        jargon_stopwords: list or set
        people_stopwords: list or set
        path_to_jargon_stopwords: string
        path_to_people_stopwords: string

        '''
        if kwargs.get("jargon_stopwords", None):
            _jargon_stopwords = kwargs.get("jargon_stopwords")
            if type(_jargon_stopwords) is list:
                self.jargon_stopwords.update(set(_jargon_stopwords))
            else:
                self.jargon_stopwords.update(_jargon_stopwords)

        if kwargs.get("people_stopwords", None):
            _people_stopwords = kwargs.get("people_stopwords")
            if type(_people_stopwords) is list:
                self.people_stopwords.update(set(_people_stopwords))
            else:
                self.people_stopwords.update(_people_stopwords)

    def get_tokens(self, sentence, lower=False):
        if lower is True:
            sentence = sentence.lower()
        sentence = striptradegov(striphtml(sentence))
        sentence = sentence.translate({ord(ch): None for ch in '0123456789'})
        return self.tokenizer.tokenize(sentence)

    def process_raw_text(self, sentence, filters=['stop_words', 'people_stopwords']):
        '''
        filers: list of strings where string is in set 'stop_words', 'people_stopwords', 'jargon_stopwords'
        '''
        word_tokens = self.get_tokens(sentence)

        # ToDO refactor stop_words to english_stopwords.

        # Todo add new <*_stopwords> function and have it carry to here.
        for each in filters:
            if each not in ["jargon_stopwords"]:
                _stopword_list = getattr(self, each)
                filtered_sentence = [w for w in word_tokens if not w in _stopword_list]
            elif each in ['jargon_stopwords']:
                 filtered_sentence = [w for w in filtered_sentence if w not in jargon_stopwords and len(w) > 1]
        return filtered_sentence

    def random_color_func(self, word=None, font_size=None, position=None, orientation=None, font_path=None,
                          random_state=None):
        if word == 'trade':
            return self.dit_colors[0]
        if word == 'service':
            return self.dit_colors[4]
        else:
            c = int(random.randint(1, len(self.dit_colors) - 1))
            return self.dit_colors[c]

    def create_word_cloud(self, list_of_documents):
        words_flat_list = [item for document in list_of_documents for item in document]
        wordcloud = WordCloud(
            background_color='white', max_words=300,
            width=1920, height=1080, color_func=self.random_color_func,
            stopwords=['health', 'care'] + list(STOPWORDS)
        ).generate(' '.join(words_flat_list))
        plt.figure(figsize=(80, 80))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()


    def make_visual(self, text_string):
        ptext = self.process_raw_text(text_string)
        self.create_word_cloud([[p.lower() for p in ptext]])

if __name__ in "__main__":
    text_string  = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore 
magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo 
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""
    cloud = WordCloud()
    cloud.mmake_visual([[p.lower() for p in text_string]])