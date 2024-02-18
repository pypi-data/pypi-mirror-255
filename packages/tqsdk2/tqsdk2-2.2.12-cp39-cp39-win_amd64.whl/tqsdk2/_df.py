#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'chengzhi'

import pandas as pd
from pandas.core.internals import BlockManager
from pandas._libs.internals import BlockPlacement
if tuple(map(int, pd.__version__.split("."))) < (1, 3, 0):
    from pandas.core.internals import FloatBlock
else:
    from pandas.core.internals import NumericBlock as FloatBlock


class BlockManagerUnconsolidated(BlockManager):
    """mock BlockManager for unconsolidated, 不会因为自动合并同类型的 blocks 而导致 k 线数据不更新"""
    def __init__(self, *args, **kwargs):
        BlockManager.__init__(self, *args, **kwargs)
        self._is_consolidated = False
        self._known_consolidated = False

    def _consolidate_inplace(self): pass


def get_dataframe(columns, arrays, size):
    blocks = [FloatBlock(values=arrays[i], ndim=2, placement=BlockPlacement(slice(i, i+1))) for i in range(len(arrays))]
    bm = BlockManagerUnconsolidated(blocks=blocks, axes=[pd.Index(columns), pd.RangeIndex(0, size)])
    df = pd.DataFrame(bm, copy=False)
    org_get_item_cache = df._get_item_cache

    def _get_item_cache(self, item):
        # 由于底层 numpy 的数据地址会有变化, 因此禁用对应列的缓存
        res = org_get_item_cache(item)
        if item in columns:
            self._item_cache.pop(item, None)
        return res

    df._get_item_cache = _get_item_cache.__get__(df, pd.DataFrame)
    return df
