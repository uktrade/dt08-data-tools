import sys
sys.path.append('..')
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from analysis.utils.nlp.dit_wordcloud import striphtml, striptradegov

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
# TODO handle for stopwords during install.
 #or python -m nltk.downloader stopwords
import random

try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML



class Dit_wordcloud():
    def __init__(self):

        self.english_stopwords = set(stopwords.words('english'))
        self.jargon_stopwords = set()
        self.other_stopwords = set()

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

        '''
        if kwargs.get("jargon_stopwords", None):
            _jargon_stopwords = kwargs.get("jargon_stopwords", set())
            self.jargon_stopwords.update(_jargon_stopwords)

        for k in kwargs.keys():
            if k in ["jargon_stopwords"]:
                pass
            else:
                _new_stopwords = kwargs.get(k, set())
                if type(_new_stopwords) is list:
                    self.other_stopwords.update(set(_new_stopwords = kwargs.get(k)))
                else:
                    self.other_stopwords.update(_new_stopwords)

    def get_tokens(self, sentence, lower=True):
        ''''
        This tokenizes a sentence and strips away numerics, removes ? marks and tradegov
        '''
        if lower is True:
            sentence = sentence.lower()
        sentence = striptradegov(striphtml(sentence))
        sentence = sentence.translate({ord(ch): None for ch in '0123456789'})
        return self.tokenizer.tokenize(sentence)

    def process_raw_text(self, sentence, filters=['english_stopwords', 'other_stopwords', 'jargon_stopwords']):
        '''
        This tokenises text according to process_raw_text
        filers: list of strings where string is in any of the stopwords provided
        '''
        word_tokens = self.get_tokens(sentence)

        # ToDO refactor stop_words to english_stopwords.

        # Todo add new <*_stopwords> function and have it carry to here.
        filtered_sentence = None
        for each in filters:
            if not filtered_sentence:
                filtered_sentence = word_tokens
            bf= len(filtered_sentence)
            _stopword_list = getattr(self, each)
            filtered_sentence = [w for w in filtered_sentence if not w in _stopword_list]
            print('Removed {} {}. List reduced from {} to {} non unique tokens.'.format(len(_stopword_list), each, bf,
                                                                                           len(filtered_sentence)))

        if each in ['jargon_stopwords']:
                    filtered_sentence = [w for w in filtered_sentence if len(w) > 1]

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

    def create_word_cloud(self, list_of_documents, notebook, figurepath, stopwords=None, lower=True):

        _stopwords = stopwords # List or None
        words_flat_list = [item for document in list_of_documents for item in document]
        wordcloud = WordCloud(
            background_color='white', max_words=300,
            width=1920, height=1080, color_func=self.random_color_func,
            stopwords=_stopwords
        ).generate(' '.join(words_flat_list))
        #fig = plt.figure(figsize=(80, 80))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        if notebook:
            plt.show()
        else:
            print("Word cloud saved to file: {}".format(figurepath))
            plt.savefig(figurepath)
        plt.close()

    def make_visual(self, text_string, notebook=True, figurepath='wordcloud.pdf', return_tokens=False):
        ptext = self.process_raw_text(text_string)# stopwords are removed here!
        self.create_word_cloud([[p.lower() for p in ptext]], notebook, figurepath, stopwords=[])
        if return_tokens:
            return ptext

def create():
    return Dit_wordcloud()

if __name__ in "__main__":

    wc = create()
    # Add default english stopwords
    wc.add_stopwords()

    test = "ugal as opposed to UK, due to risk of no-deal EU Exit.See email text from Company pasted in above.Lower tariffs via likely new free trade agreement with the USA will help company look at UK suppliers for furnitureVery positive on the Industrial Strategy in general - in particular how it successfully developped offshore wind int he UK in a short time.See notesThere is considerable nervousness in the company regarding Brexit and I provided as much practical support information as possible given the uncertainty of the situationHe supports the UK's objective of leaving the EU.EU Exit mentioned - what will happen going forward to export support. Gave reassurance that this will continue in my opinionAdam noted that in his experiance the UK is unique in offering the level of access that the meeting demonstrated.See multiple bullet points in client call notes above.See email chain for detail on policy feedback and client dissatisfactionSee notes aboveVery positive about speed of responsiveness a"
    word_tokens = wc.get_tokens(test)
    ptext = wc.process_raw_text(test)
    print(ptext)
    wc.make_visual(test)
    print(ptext)
