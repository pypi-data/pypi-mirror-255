from cross_border_mover import alibabaScraper
from cross_border_mover import pddScraper
from cross_border_mover import taobaoScraper
from cross_border_mover import amazonListing
from cross_border_mover import wishListing
import pandas as pd

class Mover:
    def __init__(self, colorList = [], sizeList = []):
        self.colorList = colorList
        self.sizeList = sizeList
        

    def toAmazon(self, columns, df_preAmz):
        # 将商品数据从指定平台的URL上传到亚马逊的代码逻辑
        # ...
        # sku数据填充
        assert len(self.colorList) > 0, '颜色列表不能为空'
        assert len(self.sizeList) > 0, '尺寸列表不能为空'
        assert len(columns) > 0, '列名不能为空'
        df_meta = pd.DataFrame(columns=['中文尺码','中文颜色','图片地址'], index=range(max(len(self.colorList),len(self.sizeList))))

        colorTitles = [item['title'] for item in self.colorList]
        imageUrls = [item['url'] for item in self.colorList]
        
        df_meta['中文尺码'] = pd.Series( [size for size in self.sizeList])
        df_meta['中文颜色'] = pd.Series( [title for title in colorTitles])
        df_meta['图片地址'] = pd.Series( [url for url in imageUrls])
        df_meta['图片'] = pd.Series( [f'=IMAGE("{url}")' for url in imageUrls])
        
        # df_meta['中文尺码'] =  [size for size in self.sizeList]
        # df_meta['中文颜色'] =  [title for title in colorTitles]
        # df_meta['图片地址'] =  [url for url in imageUrls]
        # df_meta['图片'] =  [f'=IMAGE("{url}")' for url in imageUrls]
        
        
        
        
        df_amazon = amazonListing.generate_listing_dataframe(columns, df_meta, df_preAmz)
        
        
        return df_meta, df_amazon
        # amazonListing.po(self)
        
    def toWish(self):
        # 将商品数据从指定平台的URL上传到Wish的代码逻辑
        # ...
        wishListing.po(self)



    @staticmethod
    def fromTaobao(url):
        # 从淘宝平台创建Mover对象的代码逻辑
        # ...
        colorList, sizeList = taobaoScraper.getSKUInfo(url)

        # 创建Mover对象并返回
        mover = Mover(colorList, sizeList)

        return mover
        

    @staticmethod
    def fromPDD(url):
        # 从拼多多平台创建Mover对象的代码逻辑
        # ...
        colorList, sizeList = pddScraper.getSKUInfo(url)

        # 创建Mover对象并返回
        mover = Mover(colorList, sizeList)

        return mover
        

    @staticmethod
    def from1688(url):
        # 从1688平台创建Mover对象的代码逻辑
        # ...
        # sku采集
        colorList, sizeList = alibabaScraper.getSKUInfo(url)

        # 创建Mover对象并返回
        mover = Mover(colorList, sizeList)

        return mover
