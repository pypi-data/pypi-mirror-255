"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author: 18317
@Date Created: 09/02/2024
@Description :
"""
import seaborn as sns
import matplotlib.pyplot as plt

# 加载数据集
tips = sns.load_dataset("tips")

# 创建一个散点图，展示小费与总账单之间的关系
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="time", style="time")

# 显示图表
plt.show()
