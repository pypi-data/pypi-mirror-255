from . import layer as Layer
from . import activation as Activation
from . import loss as Loss
from . import optimizer as Optimizer
import numpy as np
import matplotlib.pyplot as plt

class Model:
	def __init__(self):
		self.n_layer = 0
		self.layers = []
		self.activations = []
		self.accuracies = []
		self.losses = []

	def compile(self, optimizer=None, loss=None):
		self.optimizer = optimizer
		self.loss = loss

	def add(self, layer: Layer.Layer, activation: Activation):
		self.n_layer += 1
		self.layers.append(layer)
		self.activations.append(activation)
	
	def predict(self, values):
		if isinstance(self.loss, Loss.BinaryCrossEntropy):
			predictions = (values > 0.5) * 1
		if isinstance(self.loss, Loss.CategoricalCrossEntropy):
			predictions = np.argmax(values, axis=1)
		return predictions
	
	def fit(self, x=None, y=None, batch_size=None, epochs=1, shuffle=True, display=False, plot=False):
		self.accuracies.clear()
		self.losses.clear()
		loss_activation = None
		x = np.array(x)
		y = np.array(y)
		steps = 1
		if (batch_size):
			steps = len(x) // batch_size
			if (steps * batch_size < len(x)):
				steps += 1

		for epoch in range(epochs):
			if shuffle:
				indices = np.random.permutation(len(x))
				x = x[indices]
				y = y[indices]
			layer: Layer
			activation: Activation
			
			for step in range(steps):
				if (batch_size):
					batch_X = x[step*batch_size : (step+1) *batch_size]
					batch_Y = y[step*batch_size : (step+1) *batch_size]
				else:
					batch_X = x
					batch_Y = y
				feed = batch_X

				# forward
				for (layer, activation) in zip(self.layers, self.activations):
					layer.forward(feed)
					feed = layer.output


					# If we have a Loss Activation, it take one more input. So we have to differenciate them and we get the loss here
					if isinstance(activation, Activation.Softmax_CategoricalCrossEntropy):
						loss = activation.forward(feed, batch_Y)
						loss_activation = activation;
					else:
						activation.forward(feed)
					feed = activation.output

				predictions = self.predict(feed)
				accuracy = np.mean(predictions==batch_Y)

				if loss_activation == None:
					loss = self.loss.calculate(feed, batch_Y)
					self.loss.backward(feed, batch_Y)
					feed = self.loss.dinputs
				# If we have a Loss Activation, we have to do the backward pass directly on the activtation function, the loss is already calculated
				else:
					activation.backward(feed, batch_Y)
					feed = activation.dinputs

				self.losses.append(loss)
				self.accuracies.append(accuracy)
				if (display):
					if not epoch % 100:
						if batch_size:
							print(f' step: {step}, epoch: {epoch}, ' + f'acc: {accuracy:.3f}, ' + f'loss: {loss:.3f}, ' )
						else:	
							print(f'epoch: {epoch}, ' + f'acc: {accuracy:.3f}, ' + f'loss: {loss:.3f}, ' )#+ f'lr: {self.optimizer.current_learning_rate}')
				
				# backward
				for (layer, activation) in zip(reversed(self.layers), reversed(self.activations)):
					# since we have already compute the backward for the Loss and the activation, we do not have to compute it here
					if (isinstance(activation, Activation.Softmax_CategoricalCrossEntropy)):
						pass
					else:
						activation.backward(feed)
						feed = activation.dinputs
					layer.backward(feed)
					feed = layer.dinputs
			
				# update
				self.optimizer.pre_update_params()
				for layer in self.layers:
					self.optimizer.update_params(layer)
				self.optimizer.post_update_params()

		if (plot):
			self.plot(epochs)

	def evaluate(self, x, y):
		x = np.array(x)
		y = np.array(y)
		feed = x
		loss_activation = None

		layer: Layer.Layer
		activation: Activation
		for (layer, activation) in zip(self.layers, self.activations):
			layer.forward(feed)
			feed = layer.output
			if (isinstance(activation, Activation.Softmax_CategoricalCrossEntropy)):
				loss = activation.forward(feed, y)
				loss_activation = activation;
			else:
				activation.forward(feed)
			feed = activation.output
		if loss_activation == None:
			loss = self.loss.calculate(feed, y)
		else:
			pass
		predictions = self.predict(feed)
		accuracy = np.mean(predictions == y)

		print(f'accuracy: {accuracy:.3f}')
		#true_table = np.array([1 if pred == real else 0 for pred, real in zip(predictions, y)]).reshape(1, -1)
		#print("true table : ", true_table)
		return {"prediction": predictions, "accuracy": accuracy}
		#return {"predictions": predictions, "accuracy": accuracy, "loss": loss, "true_table": true_table}
	
	def plot(self, epochs):
		plt.figure(figsize=(12, 4))

		# loss
		plt.subplot(1, 2, 1)
		plt.plot(range(epochs), self.losses, label='Loss')
		plt.title('Training Loss')
		plt.xlabel('Epochs')
		plt.ylabel('Loss')
		plt.legend()

		# accuracy
		plt.subplot(1, 2, 2)
		plt.plot(range(epochs), self.accuracies, label='Accuracy', color='orange')
		plt.title('Training Accuracy')
		plt.xlabel('Epochs')
		plt.ylabel('Accuracy')
		plt.legend()

		plt.tight_layout()
		plt.show()





