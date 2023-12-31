from cnn import ConvolutionalNeuralNetwork
import ensemble

def ensemble_builder(classes, nb_epochs, number_of_nets=5, path="checkpoints//temp", nb_filters1=20, nb_filters2=40,\
							dense_layer_size1=150):
	
	my_ensemble = ensemble.ensemble()

	for i in range(number_of_nets):
		
		net = ConvolutionalNeuralNetwork(classes, nb_epochs=nb_epochs, model_dir=path, \
			 model_name=str(i), batch_size=128, nb_filters1=nb_filters1, nb_filters2=nb_filters2,\
			 dense_layer_size1=dense_layer_size1)

		my_ensemble.add_model(net)

	my_ensemble.compile_model()

	return my_ensemble





