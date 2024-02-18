# DeepLearningKit

**Description:**

Welcome to DeepLearningKit, a Python library crafted with a passion for learning and a drive to simplify the journey into the depths of neural networks. As my inaugural project in this domain, DeepLearningKit is designed primarily for my educational purposes, aiming to help me to understand and experiment with deep learning concepts.
This release marks the first version of DeepLearningKit, but the journey doesn't end here! I'll be actively working on improving and expanding the library regularly. Stay tuned for updates and new features in future releases.

**Key Features:**
1. **Modular Architecture:** DeepLearningKit offers a modular architecture allowing users to easily construct neural network models by stacking layers and specifying activation functions.
2. **Customizable Initialization:** Users can choose from a variety of weight initialization methods such as RandomNormal, Zero, He, Xavier, and LeCun, or define their custom initialization strategies. (Not complete)
3. **Optimizers:** The library provides a selection of optimization algorithms including SGD, Adagrad, RMSProp, Adadelta, and Adam, each with adjustable parameters for fine-tuning the training process.
4. **Loss Functions:** DeepLearningKit supports commonly used loss functions such as Categorical Cross-Entropy and Binary Cross-Entropy, enabling users to train models for classification and regression tasks.

**Getting Started:**
1. **Installation:** Install DeepLearningKit using pip:
   ```
   pip install deeplearningkit
   ```

2. **Usage:**
   ```python
   from deeplearningkit import Model, Dense, Activation, Optimizer, Loss
   import numpy as np

   # Define and compile the model
   model = Model()
   model.add(Dense(n_inputs=784, n_neurons=128, initializer='he'), Activation('relu'))
   model.add(Dense(n_inputs=128, n_neurons=10, initializer='xavier'), Activation('softmax'))
   model.compile(optimizer=Optimizer.SGD(learning_rate=0.01), loss=Loss.CategoricalCrossEntropy())

   # Load and train the model
   X_train, y_train = load_data()
   model.fit(x=X_train, y=y_train, epochs=10, batch_size=32, shuffle=True, display=True, plot=True)

   # Evaluate the model
   X_test, y_test = load_test_data()
   model.evaluate(X_test, y_test)
   ```

**Contributing:**
DeepLearningKit is a beginner-friendly project (because I'm a beginner !), and contributions from all skill levels are welcome! Whether you're fixing bugs or improving (the poor) documentation, your contributions are valuable. Feel free to open issues or pull requests on the GitHub repository.

**License:**
DeepLearningKit is licensed under the [MIT License](LICENCE).

**Contact:**
For questions, feedback, or support, please reach out to me via email at dasereno@student.42.fr.

**Acknowledgments:**
This project wouldn't have been possible without the support and guidance from the deep learning community, bigup to the book : 'Neural Network From Scratch' by Harrison Kinsley and Daniel Kukiela <3 . Let's continue to learn and grow together!