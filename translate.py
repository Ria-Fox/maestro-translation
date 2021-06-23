import re
import os
from note import code2note, note2str, Note
from scipy.io.wavfile import write

from flask_restx import Namespace, Resource, reqparse
from flask import send_file, after_this_request

import subprocess

api = Namespace('Translator', description='번역 API', path='/translate')

parser = reqparse.RequestParser()
parser.add_argument('sentence', type=str, required=True, help='번역할 문장(한글 only)')
parser.add_argument('base_key', type=str, default='C4', help='기준 음역대, 기본 C4')
parser.add_argument('speed', type=int, default=240, help='말하는 속도, 기본 240BPM')

BASE_CODE, CHOSUNG, JUNGSUNG = 44032, 588, 28
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

def convert_syllable(syllable):
    result = list()
    # 한글 여부 check 후 분리
    if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', syllable) is not None:
        char_code = ord(syllable) - BASE_CODE
        char1 = int(char_code / CHOSUNG)
        result.append(char1)
        char2 = int((char_code - (CHOSUNG * char1)) / JUNGSUNG)
        result.append(char2)
        char3 = int((char_code - (CHOSUNG * char1) - (JUNGSUNG * char2)))
        if char3 is not 0:
            result.append(char3)
        return result
    else:
        return 0

# def translate(str, stdnote='C4'):
#     # 기본적으로 한글 음절을 변환하는 것을 가정, 영어는 모두 제외
#     split = []
#     for c in str:
#         if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', str) is None:
#             continue
#         split.append(convert(c))
#     result1 = ""
#     result2 = ""
#     stdcode = code2note(stdnote)
#     for c in split:
#         result1 += note2str(stdcode + c[0]) + '--'
#         result2 += '-' + note2str(stdcode + c[1]) + '-'
#         if len(c) > 2:
#             result1 += note2str(stdcode + c[2])+'-'
#             result2 += '-'
#         result1 += '-'
#         result2 += '-'
#     return result1, result2

def translate(str, stdnote='C4'):
    # 기본적으로 한글 음절을 변환하는 것을 가정, 영어는 모두 제외
    # result1은 자음 악기용, 2는 모음 악기용
    # 초중성 화음 + 종성
    split = []
    for c in str:
        if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', str) is None:
            continue
        split.append(convert_syllable(c))
    result1 = ""
    result2 = ""
    stdcode = code2note(stdnote)
    for c in split:
        if not c:
            result1 += '-'
            result2 += '-'
            continue
        result1 += note2str(stdcode + c[0]) + '-'
        result2 += note2str(stdcode + c[1]) + '-'
        if len(c) > 2:
            result1 += note2str(stdcode + c[2])+'-'
            result2 += '-'
        result1 += '-'
        result2 += '-'
    return result1, result2

# def translate3(str, stdnote='C4'):
#     # 기본적으로 한글 음절을 변환하는 것을 가정, 영어는 모두 제외
#     split = []
#     for c in str:
#         if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', str) is None:
#             continue
#         split.append(convert(c))
#     print(split)
#     result1 = ""
#     result2 = ""
#     stdcode = code2note(stdnote)
#     for c in split:
#         print(c[0])
#         result1 += note2str(stdcode + c[0])
#         result2 += '-' + note2str(stdcode + c[1])
#         if len(c) > 2:
#             if c[0] != c[2]:
#                 result1 += '+' + note2str(stdcode + c[2])
#             else:
#                 result1 += '--' + note2str(stdcode + c[2])
#                 result2 += '-'
#
#         result1 += '---'
#         result2 += '--'
#     return result1, result2

@api.route('')
class TranslateResource(Resource):
    @api.expect(parser)
    def get(self):
        args = parser.parse_args()
        sentence = args.sentence
        base_key = args.base_key
        speed = args.speed

        inst1 = Note(speed)
        inst2 = Note(speed)
        consonant, vowel = translate(sentence, stdnote=base_key)
        sentence = sentence.replace(' ', '')
        filepath = sentence[:6] + '.wav'
        inst1.setNotesfromcode(consonant)
        inst2.setNotesfromcode(vowel)
        data = inst1.getSongdata(inst=Note.ppSound) + inst2.getSongdata(inst=Note.xyloSound)
        write(filepath, 44100, data)
        try:
            os.remove(os.getcwd() + "\\" + sentence[:6]+'.mp3')
        except:
            print("No file to delete")
        cmd = 'ffmpeg -i {} -vn -ar 44100 -ac 2 -b:a 192k {}'.format(filepath, sentence[:6]+'.mp3')
        subprocess.call(cmd, shell=True)
        filepath = sentence[:6]+'.mp3'

        @after_this_request
        def remove_file(response):
            for path, dirname, filename in os.walk(os.getcwd()):
                for file in filename:
                    if file.split('.')[1] in ["wav", "mp3"]:
                        try:
                            os.remove(path + "\\" + file)
                        except Exception as e:
                            print("Delete {} failed".format(file))
            return response

        return send_file(filepath, mimetype="audio/mp3", as_attachment=True, attachment_filename=filepath)