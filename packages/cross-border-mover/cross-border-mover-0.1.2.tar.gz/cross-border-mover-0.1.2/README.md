
# About
A Cross-Border E-Commerce Mover 跨境电商搬运工

# Goal
Making cross-border business easy worldwide

# cross-border-mover
A Cross-border E-commerce Mover

# desgin
![](https://raw.githubusercontent.com/chenzilu1990/PicGo-imgur/main/readmeImage429bf96330957a295388dc5d7a18ba8.jpg)
# Features
- scrape
- translate
- extra-batch-images with sdwebuiapi
- use pandas auto fill amazon listing excel
# Planned Features:
- title generate by AI
# Install

```
python -m pip install cross-border-mover
```

# Usage

open .\XXBand.xlsm with Excel first

```
form cross-border-mover import Mover

# move from taobao to amazon
df_amazon = Mover.fromTaobao(url).toAmazon()

# move from pinduoduo to amazon
df_amazon = Mover.fromPDD(url).toAmazon()

# move from 1688 to amazon
df_amazon = Mover.from1688(url).toAmazon()

# move from taobao to Wish
df_wish = Mover.fromTaobao(url).toWish()

# move from pinduoduo to Wish
df_wish = Mover.fromPDD(url).toAmazon()

# move from 1688 to Wish
df_wish = Mover.from1688(url).toWish()

```
                                                                                                                                                                                                                                                                              



