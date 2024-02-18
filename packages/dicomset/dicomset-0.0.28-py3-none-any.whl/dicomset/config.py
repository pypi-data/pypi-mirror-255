import os

DATA_VAR = 'DICOMSET_DATA'

class Directories:
    @property
    def datasets(self):
        filepath = os.path.join(self.data, 'datasets')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath
    
    @property
    def evaluations(self):
        filepath = os.path.join(self.data, 'evaluations')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath

    @property
    def files(self):
        filepath = os.path.join(self.data, 'files')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath

    @property
    def heatmaps(self):
        filepath = os.path.join(self.root, 'heatmaps')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath

    @property
    def models(self):
        filepath = os.path.join(self.data, 'models')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath

    @property
    def lr_find(self):
        filepath = os.path.join(self.root, 'lr-find')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath

    @property
    def predictions(self):
        filepath = os.path.join(self.data, 'predictions')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath

    @predictions.setter
    def predictions(self, value):
        self.__predictions = value

    @property
    def registrations(self):
        filepath = os.path.join(self.root, 'registrations')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath

    @property
    def reports(self):
        filepath = os.path.join(self.data, 'reports')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath

    @property
    def data(self):
        if DATA_VAR not in os.environ:
            raise ValueError(f"Must set env var '{DATA_VAR}'.")
        return os.environ[DATA_VAR]

    @property
    def runs(self):
        filepath = os.path.join(self.data, 'runs')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath

    @property
    def temp(self):
        filepath = os.path.join(self.data, 'tmp')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath

class Formatting:
    @property
    def metrics(self):
        return '.6f'

    @property
    def sample_digits(self):
        return 5

class Regions:
    @property
    def mode(self):
        return 0

directories = Directories()
formatting = Formatting()
regions = Regions()
