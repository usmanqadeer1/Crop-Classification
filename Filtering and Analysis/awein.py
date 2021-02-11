tdata = np.loadtxt("punjab_data.txt")

X = tdata[:,0:15]
Y = tdata[:,15]
m = X.shape[0]
n = X.shape[1]
skf = StratifiedKFold(n_splits=10)
classes = 9
CfKNN =np.zeros(classes)
CfDT =np.zeros(classes)
CfGNB =np.zeros(classes)
CfSVM =np.zeros(classes)
CfRF =np.zeros(classes)
filteredX = np.array([]).reshape(0,n)
filteredY = np.array([]).reshape(0,1)
Xkf = np.array([]).reshape(0,n)
Ykf = np.array([]).reshape(0,1)
pknn = np.array([]).reshape(0,1)
pdt = np.array([]).reshape(0,1)
pgnb = np.array([]).reshape(0,1)
psvm = np.array([]).reshape(0,1)
prf = np.array([]).reshape(0,1)
votes = np.array([]).reshape(0,1)
names = ['B1','B2', 'B3', 'B4', 'B5', 'B6','B7','B8','B8A','B9','B10','B11', 'B12','VH','VV'];

for train_index, test_index in skf.split(X,Y):
    
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = Y[train_index], Y[test_index]
    m_test = X_test.shape[0]
    
    #training and testing with knn
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train, y_train)
    predictKNN = knn.predict(X_test)
    cf = confusion_matrix(y_test, predictKNN)
    CfKNN = CfKNN + cf

    # training and testing with tree
    dt = DecisionTreeClassifier()
    dt.fit(X_train, y_train)
    predictDT = dt.predict(X_test)
    cf = confusion_matrix(y_test, predictDT)
    CfDT = CfDT + cf
    
    # training and testing with baysian
    gnb = GaussianNB()
    gnb.fit(X_train, y_train)
    predictGNB = gnb.predict(X_test)
    cf = confusion_matrix(y_test, predictGNB)
    CfGNB = CfGNB + cf
    
    # training and testing with SVM
    svm = SVC(kernel='rbf',gamma='scale') 
    svm.fit(X_train, y_train)
    predictSVM = svm.predict(X_test)
    cf = confusion_matrix(y_test, predictSVM)
    CfSVM = CfSVM + cf
    
    
    #training and testing with RF
    rf = RandomForestClassifier(n_estimators=100)
    rf.fit(X_train, y_train)
    predictRF = rf.predict(X_test)
    cf = confusion_matrix(y_test, predictRF)
    CfRF = CfRF + cf
    
    # get correctly predicted labels based on major voting
    KNNVotes = 1*(predictKNN == y_test)
    DTVotes =  1*(predictDT == y_test)
    GNBVotes = 1*(predictGNB == y_test)
    SVMVotes = 1*(predictSVM == y_test)
    RFVotes = 1*(predictRF == y_test)
    totalVotes = KNNVotes + DTVotes + GNBVotes + SVMVotes + RFVotes
        
    filteredIndices = np.asarray(np.where(totalVotes>=3))
#     filteredIndices = np.asarray(np.where((predictKNN==y_test)|(predictDT==y_test)|(predictGNB==y_test)|(predictSVM==y_test)))
    filteredIndices = filteredIndices.reshape(filteredIndices.shape[1],1)

    filteredXTest = np.take(X_test, filteredIndices, axis = 0)
    filteredXTest = filteredXTest.reshape(filteredXTest.shape[0],filteredXTest.shape[2])
    filteredX = np.concatenate([filteredX,filteredXTest])
    filteredYTest = np.take(y_test,filteredIndices)
    filteredY = np.concatenate([filteredY,filteredYTest])
    
    Xkf = np.concatenate([Xkf,X_test])
    Ykf = np.concatenate([Ykf,y_test.reshape(m_test,1)])
    pknn = np.concatenate([pknn,predictKNN.reshape(m_test,1)])
    pdt = np.concatenate([pdt,predictDT.reshape(m_test,1)])
    pgnb = np.concatenate([pgnb,predictGNB.reshape(m_test,1)])
    psvm = np.concatenate([psvm,predictSVM.reshape(m_test,1)])
    prf = np.concatenate([prf,predictRF.reshape(m_test,1)])
    votes = np.concatenate([votes,totalVotes.reshape(m_test,1)])
    

#confusion matrices of all classifiers
print(CfKNN)
print(CfDT)
print(CfGNB)
print(CfSVM)
print(CfRF)

filteredData = np.concatenate([filteredX,filteredY],axis = 1)
print(filteredData.shape)
print("land: {}".format(np.sum(filteredY == 0)))
print("fallow: {}".format(np.sum(filteredY == 1)))
print("water: {}".format(np.sum(filteredY == 2)))
print("fodder: {}".format(np.sum(filteredY == 3)))
print("wheat: {}".format(np.sum(filteredY == 4)))
print("gram: {}".format(np.sum(filteredY == 5)))
print("maize: {}".format(np.sum(filteredY == 6)))
print("vegetable: {}".format(np.sum(filteredY == 7)))
print("trees: {}".format(np.sum(filteredY == 8)))
filteredData = filteredData[filteredData[:,15].argsort()]
np.savetxt("filtered.csv", filteredData, delimiter=",")

wholeData = np.concatenate([Xkf,Ykf,pknn,pdt,pgnb,psvm,prf,votes],axis = 1)
wholeData = wholeData[wholeData[:,15].argsort()]
np.savetxt("data.csv", wholeData, delimiter=",",header="B1,B2,B3,B4,B5,B6,B7,B8,B8A,B9,B10,B11,B12,VV,VH,Y,KNN,DT,GNB,SVM,RF,Votes")


