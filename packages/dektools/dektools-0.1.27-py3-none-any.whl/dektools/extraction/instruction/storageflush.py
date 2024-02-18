from .base import InstructionBase
from ..produce import DefaultProduce


class StorageFlushInstruction(InstructionBase):
    head = '$='
    produce_cls = DefaultProduce

    def run(self, variables, storage):
        return [storage.flush(self.produce_cls.wrapper(self.key), self.value is not False)]
