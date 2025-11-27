import os
from config import Config
print("Root:", Config.ROOT_DIR)
print("Audio:", Config.AUDIO_DIR)
print("Outputs:", Config.OUTPUT_DIR)
print("test_data:", Config.TESTDATA_DIR)    
print("Exists(audio)?", os.path.exists(Config.AUDIO_DIR))
print("Exists(outputs)?", os.path.exists(Config.OUTPUT_DIR))
print("Exists(test_data)?", os.path.exists(Config.TESTDATA_DIR))