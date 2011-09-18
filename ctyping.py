#!/usr/bin/python

import os
import re
import sys
import urllib
import curses
import codecs
import unicodedata

class Settings(object):
    def __init__(self, parent=None, name=None):
        if parent: setattr(parent, name, self)
    def __getattr__(self, name):
        return Settings(self, name)

settings = Settings()
settings.tables = [u"cj.cin"]
#settings.tts_url = u"http://translate.google.com/translate_a/t?client=t&sl=auto&text="
settings.tts_url = u"http://translate.google.com/translate_tts?tl=zh&q="
settings.tts_cmd = u"wget -U 'Mozilla/5.0' '" + settings.tts_url + u"%s' -O '%s'"
settings.play_cmd = u"mplayer '%s'"

def update_cache():
    pass # XXX check cache dir size or number of files, perform LRU

def tts(s):
    q = urllib.quote(s.encode('utf8'))
    mp3 = u"cache/%s.mp3" % q
    if os.path.exists(mp3):
        os.system(u"touch '%s'" % (mp3,))
    else:
        os.system(settings.tts_cmd % (q, mp3))
    os.system(settings.play_cmd % (mp3,))
    update_cache()

def load_table():
    table = {}
    pat = re.compile('(\S+)\s+(\S+)')
    for t in settings.tables:
        f = codecs.open(t, encoding='utf8')
        for line in f:
            if line.startswith(u'#') or line.startswith(u'%'):
                continue
            key, word = pat.match(line).group(1, 2)
            if word not in table:
                table[word] = []
            table[word].append(key)
        f.close()
    return table

def proc_sentence(sent, table):
    words = []
    for word in sent:
        if word in table:
            words.append(table[word][0])
        else:
            words.append(word)
    ans = u' '.join(words)
    while 1:
        tts(sent)
        print sent
        print ans
        ret = raw_input()
        if ret == ans:
            break
        if ret == 'skip':
            return

def proc_text(text, table):
    i = 0
    while 1:
        while i < len(text) and unicodedata.category(text[i])[0] not in 'LN':
            i += 1
        if i == len(text):
            break
        j = i
        while j < len(text) and unicodedata.category(text[j])[0] in 'LN':
            j += 1
        sent = "".join(text[i:j])
        proc_sentence(sent, table)
        i = j

if __name__ == '__main__':
    table = load_table()
    #tts(u'\u79d1'*3)
    f = codecs.open('test.txt', encoding='utf8')
    proc_text(f.read(), table)
    f.close()

# vim: ts=8 et sw=4 sts=4 aw
