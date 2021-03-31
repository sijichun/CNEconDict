#!/usr/bin/python3

from os import listdir

sub_path = "./sub_dics/"
dict_file = "./Econ_Dict.txt"
words = []
for fn in listdir(sub_path):
    if fn[-4:] == ".txt":
        with open(sub_path + fn, 'r') as f:
            content = f.readlines()
            content = list(set(content))
            words.extend(content)
        with open(dict_file, 'r') as f:
            content = f.readlines()
            content = list(set(content))
            words.extend(content)
        words.sort()
        with open(dict_file, 'w') as f:
            for w in words:
                f.write(w.strip() + '\n')
