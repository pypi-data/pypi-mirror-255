from typing import Any, cast
import inspect, tempfile, os
import warnings


# Keras doesn't pickle well on Windows/Mac. This wrapper saves/loads it from a file format that does work cross-OS
class KerasWrapper:
  saveFormat = "h5"  # default, maybe "keras" will work soon. That might also remove the need for this custom code

  def __init__(self, kerasModel: Any):
    self.saveFormat = KerasWrapper.saveFormat
    self.data = KerasWrapper.getKerasBytes(kerasModel, self.saveFormat)

  @classmethod
  def isKerasModel(cls, obj: Any) -> bool:
    return (hasattr(obj, "__module__") and obj.__module__.startswith("keras.") and hasattr(obj, "save") and
            inspect.isroutine(obj.save))

  @classmethod
  def getKerasBytes(cls, obj: Any, saveFormat: str) -> bytes:
    import os, tempfile
    tf = tempfile.NamedTemporaryFile(suffix=f".{saveFormat}", delete=False)
    tf.close()  # windows doesn't allow multiple open files
    with warnings.catch_warnings():
      warnings.simplefilter("ignore")  # Keras warns about using H5
      obj.save(tf.name, overwrite=True, save_format=saveFormat)
    with open(tf.name, "rb") as f:
      data = f.read()
    os.unlink(tf.name)
    return data

  def getModel(self):
    tf = tempfile.NamedTemporaryFile(suffix=f".{self.saveFormat}", delete=False)
    tf.close()  # windows doesn't allow multiple open files
    from tensorflow import keras  # type: ignore
    with open(tf.name, "wb") as f:
      f.write(self.data)
    kerasModel = cast(Any, keras.models.load_model(tf.name))  # type: ignore
    os.unlink(tf.name)
    return kerasModel
