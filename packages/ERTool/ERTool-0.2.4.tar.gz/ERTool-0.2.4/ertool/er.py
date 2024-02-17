import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def er_algorithm(W, DBF, numOfEvidence, numOfPropositions):
    """
    Input Variables:
        - W: A one-dimensional array of floats. It represents the weights of each piece of evidence. These weights are used in the algorithm to adjust the influence of each evidence.
        - DBF: A two-dimensional array of floats. It stands for "Degrees of Belief" and is one of the main inputs to the algorithm, used to represent the initial belief degree of each proposition supported by each evidence.
        - numOfEvidence: An integer. It indicates the number of evidence to be combined. In the DBF array, this typically corresponds to the number of rows.
        - numOfPropositions: An integer. It indicates the number of propositions or evidential grades. In the DBF array, this typically corresponds to the number of columns.
    Output Values:
        - B Array: Upon completion of the algorithm, the B array is updated with the final calculation results. It reflects the degree of belief of each proposition or evidential grades for the object being assessed after combining all available evidence. The pre-Numofproposition values in the B represent the belief degree of each proposition after evidence fusion. The last value of the B represents the belief degree of the global uncertainty.
        - False (Boolean): It returns True if the algorithm successfully executes and completes all computations. If any error is encountered during execution (e.g., division by zero), it returns False.
    """
    # 对输入进行检测
    if len(DBF) != numOfEvidence or len(DBF[0]) != numOfPropositions or numOfEvidence < 1 or numOfPropositions < 1:
        print("An error occurred during the execution of the algorithm.")
        print(" | The input variables are incorrect. Please check them again. | ")
        return False
    
    # 将数组转换为 numpy array
    if not isinstance(W, np.ndarray):
        W = np.array(W)
    if not isinstance(DBF, np.ndarray):
        DBF = np.array(DBF)

    # 归一化 W 数组
    sngSum = W.sum()
    if sngSum == 0:
        strErrorMessage += " | Divided by 0 (sngSum) in er_algorithm. | "
    else:
        W  = W / sngSum

    # 初始化变量
    B = np.zeros(numOfPropositions+1)
    strErrorMessage = ""
    MTilde = numOfPropositions
    MBar = numOfPropositions + 1
    ng2 = numOfPropositions + 2

    # 创建一个二维数组 M
    M = np.zeros((numOfEvidence, ng2), dtype=float)

    # 将 DBF 数组赋值到 M 矩阵
    for i in range(numOfEvidence):
        for j in range(numOfPropositions):
            M[i, j] = DBF[i, j]

    # 计算概率分布的不完备因子
    for i in range(numOfEvidence):
        sngIncomplete = np.sum(M[i, :numOfPropositions])
        M[i, MTilde] = W[i] * (1.0 - sngIncomplete)  # m(theta,i)
        M[i, MBar] = 1.0 - W[i]  # m(P(theta),i)

    # 利用权重更新 M 矩阵中的概率分配
    for i in range(numOfEvidence):
        for j in range(numOfPropositions):
            M[i, j] *= W[i]

    # 赋初值
    B[:numOfPropositions] = M[0, :numOfPropositions]
    B[MTilde] = M[0, MTilde]
    BBar = M[0, MBar]

    # 递归地融合所有evidence，并根据概率分配不完备因子和权重因子
    for r in range(1, numOfEvidence):
        K = 1.0 - np.sum([B[i] * M[r, j] for i in range(numOfPropositions) for j in range(numOfPropositions) if j != i])
        if K != 0:
            K = 1.0 / K
        else:
            strErrorMessage += " | Divided by 0 (K) in er_algorithm. | "

        for n in range(numOfPropositions):
            B[n] = K * (B[n] * M[r, n] + B[n] * (M[r, MTilde] + M[r, MBar]) + (B[MTilde] + BBar) * M[r, n])

        B[MTilde] = K * (B[MTilde] * M[r, MTilde] + BBar * M[r, MTilde] + B[MTilde] * M[r, MBar])
        BBar = K * BBar * M[r, MBar]

    # 归一化置信度
    sngNormal = 1.0 - BBar
    if sngNormal != 0:
        B /= sngNormal
    else:
        strErrorMessage += " | Divided by 0 (sngNormal) in er_algorithm. | "

    # 检查是否有错误信息
    if strErrorMessage:
        print("An error occurred during the execution of the algorithm.")
        print(strErrorMessage)
        return False
    else:
        return B


def dempster_shafer(DBF, numOfEvidence, numOfPropositions):
    """
    Input Variables:
        - DBF: A two-dimensional array of floats. It stands for "Degrees of Belief" and is one of the main inputs to the algorithm, used to represent the initial belief degree of each proposition supported by each evidence.
        - numOfEvidence: An integer. It indicates the number of evidence to be combined. In the DBF array, this typically corresponds to the number of rows.
        - numOfPropositions: An integer. It indicates the number of propositions or evidential grades. In the DBF array, this typically corresponds to the number of columns.
    Output Values:
        - B Array: Upon completion of the algorithm, the B array is updated with the final calculation results. It reflects the degree of belief of each proposition or evidential grades for the object being assessed after combining all available evidence. The pre-Numofproposition values in the B represent the belief degree of each proposition after evidence fusion. The last value of the B represents the belief degree of the global uncertainty.
        - False (Boolean): It returns True if the algorithm successfully executes and completes all computations. If any error is encountered during execution (e.g., division by zero), it returns False.
    """

    if len(DBF) != numOfEvidence or len(DBF[0]) != numOfPropositions or numOfEvidence < 1 or numOfPropositions < 1:
        print("An error occurred during the execution of the algorithm.")
        print(" | The input variables are incorrect. Please check them again. | ")
        return False
    
    B = np.zeros(numOfPropositions+1)
    
    if not isinstance(DBF, np.ndarray):
        DBF = np.array(DBF)

    W = [1] * numOfEvidence

    strErrorMessage = ""
    MTilde = numOfPropositions
    MBar = numOfPropositions + 1
    ng2 = numOfPropositions + 2

    M = np.zeros((numOfEvidence, ng2), dtype=float)

    for i in range(numOfEvidence):
        for j in range(numOfPropositions):
            M[i, j] = DBF[i, j]

    for i in range(numOfEvidence):
        sngIncomplete = np.sum(M[i, :numOfPropositions])
        M[i, MTilde] = W[i] * (1.0 - sngIncomplete)
        M[i, MBar] = 1.0 - W[i]

    for i in range(numOfEvidence):
        for j in range(numOfPropositions):
            M[i, j] *= W[i]

    B[:numOfPropositions] = M[0, :numOfPropositions]
    B[MTilde] = M[0, MTilde]
    BBar = M[0, MBar]

    for r in range(1, numOfEvidence):
        K = 1.0 - np.sum([B[i] * M[r, j] for i in range(numOfPropositions) for j in range(numOfPropositions) if j != i])
        if K != 0:
            K = 1.0 / K
        else:
            strErrorMessage += " | Divided by 0 (K) in er_algorithm. | "

        for n in range(numOfPropositions):
            B[n] = K * (B[n] * M[r, n] + B[n] * (M[r, MTilde] + M[r, MBar]) + (B[MTilde] + BBar) * M[r, n])

        B[MTilde] = K * (B[MTilde] * M[r, MTilde] + BBar * M[r, MTilde] + B[MTilde] * M[r, MBar])
        BBar = K * BBar * M[r, MBar]

    sngNormal = 1.0 - BBar
    if sngNormal != 0:
        B /= sngNormal
    else:
        strErrorMessage += " | Divided by 0 (sngNormal) in er_algorithm. | "

    if strErrorMessage:
        print("An error occurred during the execution of the algorithm.")
        print(strErrorMessage)
        return False
    else:
        return B

def show_er_result(B, P = None, fig_name = "Visualization of the ER-based Calculation Results", xlabel_name = "Propositions", ylabel_name = "Belief Degree"):
    if P is None:
        P = ["Proposition "+str(i) for i in range(1,len(B))]
    P = P + ["Global Uncertainty"]
    # 创建柱状图
    plt.figure(figsize=(10, 6))
    bars = plt.bar(P, B, color = plt.get_cmap('Pastel1')(range(len(P))))

    # 添加标题和标签
    plt.title(fig_name, fontsize=14)
    plt.xlabel(xlabel_name, fontsize=12)
    plt.ylabel(ylabel_name, fontsize=12)

    # 设置y轴的范围
    plt.ylim(0, 1)

    # 为每个条形图添加数值标签
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 4), ha='center', va='bottom', fontsize=10)

    # 显示图表
    plt.show()


def run_algorithm_from_file(file_path, algorithm = 'ER', fig_name = "Visualization of the ER-based Calculation Results", xlabel_name = "Propositions", ylabel_name = "Belief Degree"):
    '''
    Input Variables:
        - file_path: A string. The address of the csv or xlsx file. Note that the format of data strictly follows the format of the template.
        - algorithm: 'ER' or 'DS'. ER' stands for using the evidence inference algorithm, and 'DS' stands for using the Dempster-Shafer algorithm.
    Output Values:
        - B Array: Upon completion of the algorithm, the B array is updated with the final calculation results. It reflects the degree of belief of each proposition or evidential grades for the object being assessed after combining all available evidence. The pre-Numofproposition values in the B represent the belief degree of each proposition after evidence fusion. The last value of the B represents the belief degree of the global uncertainty.
        - False (Boolean): It returns True if the algorithm successfully executes and completes all computations. If any error is encountered during execution (e.g., division by zero), it returns False.
    '''
    # 根据文件扩展名决定使用的读取方法
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == '.csv':
        df = pd.read_csv(file_path)
    elif file_extension.lower() == '.xlsx':
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a .csv or .xlsx file.")
    
    # ER算法
    if algorithm == 'ER':
        # 计算numOfEvidence和numOfPropositions
        numOfEvidence = len(df)
        numOfPropositions = len(df.columns) - 2

        # 提取DBF矩阵
        DBF = df.iloc[:, 2:].to_numpy()

        # 提取W数组
        W = df['Weight'].to_numpy()

        # 提取P数组
        P = df.columns[2:].tolist()

        # 调用函数
        B = er_algorithm(W, DBF, numOfEvidence, numOfPropositions)

    # dempster_shafer算法
    elif algorithm == 'DS':
        # 计算numOfEvidence和numOfPropositions
        numOfEvidence = len(df)
        numOfPropositions = len(df.columns) - 1

        # 提取DBF矩阵
        DBF = df.iloc[:, 1:].to_numpy()

        # 提取P数组
        P = df.columns[1:].tolist()

        # 调用函数
        B = dempster_shafer(DBF, numOfEvidence, numOfPropositions)

    if B is not None:
        show_er_result(B, P, fig_name, xlabel_name, ylabel_name)

    return B