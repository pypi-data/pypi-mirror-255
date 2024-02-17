"""dataclassifier

    Raises:
        NotImplementedError: implementation pending

    Yields:
        List: returns list
    """
PACKAGEMODULE = "package.DataClassifier"


class DataClassifier:
    """DataClassifier classification Data in Defined  algorithm
      and and their classification format \n
    -- We can define of algorithum \n
    -- build data classification Process for build data groups"""

    def __init__(self, algorithm=None) -> None:
        """We can define of algorithum"""
        if algorithm is None:
            self.algorithm = [
                {"algorithm": "hist", "Format": ["Catagorical", "Length"]}
            ]
        else:
            self.algorithm = algorithm

    def build_ploats(self, algorithm, groups):
        """build data classification Process for build data groups"""
        getalgo = [x for x in self.algorithm if algorithm in list(x.values())][0]
        for name, group in groups:
            print("finding catagories for {}".format(name))
            catagorical = []
            for _x in group.columns.to_list():
                if group[_x].nunique() > 1:
                    catagorical.append(
                        {
                            _x: {
                                "lables": [str(x) for x in group[_x].unique().tolist()],
                                "counts": [
                                    len(group[group[_x] == xs])
                                    for xs in group[_x].unique().tolist()
                                ],
                            }
                        }
                    )
            if getalgo["algorithm"] == "hist":
                yield catagorical
            else:
                raise NotImplementedError("use hist for now")
