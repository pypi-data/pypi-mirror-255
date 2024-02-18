import mlflow 

class FakeModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        pass

    def predict(self, context, model_input):
        return self.model.predict(model_input)

class FictitiousModel:
    def predict(self, input_data):
        return input_data * 2