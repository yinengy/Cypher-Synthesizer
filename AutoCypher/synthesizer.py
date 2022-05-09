from example_parser import Example

class Synthesizer:
    """
    Synthesis Cypher query from given Input/Output example
    """
    def __init__(self, example: Example) -> None:
        self.example = example


if __name__=="__main__":
    example = Example("example/example1")