# Marie's Magic Functions

## Pandas

### Combine Collumns

Given a pandas table

```py
import pandas as pd

from mariem.pandas import combine_collumns

df = pd.DataFrame(
    {
        "a": [1, 2, 3],
        "b": [4, 5, 6],
        "c": [7, 8, 9],
    }
)
```

```
   a  b  c
0  1  4  7
1  2  5  8
2  3  6  9
```

the columns `a` and `b` can be combined with

```py
new_df = combine_collumns(df, ["a", "b"], "category", "value")
```

```
   c category  value
0  7        a      1
1  7        b      4
2  8        a      2
3  8        b      5
4  9        a      3
5  9        b      6
```