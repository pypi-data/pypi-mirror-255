class FinetuneNotFoundError(Exception):
    fine_tune_id: str

    def __init__(self, fine_tune_id: str):
        self.fine_tune_id = fine_tune_id
        self.message = f"Finetune with id {fine_tune_id} was not found."
        super().__init__(self.message)
