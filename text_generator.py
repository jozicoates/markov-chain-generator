'''
Markov Chain Text Generator

Markov chains describe a sequence of possible events. They can be used to predict the next word in a sentence.
Created a Markov chain to generate text, given a text file.
'''

import numpy as np
from collections import Counter

#output file
out = open("output.txt", "w")

#read input from file
filename = 'speeches.txt'
words = open(filename, encoding='utf-8').read().split()

#add word and next word to list
word_pairs = []
for i in range(len(words)-1):
    word_pairs.append((words[i].lower(), words[i+1].lower()))




def predict_next_state(word:str, data:list=word_pairs):
    #create list of every word following input word (duplicates allowed)
    next_possible_words = [w for w in word_pairs if w[0] == word]

    #count num of times each word appears
    count_appearence = dict(Counter(next_possible_words))

    #find probability of each word appearing
    for i in count_appearence.keys():
        count_appearence[i] = count_appearence[i]/len(next_possible_words)
    probabilities = list(count_appearence.values())
    
    #unique list of all options for next word
    options = [k[1] for k in count_appearence.keys()]

    #return next word (random)
    return np.random.choice(options, p=probabilities)



def generate_sequence(word:str=None, data:list=word_pairs, length:int=200):
    sequence = []
    for i in range(length):
        sequence.append(predict_next_state(word, word_pairs))
        word = sequence[-1] #use last word in sequence to predict next word
    return sequence


#write to file
counter = 0
start_state = 'america'
out.write(start_state)
out.write(" ")

for item in generate_sequence(start_state):
    counter += 1
    out.write(item)
    out.write(" ")
    
    if counter % 10 == 0: #spacing for readability
        out.write("\n")
    if counter % 100 == 0:
        out.write("\n")



out.close()
