from pathlib import Path

import ezdxf
from openpyxl import Workbook


class ExtractTable:

    def __init__(self, structure: tuple, input_dir: Path, output_dir: Path):
        sorted_structure = sorted(structure, key=lambda x: x[0])
        self._columns = [item[1] for item in sorted_structure]
        self._input_dir = input_dir
        self._output_dir = output_dir

    def _dxf_parse(self, dxf_filepath: Path):
        doc = ezdxf.readfile(dxf_filepath.absolute())
        mt_list = [[mt.plain_text().replace('\n', ' '), mt.dxf.insert[1], mt.dxf.insert[0]] for mt in
                   doc.modelspace().query('MTEXT')]
        mt_list_sorted_by_x = sorted(mt_list, key=lambda m: m[1])[::-1]
        name_group = mt_list_sorted_by_x.pop(0)[0]

        n_coloumns = 5
        data_array = [mt_list_sorted_by_x[i:i + n_coloumns] for i in range(0, len(mt_list_sorted_by_x), n_coloumns)]
        for idx, row in enumerate(data_array):
            data_array[idx] = sorted(data_array[idx], key=lambda m: m[2])
        table_array = []
        for row in data_array:
            table_array.append([mt[0] for mt in row])

        return table_array, name_group

    def _xls_write(self, data: list, path: Path):
        wb = Workbook()
        ws = wb.active
        ws.title = "Table Data"

        # Записываем данные
        for i, row in enumerate(data, start=1):
            for j, value in enumerate(row, start=1):
                ws.cell(row=i, column=j, value=value)

        wb.save(path)

    def extraction(self):
        for file in self._input_dir.glob("*.dxf"):
            data, xls_filename = self._dxf_parse(file)
            data.insert(0, self._columns)
            self._xls_write(data, self._output_dir / (xls_filename + '.xlsx'))