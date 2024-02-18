################################################################################
# TODO queda por hacer, ya que depende del core.
################################################################################

from ..core import Block;

################################################################################
class CustomBlock(Block):
      """
      Permite definir un tipo de bloque que tiene slots y signals creados por el usuario.
      """

      #-------------------------------------------------------------------------
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__();
          builder=None;
          slots  =None;
          signals=None;
          if "builder" in kwargs:
             builder=kwargs["builder"];
             del kwargs["builder"];
             assert callable(builder);

          if "slots" in kwargs:
             slots=kwargs["slots"];
             del kwargs["slots"];
             assert isinstance(slots,dict);

          if "signals" in kwargs:
             signals=kwargs["signals"];
             del kwargs["signals"];
             assert isinstance(signals,dict);

          if slots:
             for key in slots:
                 self.registerSlot(key, slots[key]);

          if signals:
             for key in signals:
                 self.registerSignal(key, signals[key]);

          if builder: self.builder(kwargs);

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      # no tiene!

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      # no tiene!


################################################################################
from ml4teens.tools import debug;
debug.disable();

import ml4teens as ml;

context = ml.core.Context.instance;

def init(self, **kwargs):
    pass;

def slot_whatever(self, slot, data):
    self.signals.whatever(data);

def signal_whatever(self, data):
    return data;

custom   = CustomBlock(builder=init, slots={"whatever":slot_whatever}, signals={"whatever":signal_whatever}, x=1, y=2, z=3);
terminal = ml.blocks.Terminal();

custom("whatever") >> terminal("stdout");

context.emit(target=custom, slot="whatever", data="Hola mundo!");
context.wait();

