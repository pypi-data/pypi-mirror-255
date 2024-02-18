from abc import ABC, abstractmethod
from .loss import CategoricalCrossEntropy
import numpy as np

class Activation(ABC):
	inputs: np.ndarray
	output: np.ndarray
	dinputs: np.ndarray

	def __init__(self, activation: str):
		if (activation.lower() == "relu"):
			return ReLU()
		if (activation.lower() == "sigmoid"):
			return Sigmoid()
		if (activation.lower() == "softmax"):
			return Softmax()
		if (activation.lower() == "softmax_categoricalcrossentropy")
			return Softmax_CategoricalCrossEntropy()
		return None

	@abstractmethod
	def forward(self, inputs):
		pass

	@abstractmethod
	def backward(self, dvalues):
		pass

class ReLU(Activation):
	def forward(self, inputs):
		self.inputs = inputs
		self.output = np.maximum(0, inputs)
	def backward(self, dvalues):
		self.dinputs = dvalues.copy()
		self.dinputs[self.inputs <= 0] = 0

class Sigmoid(Activation):
	def forward(self, inputs):
		self.inputs = inputs
		self.output = 1/(1 + np.exp(-inputs))
	def backward(self, dvalues):
		self.dinputs = dvalues * (1 - self.output) * self.output
	
class Softmax(Activation):
	def forward(self, inputs):
		# on prend tout les inputs (matrice de vecteur ex : [[1, 2, 3], [2, 1, 3], [3, 1, 2]])
		# pour chaque vecteur on soustrais la valeur maximal ex : [[1 - 3, 2 - 3, 3 - 3], [2 - 3, 1 - 3, 3 - 3], [3 - 3, 1 - 3, 2 - 3]]
		# puis on passe le result en exponentiel. Donc pas de valeur négative (pas logique) et l'exponentiel
		# est monotonique, ce qui permet de garder une cohérence de valeur : + la valeur est petite (negative ou proche de zero)
		# et + elle sera proche de zero, et + la valeur est grande + elle sera grande.
		exp_values = np.exp(inputs - np.max(inputs, axis=1, keepdims=True))
		# Probleme : L'exponentiel grandi bien trop vite, donc on normalize les valeurs entre 0 - 1. En divisant ça par la somme de toutes les valeurs
		# exponentiel.
		self.output = exp_values / np.sum(exp_values, axis=1, keepdims=True)
	def backward(self, dvalues):
		self.dinputs = np.empty_like(dvalues)

		for index, (single_output, single_dvalues) in enumerate(zip(self.output, dvalues)):
			single_output = single_output.reshape(-1, 1)
			jacobian_matrix = np.diagflat(single_output) - np.dot(single_output, single_output.T)
			self.dinputs[index] = np.dot(jacobian_matrix, single_dvalues)

class Softmax_CategoricalCrossEntropy(Activation):
	def __init__(self):
		self.activation = Softmax()
		self.loss = CategoricalCrossEntropy()
	def forward(self, inputs, y_true):
		self.activation.forward(inputs)
		self.output = self.activation.output
		return self.loss.calculate(self.output, y_true)

	def backward(self, dvalues, y_true):
		samples = len(dvalues)
		if len(y_true.shape) == 2:
			y_true = np.argmax(y_true, axis=1)
		self.dinputs = dvalues.copy()
		self.dinputs[range(samples), y_true] -= 1
		self.dinputs = self.dinputs / samples
