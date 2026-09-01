
from django.shortcuts import render, redirect, get_object_or_404
import pandas            as pd
from sklearn.metrics import classification_report,accuracy_score,confusion_matrix




# Create your views here.
from Remote_User.models import ClientRegister_Model,water_quality_type,detection_ratio,detection_accuracy

def login(request):


    if request.method == "POST" and 'submit1' in request.POST:

        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            enter = ClientRegister_Model.objects.get(username=username,password=password)
            request.session["userid"] = enter.id

            return redirect('ViewYourProfile')
        except:
            pass

    return render(request,'RUser/login.html')

def Register1(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phoneno = request.POST.get('phoneno')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        ClientRegister_Model.objects.create(username=username, email=email, password=password, phoneno=phoneno,
                                            country=country, state=state, city=city, address=address, gender=gender)

        obj = "Registered Successfully"
        return render(request, 'RUser/Register1.html',{'object':obj})
    else:
        return render(request,'RUser/Register1.html')

def ViewYourProfile(request):
    userid = request.session['userid']
    obj = ClientRegister_Model.objects.get(id= userid)
    return render(request,'RUser/ViewYourProfile.html',{'object':obj})


def Predict_Water_Quality(request):
    if request.method == "POST":

        if request.method == "POST":

            State_Name = request.POST.get('State_Name')
            District_Name = request.POST.get('District_Name')
            Block_Name = request.POST.get('Block_Name')
            Panchayat_Name = request.POST.get('Panchayat_Name')
            Village_Name = request.POST.get('Village_Name')
            Habitation_Name = request.POST.get('Habitation_Name')
            Year = request.POST.get('Year')

        df = pd.read_csv('Water_Quality_Datasets.csv', encoding='latin-1')

        def apply_results(results):
            if (results == 'Salinity'):
                return 0
            elif (results == 'Fluoride'):
                return 1
            elif (results == 'Iron'):
                return 2
            elif (results == 'Arsenic'):
                return 3
            elif (results == 'Nitrate'):
                return 4

        df['results'] = df['Quality_Parameter'].apply(apply_results)

        X = df['Habitation_Name']
        y = df['results']
        from sklearn.feature_extraction.text import CountVectorizer
        cv = CountVectorizer(lowercase=False, strip_accents='unicode', ngram_range=(1, 1))

        x = cv.fit_transform(X)


        models = []
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.20)
        X_train.shape, X_test.shape, y_train.shape

        print("Naive Bayes")

        from sklearn.naive_bayes import MultinomialNB

        NB = MultinomialNB()
        NB.fit(X_train, y_train)
        predict_nb = NB.predict(X_test)
        naivebayes = accuracy_score(y_test, predict_nb) * 100
        print("ACCURACY")
        print(naivebayes)
        print("CLASSIFICATION REPORT")
        print(classification_report(y_test, predict_nb))
        print("CONFUSION MATRIX")
        print(confusion_matrix(y_test, predict_nb))
        detection_accuracy.objects.create(names="Naive Bayes", ratio=naivebayes)
        models.append(('naive_bayes', NB))

        # SVM Model
        print("SVM")
        from sklearn import svm

        lin_clf = svm.LinearSVC()
        lin_clf.fit(X_train, y_train)
        predict_svm = lin_clf.predict(X_test)
        svm_acc = accuracy_score(y_test, predict_svm) * 100
        print("ACCURACY")
        print(svm_acc)
        print("CLASSIFICATION REPORT")
        print(classification_report(y_test, predict_svm))
        print("CONFUSION MATRIX")
        print(confusion_matrix(y_test, predict_svm))
        detection_accuracy.objects.create(names="SVM", ratio=svm_acc)
        models.append(('SVM', lin_clf))

        print("Logistic Regression")

        from sklearn.linear_model import LogisticRegression

        reg = LogisticRegression(random_state=0, solver='lbfgs').fit(X_train, y_train)
        y_pred = reg.predict(X_test)
        print("ACCURACY")
        print(accuracy_score(y_test, y_pred) * 100)
        print("CLASSIFICATION REPORT")
        print(classification_report(y_test, y_pred))
        print("CONFUSION MATRIX")
        print(confusion_matrix(y_test, y_pred))
        detection_accuracy.objects.create(names="Logistic Regression", ratio=accuracy_score(y_test, y_pred) * 100)
        models.append(('LogisticRegression', reg))


        from sklearn.ensemble import VotingClassifier
        classifier = VotingClassifier(models)
        classifier.fit(X_train, y_train)
        y_pred = classifier.predict(X_test)

        Habitation_Name = [Habitation_Name]
        vector1 = cv.transform(Habitation_Name).toarray()
        predict_text = classifier.predict(vector1)

        pred = str(predict_text).replace("[", "")
        pred1 = str(pred.replace("]", ""))

        prediction = int(pred1)

        if (prediction == 0):
            val = 'Salinity'

        elif (prediction == 1):
            val = 'Fluoride'

        elif (prediction == 2):
            val = 'Iron'

        elif (prediction == 3):
            val = 'Arsenic-Fully Polluted'

        elif (prediction == 4):
            val = 'Nitrate'

            print(prediction)
            print(val)

        water_quality_type.objects.create(State_Name=State_Name,District_Name=District_Name,Block_Name=Block_Name,Panchayat_Name=Panchayat_Name,Village_Name=Village_Name,Habitation_Name=Habitation_Name,Year=Year,Prediction=val)

        return render(request, 'RUser/Predict_Water_Quality.html',{'objs': val})
    return render(request, 'RUser/Predict_Water_Quality.html')



