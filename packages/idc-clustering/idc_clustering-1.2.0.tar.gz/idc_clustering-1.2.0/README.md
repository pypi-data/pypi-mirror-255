# gitee-clustering

#### 介绍
创新性的把聚类算法（k-means和dbscan）通过模型测算原理，把学习数据输入模型计算，同时把学习数据类别输入模型标注，当需要知道训练数据具体属于哪一类时，模型会自动计算，并输出所属分类数据的标签。

#### 软件架构
软件架构说明


#### 安装教程

1.  库安装：pip install idc_clustering
2.  库调用:  
          from idc_clustering.idc import *
          print(idc())

#### 使用说明

1.  调用库函数后根据Console界面提示操作
2.  基于本算法可以计算多维数据空间点间的距离，寻求到最小距离点间距，并反馈出所属分类标签。
3.  “提示：按回车键开始选择待学习的数据！”待输入表格的格式为.CSV格式，表头为待学习数据列列名，待学习数据从第二行开始。
4.  “提示：输入真实的分类数量，并按回车键继续！”含义：待学习的数据有多少种分类。建议把待学习的数据提前按类别排序，相同类别的数据紧密连接，并记录每个类别索引切片。
5.  “提示：输入分类1所属分类类别名称，按回车键继续！”含义：即输入第一个类别的分类名称
6.  “提示：分类1开始行索引，按回车键继续！”，“提示：分类1结束行索引，按回车键继续！”含义：第一个分类的开始行索引（默认从0开始索引），第一个分类的结束行索引（结束行索引=开始行索引+该分类数据的数量，例如开始行索引=0，则结束行索引=0+该分类数据的数量），其他分类以此类推。

#### Instructions for use
1.  After calling the library function, follow the console interface prompts.
2.  Based on this algorithm, the distance between points in multi-dimensional data space can be calculated, the minimum distance between points can be found, and the corresponding classification label can be fed back.
3.  "Tip: Press the Enter key to start selecting the data to be learned! The format of the table to be input is .CSV format. The header is the column name of the data to be learned, and the data to be learned starts from the second row.
4.  "Tip: Enter the actual number of categories and press Enter to continue!" Meaning: How many categories are there in the data to be learned.It is recommended that the data to be learned be sorted by category in advance, data of the same category be closely connected, and each category index slice be recorded.
5.  "Tip: Enter the name of the category to which Category 1 belongs and press Enter to continue!&quot; Meaning: Enter the category name of the first category
6.  "Tip: Category 1 starts the row index, press Enter to continue!&quot;, &quot;Prompt: Category 1 ends the row index, press Enter to continue!&quot; Meaning: The starting row index of the first category (index starts from 0 by default) , the ending row index of the first category (ending row index = starting row index + the number of data in this category, for example, starting row index = 0, then ending row index = 0 + the number of data in this category), and so on for other categories .


