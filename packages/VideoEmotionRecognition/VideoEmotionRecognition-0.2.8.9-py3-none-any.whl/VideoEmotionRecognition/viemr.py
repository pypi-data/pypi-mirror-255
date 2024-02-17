"""
Here is the main class that makes this module, VideoEmotionRecognition
"""
import pandas as pd
import numpy as np
import math
import gdown
import matplotlib.pyplot as plt
#import whisperx
import gc
import transformers
import webvtt
import os
import ffmpeg
import random
import logging
import torch
import torch.nn as nn
import torch.nn.functional as F
from moviepy.editor import *
import torchaudio
from sklearn.neighbors import kneighbors_graph
import networkx as nx
import cv2
import glob
import re
from sentence_transformers import SentenceTransformer
from deepface import DeepFace
#from src.models import Wav2Vec2ForSpeechClassification, HubertForSpeechClassification
from transformers import AutoConfig, Wav2Vec2FeatureExtractor
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from transformers import RobertaTokenizerFast, BertForSequenceClassification
class VideoEmotionRecognition:
    def __init__(self, mp4):

        logging.basicConfig(filename="newfile.log",
        format='%(asctime)s %(message)s',filemode='w')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        self.logger.info("Initializing the class")

        self.dataframe = -1
        self.mp4 = mp4

        self.logger.info("Loading the arousal_valence map")

        url1 = 'https://drive.google.com/uc?id=1yJBHU8Zl4MuoQfJqkPgVDwJfYRJDPUAH'
        output = 'emotions_coord.xlsx'
        gdown.download(url1, output, quiet=False)
        self.emotions_coord = pd.read_excel(output)

        self.logger.info("Successfully initialized")
    """
    add_emotions
    ---------------
    """
    def add_emotions(self, new_emotions):
        """
          Use this to add the arousal and valence of a new emotion by passing a series or a dataframe with it's name, x coordinate
          and y coordinate in this order. Useful when changing the model so that the emotions classified by this model are recognized.

          Args:
            **new_emotions (pandas series/dataframe)**: new emotion to be added with it's name, arousal and valence coordinates values.

          Return:
            Nothing.

        """
        self.emotions_coords = pd.concat([self.emotions_coords,new_emotions])
        self.emotions_coords.reset_index(inplace=True, drop=True)
    """
    transcript
    ----------
    """
    def transcript(self, method = "whisperx", min_time = 1):
        """
          One of the main functions of this module. It's responsible for transforming the audio of a video into text,
          organizing it's sentences in a dataframe with the transcription and it's time frames of start and end. 
          
          This function is used in all the modalities of classification, but doesn't need to be run manually, 
          being automatically used in each modality. 

          Args:
            **method (string)**: placeholder for future integration of new models.

            **min_time (int)**: minimun time in seconds for a sentence to be added into the dataframe. Increassing this value will discard shorter sentences

          Return:
            Nothing.

        """
        self.logger.info("Running the whisperx transcription")
        bashCommand = "whisperx --compute_type float32 --output_format vtt " + self.mp4
        os.system(bashCommand)
        self.logger.info("Successfully transcripted")

        self.logger.info("Generating the Dataframe from the vtt")
        self.set_vtt(self.mp4.replace("mp4", "vtt"))

        self.dataframe = self.dataframe[self.dataframe.apply(lambda x: __time_diff(x[1], x[0]), axis=1) > min_time]
        self.dataframe.reset_index(inplace = True, drop = True)

        self.logger.info("Successfully generated the dataframe")
    """
    text
    ----
    """
    def text(self, emot_pipe = None, encoder_text = None, redo = False):
        """
        
          One of the main functions of this module. It's responsible for classifying
          the emotions present in a clip based on the transcription of it's audio. 
          
          Can be used manually or indirectly via the emotion_recogniton(modality = "transcript") method to generate a dataframe
          with each sentence of a video transcripted with it's timestamps, the emotion that is predominant in the text of this
          sentence and the score of the emotion atributed by the model.


          Args:
            **emot_pipe (pipeline)**: pass a pipeline in order to change the model being used to classify the emotions.

            **encoder_text (encoder)**: pass the encoder used in the pipeline passed.

            **redo (bool)**: This function saves if it was already used before, avoiding repeating the repeated work if, for example,
            the multimodal classification is used but the text modality has already been done before. Setting this to True 
            will force it to repeat the work.

          Return:
            Nothing.
          
          The current implementation is based on a Roberta model trained on goemotions, but since the goemotions database is in english
          there is a pre processing of translating the text in portuguese to english with this Unicamp project https://huggingface.co/unicamp-dl/translation-pt-en-t5
          
          You can also change the model being used for the emotion recognition with the emot_pipe and encoder_text arguments, 
          although you may need to add the labels that are classified by the new model via the method add_emotions() 
          if they are not present in the self.emotions_coord dataframe


        """
        if 'text_label' in self.dataframe.columns and redo == False:
          self.logger.info("Text classification already done")
          return
        try:
          self.dataframe.size

          self.logger.info("Loading the translator")
          tokenizer_tr = AutoTokenizer.from_pretrained("unicamp-dl/translation-pt-en-t5")

          translator = AutoModelForSeq2SeqLM.from_pretrained("unicamp-dl/translation-pt-en-t5")

          pten_pipeline = pipeline('text2text-generation', model=translator, tokenizer=tokenizer_tr)

          self.logger.info("Successfully loaded, now applying")
          self.dataframe['Translation'] = list(self.dataframe[2].apply(__traduz, args = (pten_pipeline,)))

          self.logger.info("Loading the classifier")
          if emot_pipe == None:
            emot_pipe = pipeline('sentiment-analysis',
                              model="bhadresh-savani/bert-base-go-emotion",
                              return_all_scores=True)
          encoder_text = encoder_text or SentenceTransformer("bhadresh-savani/bert-base-go-emotion")

          self.logger.info("Successfully loaded, now applying")
          resp = list(self.dataframe['Translation'].apply(__emocao_provavel, args = (emot_pipe,)))
          temp = pd.DataFrame.from_records(resp, columns=['text_label', 'text_prob'])
          self.dataframe["text_embeddings"] = list(self.dataframe['Translation'].apply(__encoder_text_adj, args = (encoder_text,)))

          self.dataframe = pd.concat([self.dataframe, temp], axis=1)
          self.logger.info("Dataframe emotions classified")
        except AttributeError:
          raise ValueError("There is no transcription")
    """
    audio
    -----
    """
    def audio(self, method = "Rajaram1996/Hubert_emotion", redo = False):
        """

          One of the main functions of this module. It's responsible for classifying
          the emotions present in the sentences of a clip based on it's audio. 
          
          Can be used manually or indirectly via the emotion_recogniton(modality = "audio") method to generate a dataframe
          with each sentence of a video transcripted with it's timestamps, the emotion that is predominant in it's audio 
          segment and the score of the emotion atributed by the model.

          Args:
            **method** : placeholder for future integration of new models.
            
            **redo (bool)**: This function saves if it was already used before, avoiding repeating the repeated work if, for example,
            the multimodal classification is used but the text modality has already been done before. Setting this to True 
            will force it to repeat the work.

          Return:
            Nothing.

          The current implementation is based on a Hubert model that can be found here https://github.com/m3hrdadfi/soxan

        """
        if 'audio_label' in self.dataframe.columns and redo == False:
          self.logger.info("Audio classification already done")
          return

        model_name_or_path = method

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        config = AutoConfig.from_pretrained(model_name_or_path)
        feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name_or_path)
        sampling_rate = feature_extractor.sampling_rate


        audio_model = HubertForSpeechClassification.from_pretrained("Rajaram1996/Hubert_emotion", output_hidden_states=True).to(device)
        video = VideoFileClip(self.mp4)

        emot = []
        scor = []
        embeddings = []
        maximo = self.dataframe.shape[0]

        self.logger.info("Running the Hubert classification for each sentence")

        for i in range(0, maximo):
            #Usando os timestamps da transcricao, corto o audio separando cada frase
            startPos = self.dataframe[0][i]
            endPos = self.dataframe[1][i]

            clip = video.subclip(startPos, endPos)

            part_name = "part_"+str(i)+".mp3"
            clip.audio.write_audiofile(part_name, verbose=False)

            #Aplico o modelo
            temp = __predict(part_name,sampling_rate, device, config, feature_extractor, audio_model)
            embeddings.append(__encoder_audio(part_name,sampling_rate, device, feature_extractor, audio_model))

            max_values = max(temp, key=lambda x:x['Score'])

            # A cada frase, atribuo a emocao mais provavel e sua probabilidade
            max_emotion = (max_values['Emotion'])
            max_emotion = max_emotion[(max_emotion.find('_')+ 1):]
            if max_emotion == 'sad':
              max_emotion = 'sadness'
            elif max_emotion == 'angry':
              max_emotion = 'anger'
            elif max_emotion == 'happy':
              max_emotion = 'joy'
            emot.append(max_emotion)

            max_score = (max_values['Score'])
            scor.append(float(max_score.replace("%","",1))/ 100)

            os.remove(part_name)
            i += 1

        self.dataframe['audio_label'] = emot
        self.dataframe['audio_prob'] = scor
        self.dataframe['audio_embeddings'] = embeddings

        self.logger.info("Successfully generated the dataframe")
    """
    video
    -----
    """
    def video(self, frames = 5, redo = False):
      """
        One of the main functions of this module. It's responsible for classifying
        the emotions present in the sentences of a clip based on the facial expressions present.
        
        Can be used manually or indirectly via the emotion_recogniton(modality = "video") method to generate a dataframe
        with each sentence of a video transcripted with it's timestamps, the emotion that is predominant in the facial
        expressions present and the score of the emotion atributed by the model.

        Args:
            **frames (int)**: change the amount of frames per second going to be analized by the model. Bigger values can
            improve the classification, but drastically increasing the time of execution.

            **redo (bool)**: This function saves if it was already used before, avoiding repeating the repeated work if, for example,
            the multimodal classification is used but the text modality has already been done before. Setting this to True 
            will force it to repeat the work.

          Return:
            Nothing.

          The current implementation is based on a Deepface, which can be found here https://github.com/serengil/deepface

      """
      if 'video_label' in self.dataframe.columns and redo == False:
          self.logger.info("Video classification already done")
          return
      video = VideoFileClip(self.mp4)
      face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

      new_clip = video.set_fps(frames)
      emot = []
      scor = []
      maximo = self.dataframe.shape[0]

      for i in range(0, maximo):
          #Usando os timestamps da transcricao, corto o audio separando cada frase
          startPos = self.dataframe[0][i]
          endPos = self.dataframe[1][i]

          clip = new_clip.subclip(startPos, endPos)

          frames = clip.iter_frames()

          total = {}
          quant = 0

          for frame in frames:

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            #Se não tiver face, essa função uma tupla vazia

            if(len(faces) > 0):
              try:
                #Se não tiver face, essa função retorna uma excecao
                objs = DeepFace.analyze(frame, actions = ['emotion'])
                if(total == {}):
                  total = objs[0]['emotion']
                else:
                  for key, value in objs[0]['emotion'].items():
                    total[key] += value
                quant += 1
              except ValueError:
                continue
          for key, value in total.items():
            total[key] = value / quant
          if(quant == 0):
            emot.append("no_face")
            scor.append(0)
          else:
            max_prob = max(total.values())
            max_emo = {i for i in total if total[i] == max_prob}

            #Max emo eh um set, converto para o formato certo em str
            max_emo = str(max_emo)
            max_emo = str(max_emo[2: -2])
            max_emo

            if max_emo == 'sad':
              max_emo = 'sadness'
            elif max_emo == 'angry':
              max_emo = 'anger'
            elif max_emo == 'happy':
              max_emo = 'joy'
            emot.append(max_emo)
            scor.append(max_prob/(quant * 100))

      self.dataframe['video_label'] = emot
      self.dataframe['video_prob'] = scor
    """
    emotion_recognition
    -------------------
    """
    def emotion_recognition(self, modality, text_pipeline = None, text_encoder = None, audio_method = "Rajaram1996/Hubert_emotion", video_frames = 5, redo = False):
      """
        Main functionality that classifies the emotions present in a clip. The modality determines which aspect of the video
        will be used to classify the emotions
        
        Args:
            **modality (string)**: Choose which way you want the video to be analyzed between 4 possibilities
            * transcript: classify the emotions based on the transcription of it's audio
            * audio: classify the emotions based on it's audio
            * video: classify the emotions based on the facial expressions present
            * multimodal: classify the emotions using both the text and audio modalityes, which are integrated using a graph model.

            **text_pipe (pipeline)**: pass a pipeline in order to change the model being used to classify the emotions.

            **text_encoder (encoder)**: pass the encoder used in the pipeline passed.

            **video_frames (int)**: change the amount of frames per second going to be analized by the model. Bigger values can
            improve the classification, but drastically increasing the time of execution.

            **redo (bool)**: This function saves if it was already used before, avoiding repeating the repeated work if, for example,
            the multimodal classification is used but the text modality has already been done before. Setting this to True 
            will force it to repeat the work.

        Return:
            Nothing.

      """
      try:
        maximo = self.dataframe.shape[0]
      except AttributeError:
        self.logger.info("No transcript found, generating one first")
        self.transcript()
        maximo = self.dataframe.shape[0]

      if(modality == "transcript"):

        self.logger.info("Initialzing the transcription")
        self.text(text_pipeline,text_encoder,redo)

        self.logger.info("Ending the transcription")

      elif(modality == "audio"):

        self.logger.info("Initialzing the audio classification")
        self.audio(audio_method,redo)

        self.logger.info("Ending the audio classification")

      elif(modality == "video"):

        self.logger.info("Initialzing the video classification")
        self.video(video_frames,redo)

        self.logger.info("Ending the video classification")

      elif(modality == "multimodal"):
        self.logger.info("Initialzing the transcription")
        self.text(text_pipeline,text_encoder,redo)
        self.logger.info("Ending the transcription")

        self.logger.info("Initialzing the audio classification")
        self.audio(audio_method,redo)
        self.logger.info("Ending the audio classification")

        self.logger.info("Generating the graph")

        A_text = kneighbors_graph(np.array(self.dataframe.text_embeddings.to_list()), 2, mode='connectivity')
        G_text = nx.Graph(A_text.toarray())

        A_audio = kneighbors_graph(np.array(self.dataframe.audio_embeddings.to_list()), 2, mode='connectivity')
        G_audio = nx.Graph(A_audio.toarray())

        self.G_multimodal = nx.Graph()
        for edge in G_text.edges(): self.G_multimodal.add_edge(edge[0],edge[1])
        for edge in G_audio.edges(): self.G_multimodal.add_edge(edge[0],edge[1])

        t = []
        for index,row in self.dataframe.iterrows():
          df_coord_text = __generate_coord(row["text_label"],self.emotions_coord)
          coord_text = [float(df_coord_text[0]),float(df_coord_text[1])]
          self.G_multimodal.nodes[index]['text'] = np.array(coord_text)

          df_coord_audio = __generate_coord(row["audio_label"],self.emotions_coord)
          coord_audio = [float(df_coord_audio[0]),float(df_coord_audio[1])]
          self.G_multimodal.nodes[index]['audio'] = np.array(coord_audio)

          t.append(np.linalg.norm(self.G_multimodal.nodes[index]['audio']-self.G_multimodal.nodes[index]['text']))

        for index,row in self.dataframe.iterrows():
          self.G_multimodal.nodes[index]['pseudolabeling'] = 1.0 - (t[index]/np.max(t))

        self.logger.info("Ending the multimodal classification")

    """
    set_vtt
    -------
    """
    def set_vtt(self, file):
        """
          Alternate form to load a video dataframe via it's vtt, which can be generated previously with the whisperx transcription.

          Args:
            **file (vtt)**: path to the vtt file to be used.

        Return:
            Nothing.

        """
        self.logger.info("Loading dataframe via vtt")
        L = []

        for caption in webvtt.read(file):
            L.append([caption.start,caption.end,str(caption.text)])

        self.dataframe = pd.DataFrame(L)
        self.logger.info("Successfully loaded")
    """
    get_labels
    ----------
    """
    def get_labels(self, modality = "all"):
        """
          Return the dataframe with all sentences, classificated or not. With
          modality, you can select to show only the classification for the
          modality selected in case of multiple classifications. Doesn't work
          for multimodal since there is no classification.

          The emotions and probability assigned by the model are shon respectively int the label and prob columns.

          Args:
            **modality (string)** Choose which way you want the video to be analyzed between 4 possibilities
            * transcript: classify the emotions based on the transcription of it's audio
            * audio: classify the emotions based on it's audio
            * video: show the classified emotions based on the facial expressions present. 
            * all: If either no modality argument is passed or the all modality is used, it will show all the modalities performed 
            in it's own columns(for example, text in text_label), while the label and prob column show the results of the modality 
            that was selected the last time this method was called.

        Return:
            Nothing.

        """
        if(modality == "transcript"):
          self.dataframe["label"] = self.dataframe["text_label"]
          self.dataframe["prob"] = self.dataframe["text_prob"]
          return self.dataframe[[0,1,2,'label','prob']]
        elif(modality == "audio"):
          self.dataframe["label"] = self.dataframe["audio_label"]
          self.dataframe["prob"] = self.dataframe["audio_prob"]
          return self.dataframe[[0,1,2,'label','prob']]
        elif(modality == "video"):
          self.dataframe["label"] = self.dataframe["video_label"]
          self.dataframe["prob"] = self.dataframe["video_prob"]
          return self.dataframe[[0,1,2,'label','prob']]
        return self.dataframe
    """
    get_heatmap
    -----------
    """
    def get_heatmap(self, modality = 'all', animated = False, window = 60, stride = 10, join_video = False):
        """
          Generates a heatmap of the evolution of emotions during the video. This function should be used after 
          the emotion_recognition has been used at least once with any modality. Ithout any special flags, this method
          generates an image of a heatmap with the overall emotions of the video, but with the right flags, this image
          cn be instead a video demonstrating the evolution of the emotions with the passage of time and even integrate
          this video with the original one from which the emotions were extracted.

          Args:
            **animated (bool)** instead of a single image, generate a video showing the emotions during the timestamps,
            which can be adjusted via the window and stride parameters.

            **window (int)**: size in seconds of the window shown in the animated heatmap. Only works if animated = True. 
            This also changes the heatmap generate with join_video = True

            **stride (int)**: size in seconds of the difference between two consecutives timeframes. Only works if animated = True. 
            This also changes the heatmap generate with join_video = True

            **join_video (bool)**: create a new video with the original video and the heatmap video side by side. Only works if animated = True.

            **modality (string)** Choose which way you want the video to be analyzed between 4 possibilities
            * transcript: classify the emotions based on the transcription of it's audio
            * audio: classify the emotions based on it's audio
            * video: show the classified emotions based on the facial expressions present.
            * multimodal: classify the emotions using both the text and audio modalityes, which are integrated using a graph model. 
            * all: If either no modality argument is passed or the all modality is used, it will show all the modalities performed 
            in it's own columns(for example, text in text_label), while the label and prob column show the results of the modality 
            that was selected the last time this method was called.

        Return:
            Based on the flags, a plot of the heatmap, a video of the heatmap or a merge of the original video and the video of the heatmap.

        """

        if modality == 'multimodal':
          x = []
          y = []
          __GCP(self.G_multimodal,mi=1,audio_weight=0.4, text_weight=0.6,max_iter=30)
          for index in self.dataframe.index:
            v = self.G_multimodal.nodes[index]['f']
            if animated == True or (np.abs(v[0]) > 0.1 or np.abs(v[1]) > 0.1):
              x.append(v[0])
              y.append(v[1])
        else:
          df = self.get_labels(modality)

          self.logger.info("Adding the arousal valence coordinates")
          df.loc[df['label'] == 'no_face', ['label']] = 'neutral'
          resp = list(df['label'].apply(__generate_coord, args = (self.emotions_coord,)))
          temp = pd.DataFrame.from_records(resp, columns=['x', 'y'])

          df = pd.concat([df, temp], axis=1)
          if animated == False:
              df = df[df.label!='neutral']
              df = df.reset_index(drop=True)

          array_x = df['x'].to_numpy()
          x = array_x.tolist()
          array_y = df['y'].to_numpy()
          y = array_y.tolist()

        if animated == True:
            self.logger.info("Generating images for the video")
            os.mkdir("tempjpgs")
            clip = VideoFileClip(self.mp4)

            maximo = clip.duration
            ini = 0
            fim = window
            atual = 1

            while(1):
                id_ini = np.where(self.dataframe[0].apply(__to_seconds) >= ini)[0][0]
                id_fim = np.where(self.dataframe[0].apply(__to_seconds) <= fim)[0][-1]

                x_temp = np.array(x[id_ini: id_fim + 1])
                y_temp = np.array(y[id_ini: id_fim + 1])

                if all(val == 0 for val in x_temp) and all(val == 0 for val in y_temp):
                  x_temp = np.array([0])
                  y_temp = np.array([0])
                else:
                  x_temp = [i for i,j in zip(x_temp,y_temp) if (i != 0 and j != 0)]
                  y_temp = [j for i,j in zip(x[id_ini: id_fim + 1],y_temp) if (i != 0 and j != 0)]

                __plot_heatmap(x_temp, y_temp, self.emotions_coord, "animated")
                plt.title("Emotions from " + str(ini) + " to " + str(fim) + " seconds")
                plt.savefig("tempjpgs/output" + str(atual) + ".jpg")
                plt.close()
                if fim > maximo:
                  break
                ini += stride
                fim += stride
                atual += 1
            self.logger.info("Done generating images")

            self.logger.info("Creating Video")
            img_array = []
            for filename in sorted(glob.glob('tempjpgs/*.jpg') , key=__numericalSort):
                img = cv2.imread(filename)
                height, width, layers = img.shape
                size = (width,height)
                img_array.append(img)
                os.remove(filename)

            os.rmdir("tempjpgs")

            clip = VideoFileClip(self.mp4)
            value = clip.size
            rate = 1 + (clip.fps - 1 ) *join_video
            out = cv2.VideoWriter('heatmap.mp4',cv2.VideoWriter_fourcc(*'XVID'), rate, size)


            if join_video == True:

              rate = int(rate)
              tam =  window
              count = 0
              duration = int(clip.duration)
              duration *= rate

              for i in range(len(img_array)):
                for j in range(rate * tam):
                  if count >= duration:
                    break
                  out.write(img_array[i])
                  count += 1
                tam = stride
              while count < duration:
                out.write(img_array[-1])
                count += 1

            else:
              for i in range(len(img_array)):
                for j in range(2):
                  out.write(img_array[i])

            out.release()

            myvideo = VideoFileClip('heatmap.mp4')
            self.logger.info("Video created")

            if join_video == True:
              self.logger.info("Joining Videos")

              flag = 0

              bashCommand = "ffmpeg -y -i heatmap.mp4 -f lavfi -i anullsrc -vcodec copy -acodec aac -shortest theatmap.mp4"
              flag += os.system(bashCommand)

              bashCommand = "ffmpeg -y -i theatmap.mp4 -filter:v scale=" + str(value[0]) + ":" + str(value[1]) + " sheatmap.mp4"
              flag += os.system(bashCommand)

              bashCommand = "ffmpeg -y -i " + self.mp4 + " -i sheatmap.mp4 -filter_complex \"[0][1]scale2ref=\'oh*mdar\':\'if(lt(main_h,ih),ih,main_h)\'[0s][1s];[1s][0s]scale2ref=\'oh*mdar\':\'if(lt(main_h,ih),ih,main_h)\'[1s][0s];[0s][1s]hstack,setsar=1; [0:a][1:a]amerge[a]\" -map \"[a]\" -ac 2 video_with_heatmap.mp4"
              flag += os.system(bashCommand)

              if(flag == 0):
                self.logger.info("Videos successufully joined")
              else:
                self.logger.info("Error detected joining videos")

              return

            return ipython_display(myvideo)


        else:
          __plot_heatmap(x, y, self.emotions_coord, modality)

#Funcoes auxiliares para classifcar quanto as emocoes
          
#Translate the sentences from portuguese to english in order to use the text classification model  
def __traduz(frase, pten_pipeline):
    traducao = pten_pipeline(frase)
    traducao = list(traducao[0].values())
    return traducao[0]

#Função para extrair do dicionario retornado pelo goemotions a emoção mais provável e sua probabilidade
def __emocao_provavel(frase, emot_pipe):
    emotion_labels = emot_pipe(frase)

    maximo = emotion_labels[0][0]["score"]
    emocao = emotion_labels[0][0]["label"]

    for dict in emotion_labels[0]:
        if dict["score"] > maximo:
          maximo = dict["score"]
          emocao = dict["label"]

    return emocao, maximo

#Funcoes auxiliares para gerar o heatmap

numbers = re.compile(r"(\d+)")
def __numericalSort(value):
  parts = numbers.split(value)
  parts[1::2] = map(int, parts[1::2])
  return parts
def __generate_coord(label, coords):
    index = coords.loc[coords['Emotion'] == label].index[0]
    x = coords.iloc[index]['X']
    y = coords.iloc[index]['Y']
    return (x,y)
def __kde_quartic(d,h):
    dn=d/h
    P=(15/16)*(1-dn**2)**2
    return P
def __plot_heatmap(x, y, emotions_coord, modality):
    #Definindo tamanho do grid e do raio(h)
    grid_size=0.02
    h=0.5

    #Tomando valores de máximos e mínimos de X e Y.
    x_min=-1
    x_max=1
    y_min=-1
    y_max=1

    #Construindo grid
    x_grid=np.arange(x_min-h,x_max+h,grid_size)
    y_grid=np.arange(y_min-h,y_max+h,grid_size)
    x_mesh,y_mesh=np.meshgrid(x_grid,y_grid)

    #Determinando ponto central do grid
    xc=x_mesh+(grid_size/2)
    yc=y_mesh+(grid_size/2)

    intensity_list=[]
    for j in range(len(xc)):
        intensity_row=[]
        for k in range(len(xc[0])):
            kde_value_list=[]
            for i in range(len(x)):
                #Calculando distância
                d=math.sqrt((xc[j][k]-x[i])**2+(yc[j][k]-y[i])**2)
                if d<=h:
                    p=__kde_quartic(d,h)
                else:
                    p=0
                kde_value_list.append(p)
            #Soma os valores de intensidade
            p_total=sum(kde_value_list)
            intensity_row.append(p_total)
        intensity_list.append(intensity_row)

    #Saída do Heatmap
    plt.figure(figsize=(7,7))

    intensity=np.array(intensity_list)
    plt.pcolormesh(x_mesh,y_mesh,intensity,cmap='YlOrRd') #https://matplotlib.org/stable/tutorials/colors/colormaps.html


    #fig, ax = plt.subplots()

    x_emo = emotions_coord.X.to_list()
    y_emo = emotions_coord.Y.to_list()
    plt.scatter(x_emo, y_emo)


    for i, row in emotions_coord.iterrows():
        plt.annotate(row['Emotion'], (x_emo[i], y_emo[i]))

    plt.xlim(-1, 1)
    plt.ylim(-1,1)

    ax = plt.gca()
    ax.add_patch(plt.Circle((0, 0), 1, color='black', fill=False))
    plt.axvline(x = 0, color = 'black', label = 'Arousal')
    plt.axhline(y = 0, color = 'black', label = 'Valence')

    #plt.colorbar()

    plt.plot(x,y,'x',color='white')

#Funcoes auxiliares para a transcricao

def __time_diff(fim, init):

      time_fim = __to_seconds(fim)
      time_init = __to_seconds(init)

      return time_fim - time_init

def __speech_file_to_array_fn(path, sampling_rate):
    speech_array, _sampling_rate = torchaudio.load(path)
    resampler = torchaudio.transforms.Resample(_sampling_rate, sampling_rate)
    speech = resampler(speech_array).squeeze().numpy()
    return speech

def __encoder_text_adj(sentence, encoder):
    return encoder.encode([sentence])[0]

#Funcoes auxiliares para a funcionalidade audio

def __predict(path, sampling_rate, device, config, feature_extractor, model):
    speech = __speech_file_to_array_fn(path, sampling_rate)
    inputs = feature_extractor(speech, sampling_rate=sampling_rate, return_tensors="pt", padding=True)
    inputs = {key: inputs[key].to(device) for key in inputs}

    with torch.no_grad():
        logits = model(**inputs).logits

    scores = F.softmax(logits, dim=1).detach().cpu().numpy()[0]
    outputs = [{"Emotion": config.id2label[i], "Score": f"{round(score * 100, 3):.1f}%"} for i, score in
               enumerate(scores)]
    return outputs

    # extrai os embeddings da predição feita
def __encoder_audio(path, sampling_rate, device, feature_extractor, model, mean_pool=True):
    speech = __speech_file_to_array_fn(path, sampling_rate)
    inputs = feature_extractor(speech, sampling_rate=sampling_rate, return_tensors="pt", padding=True)
    inputs = {key: inputs[key].to(device) for key in inputs}

    with torch.no_grad():
        out = model(**inputs).hidden_states[-1]
        if mean_pool:
            return np.array(torch.mean(out, dim=1).cpu())[0]
        else:
            return np.array(out.cpu())[0]
#Funcoes auxiliares para a funcionalidade multimodal
def __GCP(G, max_iter=100, audio_weight=0.2, text_weight=0.8, mi=1, min_diff=0.05):

  # inicializando
  L_nodes = []
  for n in G.nodes():
    G.nodes[n]['f'] = np.average([G.nodes[n]['text'],G.nodes[n]['audio']],axis=0,weights=[text_weight, audio_weight])
    L_nodes.append(n)


  for i in range(0,max_iter):
    random.shuffle(L_nodes)

    # propagando
    diff = 0
    for node in L_nodes:

      f_new = np.array([0.0, 0.0])
      count = 0
      for neighbor in G.neighbors(node):
        f_new += G.nodes[neighbor]['f']
        count += 1

      f_new /= count

      f_pseudolabeling = np.average([G.nodes[node]['text'],G.nodes[node]['audio']],axis=0,weights=[text_weight, audio_weight])
      pl = G.nodes[node]['pseudolabeling']*mi
      f_new = f_pseudolabeling*pl + f_new*(1-pl)
      diff += np.linalg.norm(G.nodes[node]['f']-f_new)
      G.nodes[node]['f']=f_new


    print("Iteration #"+str(i+1)+" Q(F)="+str(diff))
    if diff <= min_diff: break

#Funcoes uteis
def __to_seconds(horario):

  horario_separado = horario.split(":")
  seconds = 3600*int(horario_separado[0]) + 60*int(horario_separado[1]) + float(horario_separado[2])

  return seconds