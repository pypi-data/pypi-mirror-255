### dashboard builder util generate all posibble stats from Dataframe for DataScience and visualisation purposes

```python
from package.dashboardutil import DashboardElementsBuilder
from package.dataclassifier import DataClassifier
import pandas as pd
df=pd.read_csv("cars.csv")
dat=DataClassifier()
visual=DashboardElementsBuilder(df,dat)
ploats=visual.build_ploats("hist",df.columns.to_list()[1:])
ploat_data=[]
for x in list(ploats):
    for z in list(x):
        ploat_data+=list(z)

```

### above data canbe visualised like below

```python
data={'slow': {'lables': [66.2, 66.4, 66.3, 71.4, 67.9], 'counts': [1, 1, 1, 3, 1]}}
from bokeh.plotting import figure, show

fruits = [str(x) for x in data['slow']['lables']]
counts = data['slow']['counts']

p = figure(x_range=fruits, height=350, title="Range",
           toolbar_location=None, tools="")

p.vbar(x=fruits, top=counts, width=0.9)

p.xgrid.grid_line_color = None
p.y_range.start = 0

show(p)

```

### export bulk graphs for all possible conditions

```python
from package.DashBoardsTemplates import export_graphs_hist
from bokeh.plotting import show 
# use any graph for data clustrig or analysis purposes above function using bokeh for bulk visualisation
visual=export_graphs_hist(ploat_data)
# iter visual variable or visualise one by one
show(visual[0])
```

### calucate data formets for visualisation data for formets visulisation purposes

```python
from package.keyborddata import *
from package.formatcalculator import FormatCalculator 
# get hashes chuncks
unique_hashes=FormatCalculator.get_unique_hashes_from_data(ploat_data)
# get combines hashes 
unique_=[]
for x in unique_hashes:
    unique_+=x
```

### calucate data formets for dataframe data for formets data optimisation and validation purposes

```python
from package.keyborddata import *
import pandas as pd
from package.formatcalculator import FormatCalculator
# get df vocabs
vocabdf=FormatCalculator.split_all_labels_to_words_with_new_cols(pd.read_csv("test.csv"))
# get vocabdf formats
formets=FormatCalculator.hash_df_formats(vocabdf)
# get vocabdf formets column wise 
unique_formatas=FormatCalculator.get_unique_hashes_from_df_columnwise(formets)
```

### optimising_regex string

```python
from package.keyborddata import *
import pandas as pd
from package.formatcalculator import FormatCalculator
# get df vocabs
vocabdf=FormatCalculator.split_all_labels_to_words_with_new_cols(pd.read_csv("test.csv"))
# get vocabdf formats
formets=FormatCalculator.hash_df_formats(vocabdf)
# optimise formetts in df
df_list_formetted=[]
for x,y in formets.iterrows():
    for cd in formets.columns.to_list():
        y[cd]=regex_formattor(y[cd])
    df_list_formetted.append(y.to_dict())
# reasamble df with same variable
formets=pd.DataFrame.from_records(df_list_formetted)
# get vocabdf formets column wise 
unique_formatas=FormatCalculator.get_unique_hashes_from_df_columnwise(formets)

```

### generate data mitter

```python

from package.formatcalculator import FormatCalculator
import pandas as pd
import itertools

# reads df from csv
df = pd.read_csv("testdata.csv")
mitter=FormatCalculator.generate_datamiter(df)
mitter._df.to_excel("test.xlsx")
# datamiters optimises data acording to keyboard letters

```

### optimising and manageing large datasets with mitter and row patterns with constructive maths

```python
from package.formatcalculator import FormatCalculator
import pandas as pd
import itertools
import ast

# reads df from csv
df             = pd.read_csv("tw.csv")

mitter         = FormatCalculator.generate_datamiter(df)
a              = mitter.formatwise_mitter()
# get optimised row pattern for data ordring management
a             =  mitter.get_row_ordring_seq_from_dataset(df.head(10),3)


```

###### [Documentation LINK](https://dashboardutils-datascience.readthedocs.io/en/latest/index.html)

### Sponcers Guidelines

##### please send us email to get sponcers docs for this project <rajatsmishra@aol.com>

### Project Contribution GuideLines

##### git page link <https://github.com/rajat45mishra/DashBoardUtils_Datascience>

##### send us update suggestions on <rajatsmishra@aol.com>

#### todo tasks

###### - add more algorithum in data classifier

###### - add more graph templates in DashBoaredtemplates class

###### - use cases docs and api docs for users

###### - totorials for extracting and scripting formats to solve realword software application optimisation purposes
