from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load real dataset and train model
crop_df = pd.read_csv('Crop_recommendation.csv')  # Make sure this file is in the same directory
features = crop_df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
labels = crop_df['label']
model = DecisionTreeClassifier()
model.fit(features, labels)

# Fertilizer suggestion mapping
fertilizer_dict = {
    'rice': 'Urea and DAP',
    'wheat': 'NPK (20-20-0)',
    'maize': 'Urea with Potash',
    'cotton': 'Phosphate rich organic manure',
    'soybean': 'Biofertilizers with Phosphate Solubilizing Bacteria',
    'barley': 'Ammonium Nitrate and DAP',
    'sugarcane': 'NPK (18-18-18) and Organic Compost',
    'millets': 'Farmyard manure and low nitrogen NPK mix',
    'cashew': 'Neem cake and organic compost',
    'coconut': 'NPK (10-10-20) with Magnesium Sulphate',
    'coffee': 'Urea and potash with organic matter',
    'groundnut': 'Gypsum and NPK with calcium',
    'paddy': 'Urea and DAP',
    'peanuts': 'Calcium and Potassium-enriched NPK',
    'pulses': 'Biofertilizers like Rhizobium and PSB',
    'sorghum': 'NPK (12-32-16) and Zinc sulphate',
    'sugar beet': 'Ammonium nitrate with potash',
    'tea': 'Nitrogen-rich fertilizers with organic compost',
    'vegetables': 'Vermicompost and balanced NPK',
    'watermelon': 'High Potash and Phosphorus-rich fertilizer'
}

# Crop image mapping
crop_image_dict = {
    'rice': '/static/images/rice.png',
    'wheat': '/static/images/wheat.png',
    'maize': '/static/images/maize.png',
    'cotton': '/static/images/cotton.png',
    'soybean': '/static/images/soybean.png',
    'barley': '/static/images/barley.png',
    'sugarcane': '/static/images/sugarcane.png',
    'millets': '/static/images/millets.png',
    'cashew': '/static/images/cashew.png',
    'coconut': '/static/images/coconut.png',
    'coffee': '/static/images/coffee.png',
    'groundnut': '/static/images/groundnut.png',
    'paddy': '/static/images/paddy.png',
    'peanuts': '/static/images/peanuts.png',
    'pulses': '/static/images/pulses.png',
    'sorghum': '/static/images/sorghum.png',
    'sugar beet': '/static/images/sugarbeet.png',
    'tea': '/static/images/tea.png',
    'vegetables': '/static/images/vegetables.png',
    'watermelon': '/static/images/watermelon.png',
    'jute': '/static/images/jute.png',
    'papaya': '/static/images/papaya.png',
    'grapes': '/static/images/grapes.png',
    'mango': '/static/images/mango.png',
    'banana': '/static/images/banana.png',
    'pomegranate': '/static/images/pomegranate.png',
    'mungbean': '/static/images/mungbean.png',
    'chickpea': '/static/images/chickpea.png',
    'kidneybeans': '/static/images/kidneybeans.png',
    'pigeonpeas': '/static/images/pigeonpeas.png',
    'mothbean': '/static/images/mothbean.png',
    'lentil': '/static/images/lentil.png',
    'blackgram': '/static/images/blackgram.png',
    'apple': '/static/images/apple.png',
    'orange': '/static/images/orange.png',
    'muskmelon': '/static/images/muskmelon.png'
}

def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()
        if user:
            session['username'] = username
            flash('Login Successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('register'))
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()

        cur.execute("SELECT username, password FROM users")
        rows = cur.fetchall()
        df = pd.DataFrame(rows, columns=['Username', 'Password'])
        df.to_excel("user_data.xlsx", index=False)

        conn.close()
        flash('Registration Successful. Please Login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    crop = None
    fertilizer = None
    crop_img = None
    if request.method == 'POST':
        try:
            N = int(request.form['N'])
            P = int(request.form['P'])
            K = int(request.form['K'])
            temperature = float(request.form['temperature'])
            humidity = float(request.form['humidity'])
            ph = float(request.form['ph'])
            rainfall = float(request.form['rainfall'])
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            prediction = model.predict(data)
            crop = prediction[0]
            fertilizer = fertilizer_dict.get(crop.lower(), "Balanced NPK fertilizer with organic manure")
            crop_img = crop_image_dict.get(crop.lower(), None)
        except Exception as e:
            flash('Error in input data. Please check your entries.', 'error')
    return render_template('dashboard.html', crop=crop, fertilizer=fertilizer, crop_img=crop_img)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    message_sent = False
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        contact = request.form.get('contact')
        message = request.form.get('message')

        with open("messages.txt", "a") as file:
            file.write(f"{datetime.now()} - Name: {name}, Email: {email}, Contact: {contact}, Message: {message}\n")

        return redirect(url_for('contact', success='true'))

    if request.args.get('success') == 'true':
        message_sent = True
    return render_template('contact.html', success=message_sent)

@app.route('/learn')
def learn():
    return render_template('learn.html')

@app.route('/soil-info')
def soil_info():
    soil_data = {
        'Alluvial': ['Rice', 'Wheat', 'Sugarcane', 'Pulses'],
        'Black': ['Cotton', 'Soybean', 'Sorghum'],
        'Red': ['Millets', 'Groundnut', 'Pulses'],
        'Laterite': ['Cashew', 'Tea', 'Coffee'],
        'Sandy': ['Coconut', 'Watermelon', 'Peanuts'],
        'Clay': ['Paddy', 'Sugarcane'],
        'Peaty': ['Vegetables', 'Rice'],
        'Saline': ['Barley', 'Sugar beet']
    }
    return render_template('soil_info.html', soil_data=soil_data)

@app.route('/crop-guide')
def crop_guide():
    crop_guide_data = {
        'January': [
            {'name': 'Wheat', 'climate': 'Cool & Dry', 'img': 'static/images/wheat.png'},
            {'name': 'Mustard', 'climate': 'Cool & Dry', 'img': 'static/images/mustard.png'}
        ],
        'February': [
            {'name': 'Peas', 'climate': 'Cool & Dry', 'img': 'static/images/peas.png'},
            {'name': 'Gram', 'climate': 'Cool & Dry', 'img': 'static/images/gram.png'}
        ],
        'March': [
            {'name': 'Sunflower', 'climate': 'Warm & Dry', 'img': 'static/images/sflower.png'},
            {'name': 'Summer Maize', 'climate': 'Warm & Dry', 'img': 'static/images/smaize.png'}
        ],
        'April': [
            {'name': 'Cotton', 'climate': 'Hot & Dry', 'img': 'static/images/cotton.png'},
            {'name': 'Maize', 'climate': 'Warm & Humid', 'img': 'static/images/maize.png'}
        ],
        'May': [
            {'name': 'Sugarcane', 'climate': 'Hot & Dry', 'img': 'static/images/sugarcane.png'},
            {'name': 'Jowar', 'climate': 'Hot & Dry', 'img': 'static/images/jowar.png'}
        ],
        'June': [
            {'name': 'Paddy (early)', 'climate': 'Warm & Humid', 'img': 'static/images/paddy.png'},
            {'name': 'Groundnut', 'climate': 'Warm & Humid', 'img': 'static/images/groundnut.png'}
        ],
        'July': [
            {'name': 'Paddy', 'climate': 'Rainy & Warm', 'img': 'static/images/paddy.png'},
            {'name': 'Sugarcane', 'climate': 'Rainy & Warm', 'img': 'static/images/sugarcane.png'}
        ],
        'August': [
            {'name': 'Bajra', 'climate': 'Rainy & Humid', 'img': 'static/images/bajra.png'},
            {'name': 'Soybean', 'climate': 'Rainy & Humid', 'img': 'static/images/soybean.png'}
        ],
        'September': [
            {'name': 'Maize', 'climate': 'Warm & Humid', 'img': 'static/images/maize.png'},
            {'name': 'Arhar', 'climate': 'Warm & Humid', 'img': 'static/images/arhar.png'}
        ],
        'October': [
            {'name': 'Barley', 'climate': 'Cool & Dry', 'img': 'static/images/barley.png'},
            {'name': 'Chickpea', 'climate': 'Cool & Dry', 'img': 'static/images/chickpea.png'}
        ],
        'November': [
            {'name': 'Garlic', 'climate': 'Cool & Dry', 'img': 'static/images/garlic.png'},
            {'name': 'Lentils', 'climate': 'Cool & Dry', 'img': 'static/images/lentil.png'}
        ],
        'December': [
            {'name': 'Spinach', 'climate': 'Cool & Dry', 'img': 'static/images/spinach.png'},
            {'name': 'Wheat', 'climate': 'Cool & Dry', 'img': 'static/images/wheat.png'}
        ]
    }
    return render_template('crop_guide.html', crop_data=crop_guide_data)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)