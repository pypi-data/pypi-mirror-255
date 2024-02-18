from klu.common.errors import BaseKluError


class DatasetNotFoundError(BaseKluError):
    datum_id: int

    def __init__(self, datum_id):
        self.datum_id = datum_id
        self.message = f"Dataset with GUID {datum_id} was not found."
        super().__init__(self.message)
