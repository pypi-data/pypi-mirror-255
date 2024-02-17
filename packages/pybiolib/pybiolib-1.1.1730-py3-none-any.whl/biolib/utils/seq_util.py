import re
from biolib.typing_utils import List, Optional, Dict

allowed_sequence_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
def find_invalid_sequence_characters(sequence):
    invalid_chars = [char for char in sequence if char not in allowed_sequence_chars]
    return invalid_chars

class SeqUtilRecord:
    def __init__(self,
                 sequence: str,
                 sequence_id: str,
                 description: Optional['str'],
                 properties: Optional[Dict[str, str]] = None):
        self.sequence = sequence
        self.id = sequence_id  # pylint: disable=invalid-name
        self.description = description

        if properties:
            disallowed_pattern = re.compile(r"[=\[\]\n]")
            for key, value in properties.items():
                assert not bool(disallowed_pattern.search(key)), "Key cannot contain characters =[] and newline"
                assert not bool(disallowed_pattern.search(value)), "Value cannot contain characters =[] and newline"
            self.properties = properties
        else:
            self.properties = {}

    def __repr__(self) -> str:
        return f'{self.__class__.__name__} ({self.id})'


class SeqUtil:
    @staticmethod
    def parse_fasta(
        file_name: str,
        default_header: Optional[str] = None,
        allow_any_sequence_characters: bool = False,
        allow_empty_sequence: bool = False,
    ) -> List[SeqUtilRecord]:
        with open(file_name, 'r') as file_handle:
            data = file_handle.read().strip()

        if not data:
            return []

        if '>' not in data:
            if default_header:
                lines_with_header = []
                for index, line in enumerate(data.split('\n')):
                    index_string = str(index + 1) if index > 0 else ''
                    lines_with_header.append(f'>{default_header}{index_string}\n{line}')

                data = '\n'.join(lines_with_header)
            else:
                raise Exception(f'No header line found in FASTA file "{file_name}"')

        splitted = []
        tmp_data = ""
        for line in data.splitlines():
            if line.startswith(">"):
                if tmp_data:
                    splitted.append(tmp_data)
                tmp_data = line[1:].strip() + '\n'
            else:
                if line.strip():
                    tmp_data += line.strip() + '\n'

        if tmp_data:
            splitted.append(tmp_data)

        parsed_sequences = []
        for sequence_data in splitted:
            sequence_data_splitted = sequence_data.strip().split('\n')
            header_line = sequence_data_splitted[0].split()
            sequence_id = header_line[0]
            description = sequence_data_splitted[0][len(sequence_id):].strip()
            sequence = "".join([seq.strip().upper() for seq in sequence_data_splitted[1:]])

            if not allow_any_sequence_characters:
                invalid_sequence_characters = find_invalid_sequence_characters(sequence)
                if len(invalid_sequence_characters) > 0:
                    raise Exception(
                        f'Error: Invalid character ("{invalid_sequence_characters[0]}") found in sequence {sequence_id}'
                    )
            if not allow_empty_sequence and len(sequence) == 0:
                raise Exception(
                    f'Error: No sequence found for fasta entry {sequence_id}'
                )

            parsed_sequences.append(
                SeqUtilRecord(sequence=sequence, sequence_id=sequence_id, description=description)
            )
        return parsed_sequences

    @staticmethod
    def write_records_to_fasta(file_name: str, records: List[SeqUtilRecord]) -> None:
        with open(file_name, mode='w') as file_handle:
            for record in records:
                optional_description = f' {record.description}' if record.description else ''
                if record.properties:
                    for key, value in record.properties.items():
                        optional_description += f' [{key}={value}]'
                sequence = '\n'.join(record.sequence[i:i + 80] for i in range(0, len(record.sequence), 80))
                file_handle.write(f'>{record.id}{optional_description}\n{sequence}\n')
