import pandas as pd
from slugify import slugify
import re

def create_ids(df, pattern="{}"):
    def to_id(row):
        id = "_".join(row)
        return slugify(pattern.format(id))

    ids = df.apply(to_id, axis=1)
    dups = ids.groupby(ids).rank(method="first", ascending=False).apply(lambda x: "" if x == 1 else str(int(x)))
    return ids + dups

def segment_sounds(col, sounds):
    def splitter(series, split_pattern):
        series = series.str.split(pat=split_pattern, regex=True)
        return series.apply(lambda x: " ".join([char for char in x if char]))

    defs = col == "#DEF#"
    split_pattern = re.compile("(" + "|".join(sorted(sounds, key=len, reverse=True)) + ")")
    segmented = col.copy()
    segmented[~defs] = splitter(segmented[~defs], split_pattern)
    return segmented