import sys
print("Python version:", sys.version)
print("Python path:", sys.path)

try:
    import agents
    print("Agents module path:", agents.__file__)
    print("Agents module version:", getattr(agents, "__version__", "Unknown"))
    print("Agents module contents:", dir(agents))
except ImportError as e:
    print("Error importing agents module:", e)

try:
    import tensorflow as tf
    print("TensorFlow version:", tf.__version__)
    print("TensorFlow has contrib:", hasattr(tf, "contrib"))
except ImportError as e:
    print("Error importing tensorflow:", e)
