import dataset_generator as dataset
import numpy as np
import os


class binary_nets_wrapper:

	def __init__(self, binary_nets, classes=dataset.ALPHABET_ALL):

		self._classes = classes
		self._models = binary_nets


	# Returns a dictonary containing for each key, the binary classifier represented by that key
	# es: keu=a, binary classifier = a, not a
	# in a dictionary entry, prediction[key], is a list containing for the index i, the prediction of that
	# classifier for the test entry i.
	# You can also see this as a matrix A where the rows are the classifier, and the columns are the prediction
	# Aij represents the prediction of classifier i for the test input j
	def predict_matrix(self, X_test, verbose=0):
		prediction = {}
		for letter in self._models:
			prediction[letter] = self._models[letter].predict(X_test, verbose=verbose)

		return prediction

	# Returns a ranking of letters for each prediction
	# es: prediction[i] is a list of prediction i containing (letter, value)
	# where the letter is the class, and the value is its probability
	def predict_ranking(self,X_test,verbose=0):
		prediction = []
		for i,letter in enumerate(self._models):
			letter_pred = self._models[letter].predict(X_test, verbose=verbose)
			prediction.append(list(map(lambda x : (letter, x[1]*100), letter_pred)))

		dt = np.dtype([('letters', np.str_, 16), ('grades', np.float64)])
		prediction = np.array(prediction, dtype=dt)
		prediction = prediction.T
		prediction = np.sort(prediction,order=["grades","letters"])

		# In decreasing order
		for i,row in enumerate(prediction):
			prediction[i] = row[::-1]

		return prediction

	# Predict and choose if returning a ranking or a matrix of prediction
	def predict(self,X_test, ranking=1, verbose=0):
		if ranking:
			ranking_lst = self.predict_ranking(X_test, verbose=verbose)
			prediction = []
			for row in ranking_lst:
				# Bad Cut
				if row[0][1] < 50:
					prediction.append((False, []))
				# Good Cut
				else:
					prediction.append((True, row))
			return prediction
		else:
			return self.predict_matrix(X_test, verbose=verbose)

		
		





