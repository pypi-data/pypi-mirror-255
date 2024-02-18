from .base import InstructionBase


class ChainInstruction(InstructionBase):
    head = '$<'

    def run(self, variables, storage):
        return self.instruction_set.run(variables.payload, self.value, variables, storage)
