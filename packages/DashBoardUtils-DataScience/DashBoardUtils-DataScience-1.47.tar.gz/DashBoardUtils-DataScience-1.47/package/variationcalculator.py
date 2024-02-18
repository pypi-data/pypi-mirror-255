# process veriations calculator
import ast
import pandas as pd


class VERIATIONS:
    def __init__(self, columnsTable: pd.DataFrame, RowTable: pd.DataFrame) -> None:
        """_summary_

        Args:
            columnsTable (pd.DataFrame): _description_
            RowTable (pd.DataFrame): _description_
        """
        self.columnsTable = columnsTable
        self.RowTable = RowTable

    def formats_and_no_of_patterns(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        col = {}
        for i, v in self.columnsTable.iterrows():
            cd = self.columnsTable.columns.to_list()
            for c in cd:
                sw = None
                try:
                    sw = ast.literal_eval(v[c])
                except Exception as E:
                    sw = v[c]
                if isinstance(sw, list):
                    col[c] = len(sw)
                else:
                    col[c] = 1
        return col

    def row_sequance_veriations(self):
        """_summary_

        Returns:
            columns: list of columns seq veriations
        """
        veriations = []
        for i, v in enumerate(self.RowTable.columns.to_list()):
            s, d = v.split("|")
            s = s.split("+")
            d = d.split("+")
            s = [x.split("?") if "?" in x else [x] for x in s]
            d = [x.split("?") if "?" in x else [x] for x in d]
            veriations.append({i: [s, d]})
        return veriations
