from deep_translator import GoogleTranslator
import mws
import pandas as pd
import numpy as np
import math
def po(product):
    # 将商品数据从指定平台的URL上传到亚马逊的代码逻辑
    # ...

    # 创建亚马逊MWS客户端
    amazon_access_key = "您的亚马逊访问密钥"
    amazon_secret_key = "您的亚马逊密钥"
    amazon_seller_id = "您的亚马逊卖家ID"
    amazon_marketplace_id = "您的亚马逊市场ID"

    client = mws.Products(access_key=amazon_access_key,
                          secret_key=amazon_secret_key,
                          account_id=amazon_seller_id,
                          region='US',
                          marketplaceids=[amazon_marketplace_id])

    # 创建商品信息
    product = {
        'sku': '商品SKU',
        'product_id': '商品ID',
        'price': '商品价格',
        'quantity': '商品数量',
        # 其他商品信息...
    }

    # 刊登商品
    response = client.submit_feed(
        feed=product,
        feed_type='_POST_PRODUCT_DATA_'
    )

    # 处理刊登结果
    if response.status_code == 200:
        print("商品刊登成功！")
    else:
        print("商品刊登失败。错误信息：", response.text)

def generate_listing_dataframe(columns, df_meta, df_preAmz):
    
    sku_qty = df_meta['中文颜色'].count() * df_meta['中文尺码'].count()
    colorUrls = df_meta['图片地址'].dropna().tolist()
    
    # pic_url_prefix = "https://raw.githubusercontent.com/chenzilu1990/PicGo-imgur/main/"    
    # pic_url_prefix = "https://myway-images.s3.ap-northeast-1.amazonaws.com/" + 
    # assert df_preAmz['item_sku'][0]
    
    assert isinstance(df_preAmz['item_sku'][0], str), "df_preAmz['item_sku'][0]不是字符串"     
    assert df_preAmz['item_sku'][0] != '', "df_preAmz['item_sku'][0]为空"
         
    parent_sku = df_preAmz['item_sku'][0]
    title = df_preAmz['item_name'][0]
    #  变体颜色尺码翻译
    colors_en = GoogleTranslator().translate_batch(df_meta['中文颜色'].dropna().tolist())
    sizes_en = GoogleTranslator().translate_batch(df_meta['中文尺码'].dropna().tolist())

    
    df_amazon = pd.DataFrame(index=range(sku_qty+1), columns=columns )
    # 动态添加列

    
    for col in df_preAmz:
        if (isinstance(col, str)):
           df_amazon[col] = df_preAmz[col][0] 
    
    
    # 基本
    df_amazon['item_sku'] = [parent_sku] + [parent_sku + f'{i:03}' for i in range(1, sku_qty + 1)]

    df_amazon.loc[0,'quantity'] = np.nan
    df_amazon.loc[0,'standard_price'] = np.nan

    # 图片
    
    # df_amazon['main_image_url'] = pic_url_prefix + df_amazon['item_sku'] + '.jpg'
    df_amazon['main_image_url'] =  pd.Series( [colorUrls[0] ]+ [url for url in colorUrls] * df_meta['中文尺码'].count())
    # df_amazon['other_image_url1'] = pic_url_prefix + df_amazon['item_sku'] + '.TP01.jpg'
    # df_amazon['other_image_url2'] = pic_url_prefix + df_amazon['item_sku'] + '.TP02.jpg'
    df_amazon['swatch_image_url'] =  pd.Series( [colorUrls[0] ]+ [url for url in colorUrls] * df_meta['中文尺码'].count())

    # 变体信息
    df_amazon.loc[0,'relationship_type'] = np.nan
    df_amazon.loc[0,'parent_sku'] = np.nan
    df_amazon.loc[0,'parent_child'] = 'Parent'

    # 商品发现信息

    df_amazon['color_name'] = [np.nan] + [colors_en[(i - 1) % colors_en.__len__()] for i in range(1, sku_qty + 1)]
    df_amazon['size_name'] = [np.nan] + [sizes_en[math.floor(((i - 1) / colors_en.__len__()))] for i in range(1, sku_qty + 1)]


    df_amazon.loc[0,'list_price'] = np.nan
    df_amazon.loc[0,'item_package_quantity'] = np.nan
    df_amazon.loc[0,'merchant_shipping_group_name'] = np.nan
    df_amazon.loc[0,'condition_type'] = np.nan
    df_amazon.loc[0,'sale_price'] = np.nan
    df_amazon.loc[0,'sale_from_date'] = np.nan
    df_amazon.loc[0,'sale_end_date'] = np.nan

    assert isinstance(title, str), "没有标题"
    df_amazon['item_name'] = [title] + [title.replace('[color]', df_amazon['color_name'][i]).replace('[size]', df_amazon['size_name'][i]) for i in range(1, sku_qty + 1)]

    return df_amazon




# generate by pyminifier (  
#     "cross-border-mover/amazonListing.py"
# )
def generate_listing_excel(products):
    # Convert the product data into a pandas DataFrame
    df = pd.DataFrame(products)

    # Save the DataFrame to an Excel file
    excel_file_path = '/path/to/listing.xlsx'
    df.to_excel(excel_file_path, index=False)

    print("Listing Excel file generated successfully!")

# Example usage
products = [
    {'sku': 'SKU1', 'product_id': 'ID1', 'price': 10.99, 'quantity': 100},
    {'sku': 'SKU2', 'product_id': 'ID2', 'price': 19.99, 'quantity': 50},
    # Add more products as needed
]

# generate_listing_excel(products)


