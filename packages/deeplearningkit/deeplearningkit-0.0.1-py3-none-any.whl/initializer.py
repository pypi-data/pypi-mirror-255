import numpy as np

class Initializer:
	def __call__(self, shape: tuple) -> np.ndarray:
		pass

class RandomNormal(Initializer):
	def __init__(self,  mean=0.0, std=0.05):
		self.mean = mean
		self.std = std
		pass

	def __call__(self, shape: tuple) -> np.ndarray:
		return np.random.normal(self.mean, self.std, shape)

class Zero(Initializer):
	def __init__(self):
		pass

	def __call__(self, shape: tuple) -> np.ndarray:
		return np.zeros(shape)

class He(Initializer):
	def __init__(self, n_input: int):
		self.n_input = n_input

	def __call__(self, shape: tuple) -> np.ndarray:
		std = np.sqrt(2.0 / self.n_input)
		return np.random.randn(*shape) * std

class Xavier(Initializer):
	def __init__(self, n_input: int, n_output: int):
		self.n_input = n_input
		self.n_output = n_output
		pass

	def __call__(self, shape: tuple) -> np.ndarray:
		limit = np.sqrt(6 / (self.n_input + self.n_output))
		return np.random.uniform(-limit, limit, shape)

class LeCun(Initializer):
	def __init__(self, n_input: int):
		self.n_input = n_input
		pass
	
	def __call__(self, shape: tuple) -> np.ndarray:
		limit = np.sqrt(1 / self.n_input)
		return np.random.uniform(-limit, limit, shape)