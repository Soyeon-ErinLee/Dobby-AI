#!/usr/bin/python --> 이거 민찬이가 환경에 적합한 형태로 변경해주세요
# -*- coding: utf-8 -*-

# Written by Ju Yeon Lee. justforher12344@gmail.com
# Co-worker: Min Chan Kim.

import pandas as pd
import json
import urllib
import sys
import warnings
warnings.filterwarnings("ignore")
from _transriber import TRANSCRIBER

class STT_TRANSFORMER(object):

    def __init__(self, stream, filename, num_speaker):
        assert type(json) is str, print('json path must be str.')

        self.filename = filename
        self.data = TRANSCRIBER(filename).transcribe(num_speaker) ### 이부분 민찬 확인 부탁
        self.level1 = self._extraction()[0]
        self.info = self._extraction()[1]

    def _html_tagger(self, string, tag):

        assert type(string) is str, print("text input must be string.")
        assert type(string) is str, print("tag input must be string.")

        ''' 

        tag information
        --------------------------------------------------------
        1. start : we add "<strong>" at the front part of input, which contains start time and speaker information
        2. middle : we add "</strong><br>" at the front part of the input, which is usually real script.
        3. end : we add "<br><br>" at the last part of the input, which is usually real script.

        '''

        if tag == 'start':
            new_string = "<strong>" + string
            return new_string

        elif tag == 'middle':
            new_string = "</strong><br>" + string
            return new_string

        elif tag == 'end':
            new_string = string + " <br><br>"
            return new_string

        else:
            print("there is no such {} tag").format(tag)


    def _extraction(self):

        level0 = list(self.data.values())
        level1 = list(level0[2].values())

        information = dict()
        information['full_transcript'] = list(level1[0][0].values())[0]
        information['speaker_num'] = level1[1]['speakers']

        return level1, information


    def _segmentation(self):

        level1 = self.level1
        level2 = level1[1]
        level3 = level2['segments']

        df = pd.DataFrame()
        for script in level3:
            s = script['start_time']
            e = script['end_time']
            l = script['speaker_label']
            print(s, e, l)
            df = df.append([(l, s, e)], ignore_index=False)
        df.columns = ['speaker', 'start_time', 'end_time']

        return df


    def parsing(self):

        base_df = self._segmentation()
        level1 = self.level1
        level2 = level1[2]
        df = pd.DataFrame(level2)

        num_list = pd.merge(df[['start_time', 'alternatives', 'type']].reset_index().fillna('P'), base_df,\
                            on='start_time', how='outer').dropna()['index'].values

        num_list = list(num_list)
        num_list.append(len(df))
        script_list = []

        for i in range(len(num_list) - 1):
            start_row = num_list[i]
            next_row = num_list[i + 1]
            print(start_row, next_row)
            string = ''

            for script in range(start_row, next_row):
                content = df.iloc[script, 2][0]['content']

                if script == start_row:
                    string = string + content

                else:
                    if df.iloc[script, -1] == 'pronunciation':
                        string = string + ' ' + content

                    elif df.iloc[script, -1] == 'punctuation':
                        string = string + content

            script_list.append(string)

        final_df = pd.concat([base_df.reset_index().iloc[:, 1:], pd.DataFrame(script_list, columns=['text'])], axis=1)

        return final_df


    def html_transformer(self):

        df = self.parsing()
        html_string = ''
        df['speaker'] = df['speaker'].apply(lambda x: int(x.split('_')[1])+1)

        for i in range(len(df)):
            speaker_temp = 'Speaker ' + str(df.iloc[i, 0])
            start_time_temp = (df.iloc[i, 1])//60 + ':' + (df.iloc[i, 1])%60 # 분단위 데이터 확인 후 코드 수정 예정
            text_temp = df.iloc[i, -1]
            print(speaker_temp, start_time, text_temp)

            speaker = self._html_tagger(speaker_temp, 'start')
            text = self._html_tagger(text_temp, 'middle')
            text = self._html_tagger(text, 'end')

            new_string = speaker + ' ' + start_time + ' ' + text
            html_string += new_string

        return html_string

    # 각 자료를 파일로 저장하여 AWS 클라우드로 연결하는 file_connector 모듈 따로 제작 예정


    def model_transformer(self):



        df = self.parsing()

        return


    def file_export(self):

        # text 파일이나 excel 등으로 볼 수 있게 내보내는 과정

        return
