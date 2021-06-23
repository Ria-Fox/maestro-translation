import math
import numpy as np

def code2note(nstr):
    # 음계 코드 하나를 노트로 변환
    notenames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    if nstr == '':
        return -1
    note = notenames.index(nstr[0:-1])
    return note + 12 * int(nstr[-1])

def note2str(note):
    # 노트 하나를 받아서 음계 코드로 변환
    oct = int(note / 12)
    n = (note % 12)
    notenames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    if note < 0:
        return ''
    return notenames[n]+str(oct)

class Note(): # 노트 : 숫자로 쓰인 음계, 음계 코드 : C#과 같은 음계 코드
    def __init__(self, bpm=120):
        self.notes = []
        self.bpm = bpm
        self.stair = math.pow(2, 1/12)
        self.notefreq = None
        self.notedata = None

    def note2freq(self, note):
        # 노트 하나를 받아서 frequency로 변환
        if note < 0:
            return 0.0
        return 440 * math.pow(self.stair, note-57)

    def setNotefreq(self): # 노트로 쓰인 곡을 받아서 freq의 배열로 변환
        song = []
        for x in self.notes:
            if type(x) is list:
                song.append([self.note2freq(xx) for xx in x])
            else:
                song.append(self.note2freq(x))
        print(song)
        self.notefreq = song

    def getNotesheet(self):
        # 노트를 음계 코드 형식으로 반환
        sheet = ""
        for n in self.notes:
            sheet = sheet + note2str(n) + '-'
        return sheet[0:-1]

    def setNotesfromcode(self, codes):
        # 음계 코드로 쓰인 곡을 받아서 노트, freq, data 형식으로 저장
        self.notes = []
        c = codes.split('-')
        for code in c:
            if '+' in code:
                self.notes.append([code2note(c) for c in code.split('+')])
            else:
                self.notes.append(code2note(code))

        self.setNotefreq()

    def xyloSound(freq, t):
        w = 2 * np.pi * freq
        y = 0.6*np.sin(1*w*t) * np.exp(-0.0015*w*t)
        y += 0.4*np.sin(2*w*t) * np.exp(-0.0015*w*t)
        return 0.5 * y

    def pianoSound(freq, t):
        y = Note.xyloSound(freq, t)
        y += y*y*y
        y *= 1 + 16*t*np.exp(-6*t)
        return y

    def ppSound(freq, t):
        Y = np.sin(2 * np.pi * freq * t) * np.exp(-0.0004 * 2 * np.pi * freq * t)
        Y += np.sin(2 * 2 * np.pi * freq * t) * np.exp(-0.0004 * 2 * np.pi * freq * t) / 2
        Y += np.sin(3 * 2 * np.pi * freq * t) * np.exp(-0.0004 * 2 * np.pi * freq * t) / 4
        Y += np.sin(4 * 2 * np.pi * freq * t) * np.exp(-0.0004 * 2 * np.pi * freq * t) / 8
        Y += np.sin(5 * 2 * np.pi * freq * t) * np.exp(-0.0004 * 2 * np.pi * freq * t) / 16
        Y += np.sin(6 * 2 * np.pi * freq * t) * np.exp(-0.0004 * 2 * np.pi * freq * t) / 32
        Y += Y * Y * Y
        Y *= 1 + 16 * t * np.exp(-6 * t)
        return 0.02 * Y

    def getWave(self, freq, inst=xyloSound):
        amplitude = 0.5
        duration = 60.0 / self.bpm
        t = np.linspace(0, duration, int(44100 * duration))
        wave = inst(freq, t)
        return wave

    def getSongdata(self, inst=xyloSound):
        results = []
        for freq in self.notefreq:
            if type(freq) is list:
                results.append(np.array(sum([self.getWave(f, inst=inst) for f in freq])))
            else:
                results.append(self.getWave(freq, inst=inst))
        return np.concatenate(results)
