import ast
from collections import defaultdict
import csv
import ctypes
from datetime import datetime, timedelta, timezone
from itertools import tee
from pathlib import Path
from typing import Callable, Iterable, TypeVar
import uuid

from google.protobuf.timestamp_pb2 import Timestamp

from run_one.util.config import Config


_T = TypeVar('_T')
uid = str(uuid.uuid1()).replace('-', '')
counter = 0


class Action:

    def __init__(self, row: dict, extra_data: dict) -> None:
        self.row = row
        self.extra_data = extra_data

    def __repr__(self) -> str:
        return f'Action(row={self.row}\nextra_data={self.extra_data})'

    def regenerate_time_fields(self, time_fields: list[str], time_function: Callable):
        time_mapping = {}
        for field in time_fields:
            if field in self.row and self.row[field] != '*':
                self.row[field] = time_mapping.setdefault(self.row[field],
                                                          time_function(self.row[field], self.row, self.extra_data))


def generate_random_id(current_value: str, row: dict, extra_data: dict):
    global counter
    counter += 1
    return f'{uid[:len(current_value) - len(str(counter))]}{counter}'


def generate_time(current_value: str, row: dict, extra_data: dict, time_format: str = '%Y-%m-%dT%H:%M:%S.%fZ'):
    return datetime.now(timezone.utc).strftime(time_format)


def create_timestamp(timestamp_shift) -> Timestamp:
    timestamp = Timestamp()
    timestamp.FromDatetime(datetime.now(timezone.utc) - timedelta(seconds=timestamp_shift))
    return timestamp


def read_csv_matrix(filepath: str,
                    config: Config,
                    id_function: Callable = generate_random_id) -> dict[str, dict[str, list[Action]]]:
    """
    Read matrix file(s)
    :param str filepath: path to matrix file or directory with matrices
    :param config: configuration class instance
    :param id_function: function to transform ID-like fields
    :return: matrices_data: collection of parsed matrices data: matrix file name to test cases data
                            (test case name to list of its actions)
    """

    path = Path(filepath)
    if path.is_dir():
        matrices = sorted(path.glob(config.filename_pattern))
    elif path.is_file():
        matrices = [path]
    else:
        raise FileNotFoundError('No matrices were found at specified path. '
                                'Check `matrix_file` and `filename_pattern` config parameters.')

    csv.field_size_limit(ctypes.c_ulong(-1).value // 2)

    result = {}
    for matrix in matrices:

        test_cases = defaultdict(list)
        test_case_name = ''
        test_case_transformed_ids = {}
        id_mapping = {}

        with open(matrix, 'r', newline='', encoding='utf-8') as file:
            csv_data = csv.DictReader(file)
            row: dict
            for row in csv_data:

                seq = row.get('Seq')
                if seq == 'TEST_CASE_START':
                    test_case_name = row.get('CaseName')
                    continue
                elif seq == 'TEST_CASE_END':
                    test_case_transformed_ids.clear()
                    continue

                action = row.get('Action')

                if action in config.processed_actions:

                    row = {k: v for k, v in row.items() if v != ''}

                    extracted_fields = {field: row[field] for field in config.fields_to_extract if field in row}
                    for field in config.fields_to_drop + config.fields_to_extract:
                        if field in row:
                            row.pop(field)

                    for old_field, new_field in config.field_mapping.items():
                        if old_field in row:
                            row[new_field] = row.pop(old_field)

                    for field in config.nested_fields:
                        if field in row and row[field] != '*':
                            row[field] = ast.literal_eval(row[field])

                    if id_function is not None:
                        for field in config.regenerate_id_fields:
                            if field in row and row[field] != '*':
                                field_value = row[field]
                                if field_value.startswith('!='):
                                    key = field_value[2:]
                                    row[field] = f'''!={test_case_transformed_ids.setdefault(
                                        key, id_function(key, row, extracted_fields))}'''
                                else:
                                    row[field] = test_case_transformed_ids.setdefault(
                                        field_value, id_function(field_value, row, extracted_fields))

                    test_cases[test_case_name].append(Action(row, extracted_fields))
                    id_mapping.update(test_case_transformed_ids)

            matrix_name = matrix.stem
            result[matrix_name] = test_cases
            with open(f'id_mapping_{matrix_name}.csv', 'w', newline='', encoding='utf-8') as id_mapping_file:
                csv_writer = csv.DictWriter(id_mapping_file, fieldnames=['old', 'new'])
                csv_writer.writeheader()
                csv_writer.writerows({'old': k, 'new': v} for k, v in id_mapping.items())

    return result


def pairwise(iterable: Iterable[_T]) -> Iterable[tuple[_T]]:
    """
    Return successive overlapping pairs taken from the input iterable.
    pairwise('ABCDEFG') --> AB BC CD DE EF FG
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
