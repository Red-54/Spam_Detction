import os
from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC
import pandas as pd
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

app = Flask(__name__)
global Classifier
global Vectorizer

# Set your Twilio credentials here
TWILIO_ACCOUNT_SID = 'xxxxx'  # Replace with your Twilio Account SID
TWILIO_AUTH_TOKEN = 'xxxxx'    # Replace with your Twilio Auth Token
TWILIO_PHONE_NUMBER = '+xxxxx'  # Replace with your Twilio Phone Number

# Load data and train model
data = pd.read_csv('spam.csv', encoding='latin-1')
train_data = data[:4400]  # 4400 items
test_data = data[4400:]   # 1172 items

Classifier = OneVsRestClassifier(SVC(kernel='linear', probability=True))
Vectorizer = TfidfVectorizer()
vectorize_text = Vectorizer.fit_transform(train_data['v2'])
Classifier.fit(vectorize_text, train_data['v1'])

@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').strip()
    
    # Initialize the response message
    resp = MessagingResponse()
    msg = resp.message()
    
    try:
        # Vectorize and predict
        vectorized_msg = Vectorizer.transform([incoming_msg])
        prediction = Classifier.predict(vectorized_msg)[0]
        prediction_proba = Classifier.predict_proba(vectorized_msg).tolist()[0]

        if prediction == 'spam':
            msg.body(f"The message you sent is classified as *SPAM* with a confidence of {max(prediction_proba) * 100:.2f}%.")
        else:
            msg.body(f"The message you sent is *NOT SPAM*, classified with {max(prediction_proba) * 100:.2f}% confidence.")
    
    except Exception as e:
        msg.body(f"An error occurred: {str(e)}")

    return str(resp)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)

