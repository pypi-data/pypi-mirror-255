# -*- coding: utf-8 -*-

import pydatamodel.creditScore as creditScore
import pydatamodel.dataAnalysis as dataAnalysis
import pydatamodel.databaseModel as databaseModel
print("欢迎使用pydatamodel，模块说明：creditScore:评分卡模块，mechineLearning：机器学习模块，dataAnalysis：数据分析模块，databaseModel：数据库处理模块")
try:
    import pydatamodel.mechineLearning as mechineLearning
except ImportError:
    print('mechineLearning模块中，以下库是必须的，\
          你可能缺少了其中的一个或者多个：xlsxwriter、joblib、xgboost、openpyxl。如你不使用mechinelearning模块则无需理会本提示。')

__all__=['creditScore','dataAnalysis','databaseModel','mechineLearning']
