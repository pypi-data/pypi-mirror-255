"""Dashboared Elements builder

    Raises:
        ValueError: data validation

    Returns:
        List: list

    Yields:
        List: list
    """

from datetime import datetime
import pandas as pd


class DashboardElementsBuilder:
    """DashboardElementsBuilder build data
    visualisation elements on behalf of DataFrame"""

    def __init__(self, data, DataClassifier) -> None:
        if isinstance(data, pd.DataFrame):
            self.data = data
        else:
            raise ValueError("data should be instance of Dataframe")
        self.classifier = DataClassifier

    def prepare_sections(self, columns):
        """selects required cols"""
        filters = self.data[columns]
        return filters

    def get_columns_groups(self, columns):
        """Builds Groups on Behalf of all
        possible Catagories of Data"""
        alldata_groups = []
        for _x in columns:
            if not isinstance(self.prepare_sections(columns)[_x], datetime):
                alldata_groups.append(self.prepare_sections(columns).groupby([_x]))
            else:
                alldata_groups.append(
                    self.prepare_sections(columns).groupby(
                        by=[
                            getattr(self.prepare_sections(columns), _x).month,
                            getattr(self.prepare_sections(columns), _x).year,
                        ]
                    )
                )
                alldata_groups.append(
                    self.prepare_sections(columns).groupby(
                        by=[
                            getattr(self.prepare_sections(columns), _x).day,
                            getattr(self.prepare_sections(columns), _x).month,
                        ]
                    )
                )
                alldata_groups.append(
                    self.prepare_sections(columns).groupby(
                        by=[getattr(self.prepare_sections(columns), _x).month]
                    )
                )
                alldata_groups.append(
                    self.prepare_sections(columns).groupby(
                        by=[getattr(self.prepare_sections(columns), _x).day]
                    )
                )
                alldata_groups.append(
                    self.prepare_sections(columns).groupby(
                        by=[getattr(self.prepare_sections(columns), _x).year]
                    )
                )
                alldata_groups.append(
                    self.prepare_sections(columns).groupby(
                        by=[
                            getattr(self.prepare_sections(columns), _x).day,
                            getattr(self.prepare_sections(columns), _x).year,
                        ]
                    )
                )
        return alldata_groups

    def build_ploats(self, algorithm, columns):
        """generate ploat data for user provided algorithm,columns"""
        for _x in self.get_columns_groups(columns):
            yield self.classifier.build_ploats(algorithm, _x)
