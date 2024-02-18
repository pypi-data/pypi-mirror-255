class RegisterModelProps:
    def __init__(self, model_id, model_location, is_active, **kwargs):
        self.model_id = model_id
        self.model_location = model_location
        self.is_active = is_active
        for key, value in kwargs.items():
            setattr(self, key, value)
