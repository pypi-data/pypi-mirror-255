import os;
import requests;
import numpy as np;
import PIL;

from tempfile import NamedTemporaryFile;

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from torch import Tensor;

from PIL.Image import Image;

from ...core import Block;

class Embedding(Block):
      """
      Dada una imagen calcula su embedding.
      """

      #-------------------------------------------------------------------------
      @staticmethod
      def download(source:str):
          if source.startswith("http"):
             with requests.get(source, stream=True) as r:
                  r.raise_for_status();
                  with NamedTemporaryFile(delete=False) as f:
                       for chunk in r.iter_content(chunk_size=65536//8):
                           f.write(chunk);
                       fuente = f.name;
                       istemp = True;
          else:
             fuente = source;
             istemp = False;
          return (fuente, istemp);

      #-------------------------------------------------------------------------
      @staticmethod
      def embedding(model, imagen):
          result = model.embed(imagen);
          return result.embeddings[0].embedding;
          
      #-------------------------------------------------------------------------
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          
          cwd = os.path.dirname(__file__);
          mwd = os.path.join(cwd, '../../models');
          fwd = os.path.join(cwd, '../../fonts');
          
          BaseOptions = mp.tasks.BaseOptions
          ImageEmbedder = mp.tasks.vision.ImageEmbedder
          ImageEmbedderOptions = mp.tasks.vision.ImageEmbedderOptions
          VisionRunningMode = mp.tasks.vision.RunningMode

          self.model_name="mobilenet_v3_small.tflite";
          if "model_name" in self.params:
              if self.params["model_name"].lower() in ["nano",  "xs"]: self.model_name="mobilenet_v3_small.tflite";
              if self.params["model_name"].lower() in ["small", "s" ]: self.model_name="mobilenet_v3_small.tflite";
              if self.params["model_name"].lower() in ["medium","m" ]: self.model_name="mobilenet_v3_small.tflite";
              if self.params["model_name"].lower() in ["large", "l" ]: self.model_name="mobilenet_v3_large.tflite";
              if self.params["model_name"].lower() in ["xlarge","xl"]: self.model_name="mobilenet_v3_large.tflite";

          options = ImageEmbedderOptions(base_options=BaseOptions(model_asset_path=os.path.join(mwd, self.model_name)), quantize=self.params.quantize or True, running_mode=VisionRunningMode.IMAGE);
          self._model = ImageEmbedder.create_from_options(options);

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("image",{Image,str})
      def slot_image(self, slot, data:(Image|str)):

          if data and self.signal_embedding():

             assert isinstance(data,(Image,str));

             if   isinstance(data,str):
                  try:
                    fuente, istemp = Embedding.download(data);
                    imagen = PIL.Image.open(fuente);                      
                    imagen = imagen.convert('RGB');
                    imagen = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(imagen));
                    self.signal_embedding(Embedding.embedding(self._model, imagen));
                  finally:
                    if istemp: os.remove(fuente);

             elif isinstance(data,Image):
                  imagen = data.convert('RGB');
                  imagen = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(imagen));
                  self.signal_embedding(Embedding.embedding(self._model, imagen));

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("embedding",Tensor)
      def signal_embedding(self, data):
          return Tensor(data);
