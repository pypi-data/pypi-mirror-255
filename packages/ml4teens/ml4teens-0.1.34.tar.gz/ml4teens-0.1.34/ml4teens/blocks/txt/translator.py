#https://huggingface.co/facebook/nllb-200-distilled-600M

#https://huggingface.co/facebook/mbart-large-50-many-to-many-mmt

# TODO No funciona (modelo demasido grande)

from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

from   ...core import Block;

class Translator(Block):

      #------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          device = "cuda" if torch.cuda.is_available() else "cpu";
          model_name = "facebook/nllb-200-distilled-600M"
          tokenizer = AutoTokenizer.from_pretrained(model_name)
          model = AutoModelForSeq2SeqLM.from_pretrained(model_name);
          # Aplicar Quantization al modelo
          model_quantized = torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8);
          # Crear el pipeline con el modelo cuantizado
          self._pipeline = pipeline("translation", model=model_quantized, tokenizer=tokenizer)

      #------------------------------------------------------------------------
      # SLOTS
      #------------------------------------------------------------------------
      @Block.slot("text", {str})
      def slot_text(self, slot, data):
          if data:
             text = self._pipeline(data, src_lang="en", tgt_lang=self.params.language or "es")
             self.signal_text(text[0]['translation_text']);

      #------------------------------------------------------------------------
      # SIGNALS
      #------------------------------------------------------------------------
      @Block.signal("text", str)
      def signal_text(self, data):
          return data;

##############################################################################################################
if __name__=="__main__":
   import ... as ml;

   context = ml.core.Context.instance;
   context.reset();

   nllb = Translator();
   terminal = ml.blocks.Terminal();

   nllb("text") >> terminal("stdout");

   context.emit(target=nllb, slot_name="text", data="Hi, my friend! Who are you?");
   context.wait();
