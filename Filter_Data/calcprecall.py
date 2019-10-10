def calcprecall(cf, classes):
    TP = np.diag(cf)
    FP = np.sum(cf, axis=0) - TP
    FN = np.sum(cf, axis=1) - TP

    accuracy = np.sum(TP/np.sum(np.sum(cf)))/classes
    precision = np.sum(TP / (TP + FP))/classes
    recall = np.sum(TP / (TP + FN))/classes
    F1score = (precision+recall)/(2*precision*recall)
    
    return accuracy, precision, recall, F1score