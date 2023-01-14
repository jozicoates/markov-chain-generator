import music21
from collections import Counter
import numpy as np
from difflib import SequenceMatcher


music21.environment.set('musescoreDirectPNGPath', 'C:\\Program Files\\MuseScore 3\\bin\\MuseScore3.exe')
noteList = []
durationList = []

bach = ['bach/bwv3.6', 'bach/bwv1.6', 'bach/bwv2.6']
beethoven = ['beethoven/opus18no3', 'beethoven/opus18no4']
mozart = ['mozart/k458/movement1','mozart/k458/movement2','mozart/k458/movement3']

#Get sequence of notes and durations from original composition streams
for i in bach:
	s = music21.corpus.parse(i)
	s = s.parts[0]
	print(s.analyze('key'))
	searcher = music21.search.serial.ContiguousSegmentSearcher(s, reps='skipConsecutive', includeChords=False).byLength(1)
	instanceList = [instance.segment for instance in searcher]
	for note in instanceList:
		noteList.append(note[0].pitch)
		durationList.append(note[0].duration.type)
fp = s.write('midi', fp='originalscore')


#Get random notes and durations
uniqueNotes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
uniqueNotes2 = []
for i in uniqueNotes:
	uniqueNotes2.append(i)
	uniqueNotes2.append(''.join((i, '-')))
	uniqueNotes2.append(''.join((i, '#')))
uniquePitches = []
for i in uniqueNotes2:
	for j in range(1,7):
		uniquePitches.append(''.join((i, str(j))))
uniqueDurations = list(set(durationList))


#Create a dictionary with durations of the first notes in a sequence
merged_list = [(noteList[i], noteList[i+1], noteList[i+2], durationList[i]) for i in range(len(noteList)-2)]
durationDict = {}
for k in merged_list:
	if k not in durationDict:
		durationDict[k] = 1
	else:
		durationDict[k] += 1

#Create a list of sequenes of 3 notes
pitch_pairs = []
for i in range(len(noteList)-2):
    pitch_pairs.append((noteList[i], noteList[i+1], noteList[i+2]))



'''Markov Functions'''

def predict_next_pitch(pitch1:str, pitch2:str, data:list=pitch_pairs):
	'''Generates the next pitch randomly, given the previous two pitches'''
	next_possible_pitches = [p for p in data if p[0] == pitch1 and p[1] == pitch2]
	count_appearence = dict(Counter(next_possible_pitches))
	for i in count_appearence.keys():
		count_appearence[i] = count_appearence[i]/len(next_possible_pitches)
	probabilities = list(count_appearence.values())
	options = [k[2] for k in count_appearence.keys()]
	return np.random.choice(options, p=probabilities)

def predict_duration(pitch:str, data:dict=durationDict):
	'''Generates the duration of a single note, given a pitch'''
	possible_durations = [d for d in data if d[0] == pitch]
	count_appearence = dict(Counter(possible_durations))
	for i in count_appearence.keys():
		count_appearence[i] = count_appearence[i]/len(possible_durations)
	probabilities = list(count_appearence.values())
	options = [k[3] for k in count_appearence.keys()]
	return np.random.choice(options, p=probabilities)


def generate_sequence(pitch1:str, pitch2:str, data:list=pitch_pairs, length:int=100):
	'''Generates a sequence of pitches, given two starting states'''
	sequence = []
	sequence.append(pitch1)
	sequence.append(pitch2)
	for i in range(length):
		sequence.append(predict_next_pitch(pitch1, pitch2, pitch_pairs))
		pitch1 = sequence[-2] #use second to last word in sequence to predict next word
		pitch2 = sequence[-1] #use last word in sequence to predict next word	
	return sequence


'''Random Functions'''

def generate_random_sequence(length:int=100):
	'''Generates a random sequence given a list of pitches'''
	sequence = []
	for i in range(length):
		sequence.append(np.random.choice(uniquePitches))
	return sequence

def random_duration():
	'''Generates a random duration of a note'''
	return np.random.choice(uniqueDurations)





#Input starting states
starting_pitch = [p[0] for p in pitch_pairs]
x = input("Starting pitch? ")
next_possible_pitch = [p[1] for p in pitch_pairs if p[0]==music21.pitch.Pitch(x)]
while len(next_possible_pitch) == 0:
	x = input("Not found. Starting pitch? ")
	next_possible_pitch = [p[1] for p in pitch_pairs if p[0]==music21.pitch.Pitch(x)]
print("Next possible pitches are: ", set(next_possible_pitch))
y = input("Next pitch? ")


#Generate Markov sequence and append to score
start_state1 = music21.pitch.Pitch(x)
start_state2 = music21.pitch.Pitch(y)
item = generate_sequence(start_state1, start_state2)

score = music21.stream.Score()
for i in item:
	n = music21.note.Note(i, type=predict_duration(i))
	score.append(n)
score.show()
fp1 = score.write('midi', fp='markovscore')


#Generate random sequence and append to score
randomscore = music21.stream.Score()
item2 = generate_random_sequence()
for i in item2:
	n = music21.note.Note(i, type=random_duration())
	randomscore.append(n)

randomscore.show()
fp = randomscore.write('midi', fp='randomscore')


#Calculate similarity between scores
with open("markovscore", 'r', encoding='latin-1') as f:
	content = f.read()
with open("originalscore", "r", encoding='latin-1') as f2:
	content2 = f2.read()
with open("randomscore", 'r', encoding='latin-1') as f3:
	content3 = f3.read()

m = SequenceMatcher(None, content, content2)
print("Original score's similarity with Markov-generated score:", m.ratio())

m2 = SequenceMatcher(None, content3, content2)
print("Original score's similarity with random score:", m2.ratio())