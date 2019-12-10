'''
Author: cs88882
Charlotte Szostek

I am copying the pattern of tests.io and not using a test package.
This is in effect more of a dev script for the libraries being created.

'''
# TODO ? remove one level once see packaing results.

from datatools.analysis import dit_wordcloud as wc

jargon_stopwords = set([
    'a', 'bunch', 'of', 'words', 'any', 'with', 'only', '1', 'characters', 'will', 'be', 'disguarded'
])

people_stopwords = set([
    'alice', 'rabbit'
])


if __name__ in "__main__":

    cloud = wc.create()
