from .abc import Dataset, DatasetItem, Message
from datasets import load_dataset

class HFDataset(Dataset):
    def __init__(self, hf_name: str, split='test'):
        super().__init__()
        self.name = 'hf:' + hf_name
        self._dataset = load_dataset(hf_name, trust_remote_code=True)
        self._split = split

    def __iter__(self):
        for x in self._dataset[self._split]:
            prompt = x['prompt']
            completion = x['completion']
            id_ = x['id']

            yield DatasetItem(
                id=id_,
                messages = [Message.user(prompt)],
                expected=completion,
            )