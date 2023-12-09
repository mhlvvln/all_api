import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score

#df = pd.read_csv('../dataset.csv', sep='\t')

# X = df.drop(['target'], axis=1)
# y = df['target']
#
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#
#
# model = LinearRegression()
#
#
# model.fit(X_train, y_train)
#
# y_pred = model.predict(X_test)
#
# mse = mean_squared_error(y_test, y_pred)
# print(f'Mean Squared Error: {mse}')
#
# r2 = r2_score(y_test, y_pred)
# print(f'R^2 Score: {r2}')
#
model_filename = 'linear_regression_model.joblib'


# joblib.dump(model, model_filename)


def getModelResult(owner_id, topic, user_answer, is_correct, question_id, number_of_attempts, response_time,
                   question_rating):
    loaded_model = joblib.load(model_filename)

    # Пример входных данных для предсказания (подставьте свои значения)
    input_data = [
        [owner_id, topic, user_answer, is_correct, question_id, number_of_attempts, response_time, question_rating]]

    prediction = loaded_model.predict(input_data)
    return prediction[0]


#print(getModelResult(5, 1, 11, 1, 10, 0, 32, 0.4))
