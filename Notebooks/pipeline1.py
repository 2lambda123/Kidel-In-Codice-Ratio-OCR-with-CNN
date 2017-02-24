from ocr_ensamble_builder import ocr_cnn_ensamble_builder
import dataset_generator as dataset
import numpy as np
import os

# This pipeline is composed by n ensamble models of binary nerual networks, where n is the number of the classes to
# recognize

class pipeline1:

	def __init__(self, chars=dataset.ALPHABET_ALL, nb_epochs = 800, number_of_nets=5, batch_size=128, path="checkpoints/pipeline1"):

		# Contains each binary models per letter
		self._models = {}

		for letter in chars:
			path_letter = os.path.join(path, letter)
    		
		    if not os.path.exists(path):
		        os.makedirs(path)

		    self._models[letter] = ocr_cnn_ensamble_builder(2, nb_epochs, number_of_nets=number_of_nets, path=path_letter):
			

	# We prefer write a fit method per letter in order to avoid loading the entire dataset
	def fit_letter(self, letter, X_train, y_train, X_test=[], y_test=[], verbose=0):
		self._models[letter].fit(X_train, y_train, X_test=X_test, y_test=y_test, verbose=verboses)

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
			prediction[i] = list(map(lambda x : (letter, x[1]*100), self._models[letter].predict(X_test, verbose=verbose)))

		dt = np.dtype([('letters', np.str_, 16), ('grades', np.float64)])
		prediction = np.array(prediction, dtype=dt)
		prediction = prediction.T
		prediction = np.sort(x.T,order=["grades","letters"])

		# In decreasing order
		for i,row in enumerate(prediction):
			prediction[i] = row[::-1]

		return prediction

	# Predict and choose if returning a ranking or a matrix of prediction
	def predict(self,X_test,verbose=0, ranking=1, verbose=0):
		if ranking:
			ranking_lst = predict_ranking(X_test, verbose=verbose)
			prediction = []
			for row in ranking_lst:
				# Bad Cut
				if row[0][1] < 50
					prediction.append((False, []))
				# Good Cut
				else
					prediction.append((True, row))
		else
			return predict_matrix(X_test, verbose=verbose)


		
		




