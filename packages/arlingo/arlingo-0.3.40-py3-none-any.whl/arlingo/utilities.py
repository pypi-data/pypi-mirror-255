import requests
from bs4 import BeautifulSoup
from easygoogletranslate import EasyGoogleTranslate
from pydub import AudioSegment
from gtts import gTTS
from io import BytesIO
import time
import clipboard
import string


class Conjugator:
    
    def __init__(self):
        pass
    
    def retrieve_page(self):
        self.page = requests.get(f"https://dic.b-amooz.com/{self.lang}/dictionary/conjugation/v?verb={self.verb}")
        self.page = BeautifulSoup(self.page.content, 'html.parser')
        self.conjugation_tables = self.page.find_all('table', class_='conjugation-table')
        
    def get_conjugation(self, verb, tense='present', lang='fr'):
        self.verb = verb[:]
        self.tense = tense
        self.lang = lang
        self.retrieve_page()
        if self.lang in ['fr', 'de']:
            if self.tense == 'present':
                self.conjugations_object = self.conjugation_tables[0]
            else:
                raise NotImplementedError("Only present tense is supported at the moment.")
            pronouns = [span.text.strip() for span in self.conjugations_object.find_all('span')][0::2]
            verbs = [span.text.strip() for span in self.conjugations_object.find_all('span')][1::2]
            conjugation_lst = [pronoun + " " + verb for pronoun, verb in zip(pronouns, verbs)]
            self.pronouns = pronouns
            self.verbs = verbs
            return conjugation_lst
        else:
            raise NotImplementedError("Only French and German are supported at the moment.")


class WordExplorer:
    
    def __init__(self):
        pass
    
    def explore(self, word, lang='fr'):
        self.word = word
        self.lang = lang
        page = requests.get(f"https://dic.b-amooz.com/{self.lang}/dictionary/w?word={self.word}")
        page = BeautifulSoup(page.content, 'html.parser')
        try:
            self.part_of_speech = page.find_all('span', class_='part-of-speech')[0].text.replace('[','').replace(']','').strip()
            if self.part_of_speech == 'اسم':
                target_divider = page.find_all('div', class_='attr-noun')[0]
                features_span = target_divider.find_all('span')
                features = [span.text.strip() for span in features_span]
                self.gender = 'خنثی' if 'خنثی' in features else ('مذکر' if 'مذکر' in features else 'مونث')
            else:
                self.gender = None
        except:
            self.part_of_speech = ' '
            self.gender = ' '
        
        

class Translator:
    
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.translator = EasyGoogleTranslate(source_language=self.source, target_language=self.target, timeout=100)
    
    def translate(self, phrase, translated=None, get_audio=False, filepath = None):
        '''
        - translated: if you already have the translation, you can pass it here. Helps when google translate fails to give a correct translation.
        '''
        if translated == None:
            self.translated = self.translator.translate(phrase.strip())
        else:
            self.translated = translated
        if get_audio != False:
            if (get_audio=='source' and self.source == 'fa') or (get_audio=='target' and self.target=='fa') or (get_audio=='both' and (self.source=='fa' or self.target=='fa')):
                raise ValueError("Generating Persian speech is not currently supported")
            if filepath == None:
                raise ValueError("Please provide a filepath.")
            if get_audio == 'source' or get_audio == 'both':
                source_audio = gTTS(text=phrase, lang=self.source)
                source_tmp_file = BytesIO()
                source_audio.write_to_fp(source_tmp_file)
                source_tmp_file.seek(0)
                self.source_audio_segment = AudioSegment.from_mp3(source_tmp_file)
            if get_audio == 'target' or get_audio == 'both':
                target_audio = gTTS(text=self.translated, lang=self.target)
                target_tmp_file = BytesIO()
                target_audio.write_to_fp(target_tmp_file)
                target_tmp_file.seek(0)
                self.target_audio_segment = AudioSegment.from_mp3(target_tmp_file)
            
            output_audio = AudioSegment.silent(duration=1)
            
            if get_audio == 'both':
                output_audio += self.source_audio_segment
                output_audio += AudioSegment.silent(duration=1500)
                output_audio += self.target_audio_segment
            elif get_audio == 'source':
                output_audio += self.source_audio_segment
            elif get_audio == 'target':
                output_audio += self.target_audio_segment
            
            output_audio.export(filepath, format='mp3')
            
            
            
class PhraseTranslationWriter:
    
    def __init__(self, phrases, translations, audiopaths, part_of_speechs, genders=None):
        self.phrases = phrases
        self.translations = translations
        self.audiopaths = audiopaths
        self.part_of_speechs = part_of_speechs
        self.genders = genders
        
    def write(self, output_type='markdown'):
        if output_type not in ['markdown', 'telegram']:
            raise ValueError("output type must be either 'markdown' or 'telegram'")
        
        output = ''
        output += '|--|--|--|--|--|\n'
        output += '| کلمه/عبارت | ترجمه | نقش | جنسیت | تلفظ |\n'
        output += '|--|--|--|--|--|\n'
        if output_type == 'markdown':
            for phrase, translated, part_of_speech, gender, filepath in zip(self.phrases, self.translations, self.part_of_speechs, self.genders, self.audiopaths):
                gender = gender if gender is not None else ' '
                output += '| ' + phrase + ' | ' + translated + ' | ' + part_of_speech + ' | ' + gender + ' | ' + f'<audio controls><source src="{filepath}" type="audio/mpeg"></audio>' + ' |' + '\n'
        
            
        elif output_type == 'telegram':
            for phrase, translated, part_of_speech, gender in zip(self.phrases, self.translations, self.part_of_speechs, self.genders):
                gender = gender if gender is not None else ' '
                output += '| ' + phrase + ' | ' + translated + ' | ' + part_of_speech + ' | ' + gender + ' | ' + '\n'
        
        return output
    
    
class VerbConjugationWriter:
    
    def __init__(self, verb, meaning, pronouns, verbs, audiopaths):
        self.verb = verb[:]
        self.meaning = meaning
        self.pronouns = pronouns
        self.verbs = verbs
        self.audiopaths = audiopaths
        
    def write(self, output_type='markdown'):
        if output_type not in ['markdown', 'telegram']:
            raise ValueError("output type must be either 'markdown' or 'telegram'")
        
        output = ''
        if output_type == 'markdown':
            output += '## فعل ' + self.verb + ' (' + self.meaning + ')' + '\n\n'    
            output += '|--|--|--|' + '\n'
            output += '| ضمیر | فعل | تلفظ |' + '\n'
            output += '|--|--|--|' + '\n'
            for pronoun, verb, audiopath in zip(self.pronouns, self.verbs, self.audiopaths):
                output += '| ' + pronoun + ' | ' + verb + ' | ' + f'<audio controls><source src="{audiopath}" type="audio/mpeg"></audio>' + ' |' + '\n'
        elif output_type == 'telegram':
            output += 'فعل ' + self.verb + ' (' + self.meaning + ')' + '\n\n'
            for pronoun, verb, audiopath in zip(self.pronouns, self.verbs, self.audiopaths):
                output += pronoun + ' | ' + verb + ' | '  + '\n'
        
        return output


def get_conjugation_output(verb, output_type='markdown', save_root_path='', github_root_path='', translated=None, lang='fr'):
    conjugator = Conjugator()
    _ = conjugator.get_conjugation(verb=verb, lang='fr')
    filepaths = []

    for pronoun, curr_verb in zip(conjugator.pronouns, conjugator.verbs):
        pronoun = pronoun.split('/')[0] if '/' in pronoun else pronoun
        text_for_speech = pronoun + ' ' + curr_verb
        base_filepath = str(time.time()).replace('.','P') + '-' + text_for_speech.translate(str.maketrans('', '', string.punctuation)).replace(' ','').lower() + '.mp3'
        save_filepath = save_root_path + base_filepath
        github_filepath = github_root_path + base_filepath
        filepaths.append(github_filepath)
        tr = Translator(source=lang, target='fa')
        tr.translate(text_for_speech, get_audio='source', filepath=save_filepath)
        
    translated = translated if translated is not None else tr.translated
    writer = VerbConjugationWriter(verb, translated, conjugator.pronouns, conjugator.verbs, filepaths)
    clipboard.copy(writer.write(output_type))


def get_phrase_translation_output(phrases, given_translations=[], source='fr', target='fa', save_root_path='', github_root_path='', output_type='markdown'):
    translator = Translator(source=source, target=target)
    filepaths = []
    part_of_speechs = []
    translations = []
    genders = []
    explorer = WordExplorer()
    for phrase, given_translation in zip(phrases, given_translations):
        base_filepath = str(time.time()).replace('.','P') + '-' + phrase.translate(str.maketrans('', '', string.punctuation)).replace(' ','').lower() + '.mp3'
        save_filepath = save_root_path + base_filepath
        github_filepath = github_root_path + base_filepath
        translator.translate(phrase, get_audio='source', filepath=save_filepath)
        filepaths.append(github_filepath)
        if len(given_translation.strip()) == 0:
            translations.append(translator.translated)
        else:
            translations.append(given_translation)
        is_word = True if len(phrase.strip().split())==1 else False
        if is_word == True:
            explorer.explore(phrase, source)
            part_of_speechs.append(explorer.part_of_speech)
            genders.append(explorer.gender)
        else:
            part_of_speechs.append(' ')
            genders.append(' ')
            
    writer = PhraseTranslationWriter(phrases, translations, filepaths, part_of_speechs, genders)
    clipboard.copy(writer.write(output_type))