from dataclasses import dataclass
from pathlib import Path


@dataclass
class InputFile:
    file: str

    def __post_init__(self):
        self.file_name_only = Path(self.file).name
        self.file_name_wo_ext = Path(self.file).stem
        self.file_type: str = Path(self.file).suffix
        self.full_path: str = Path(self.file).resolve().parent
        self.full_path_filename = Path(self.file).resolve()

    def valid(self) -> bool:
        return True if Path(self.file).exists() else False


if __name__ == '__main__':

    print('Nothing to see here')
