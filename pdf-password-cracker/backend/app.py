from flask import Flask, request, render_template, redirect, url_for, jsonify
import os
from PyPDF2 import PdfReader

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'backend', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure uploads folder exists

# Function to recover password using a wordlist
def recover_password_with_wordlist(file_path, wordlist_path):
    try:
        reader = PdfReader(file_path)

        if not reader.is_encrypted:
            return "No password required (not encrypted)."

        with open(wordlist_path, 'r') as wordlist_file:
            for password in wordlist_file:
                password = password.strip()
                try:
                    reader.decrypt(password)
                    if reader.pages:  # Successful decryption
                        return f"Password recovered: {password}"
                except Exception:
                    continue

        return "Password not found in the wordlist."
    except Exception as e:
        return f"Error occurred: {e}"

# Flask routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recover', methods=['POST'])
def recover_password_route():
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400

    pdf = request.files['pdf']
    wordlist = request.files.get('wordlist')  # Optional wordlist file

    pdf_path = os.path.join(UPLOAD_FOLDER, pdf.filename)
    wordlist_path = None

    pdf.save(pdf_path)
    if wordlist:
        wordlist_path = os.path.join(UPLOAD_FOLDER, wordlist.filename)
        wordlist.save(wordlist_path)

    if wordlist_path:
        result = recover_password_with_wordlist(pdf_path, wordlist_path)
    else:
        result = "No wordlist provided. Use brute-force for recovery."

    # Clean up uploaded files
    os.remove(pdf_path)
    if wordlist_path:
        os.remove(wordlist_path)

    # Redirect to result page with the recovery result
    return redirect(url_for('result', result=result))

# Result page to show password recovery result
@app.route('/result')
def result():
    result = request.args.get('result')  # Get the result from the query string
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)

