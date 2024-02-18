from abc import ABC, abstractmethod
import numpy as np

class Loss(ABC):
	dinputs: np.ndarray

	@abstractmethod
	def forward(self, y_pred, y_true):
		pass
	
	def backward(self, dvalues, y_true):
		pass

	def calculate(self, output, y):
		sample_losses = self.forward(output, y)
		data_loss = np.mean(sample_losses) # calcul la moyenne de la loss
		return data_loss

class CategoricalCrossEntropy(Loss):
	def forward(self, y_pred, y_true):
		samples = len(y_pred)
		y_pred_clipped = np.clip(y_pred, 1e-7, 1 - 1e-7)

		if len(y_true.shape) == 1: # quand on reçoit un vecteur de label : [0, 2, 0, 1] -> la classe 0, 2, 0, 1 sont vrai.
			# donc on cherche directement a la case des predictions les valeurs
			correct_confidences = y_pred_clipped[range(samples), y_true]
		elif len(y_true.shape) == 2: # One hot encoding, on reçoit une matrice : [[1, 0, 0], [0, 0, 1], [1, 0, 0], [0, 1, 0]]
			# donc on a juste a multiplier chaque vecteur par la reponse : [1, 0, 0] * 0 = 0, [0, 0, 1] * 2 = 2.... 
			#(meme resultat que pour la ligne au dessus)
			correct_confidences = np.sum(y_pred_clipped * y_true, axis=1)
		
		negative_log_likelihoods = -np.log(correct_confidences)
		# ici on met au -logarithme (naturel !! base E) les resultat. Ca permet de pouvoir revenir au resultat en 
		# mettant en exponentiel le logarithme. (pratique pour la backpropagation et l'optimisation)
		return negative_log_likelihoods
	def backward(self, dvalues, y_true):
		samples = len(dvalues)
		labels = len(dvalues[0])

		if (len(y_true.shape) == 1):
			y_true = np.eye(labels)[y_true]
		
		self.dinputs = -y_true / dvalues
		self.dinputs = self.dinputs / samples
	
class BinaryCrossEntropy(Loss):
	def forward(self, y_pred, y_true):
		y_pred_clipped = np.clip(y_pred, 1e-7, 1 - 1e-7)

		sample_losses = -(y_true * np.log(y_pred_clipped) + (1 - y_true) * np.log(1 - y_pred_clipped))
		sample_losses = np.mean(sample_losses, axis=-1)

		return sample_losses
	def backward(self, dvalues, y_true):
		samples = len(dvalues)
		outputs = len(dvalues[0])

		clipped_dvalues = np.clip(dvalues, 1e-7, 1 - 1e-7)
		self.dinputs = -(y_true / clipped_dvalues - (1 - y_true) / (1 - clipped_dvalues)) / outputs
		self.dinputs = self.dinputs / samples