import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import numpy as np
from scipy import stats
import sympy as sp
import speech_recognition as sr

# Download necessary NLTK resources if not already downloaded
nltk.download('punkt')
nltk.download('stopwords')

def extract_command(sentence):
    operations = {
        'add': 'add',
        'plus': 'add',
        'subtract': 'subtract',
        'minus': 'subtract',
        'multiply': 'multiply',
        'times': 'multiply',
        'divide': 'divide',
        'over': 'divide',
        'sqrt': 'sqrt',
        'square root': 'sqrt',
        'mean': 'mean',
        'average': 'mean',
        'mode': 'mode',
        'derivative': 'derivative',
        'integral': 'integral'
    }
   
    tokens = word_tokenize(sentence.lower())
    filtered_tokens = [word for word in tokens if word not in stopwords.words('english')]
   
    command = None
    numbers = []

    for token in filtered_tokens:
        # Check for operations
        if token in operations:
            command = operations[token]
        # Check for numbers and operators (+, -, *, /)
        elif re.match(r'^-?\d+(\.\d+)?$', token) or token in {'+', '-', '*', '/'}:
            numbers.append(token)
   
    return command, numbers

def sanitize_expression(numbers):
    sanitized_expression = []
    for token in numbers:
        if re.match(r'^-?\d+(\.\d+)?$', token):  # Number
            sanitized_expression.append(token)
        elif token in {'+', '-', '*', '/'}:  # Operator
            sanitized_expression.append(token)
        else:
            return None  # Invalid token found
    return " ".join(sanitized_expression)

def calculate(command, numbers):
    if command in ['add', 'subtract', 'multiply', 'divide']:
        sanitized_expression = sanitize_expression(numbers)
        if sanitized_expression is None:
            return "Invalid expression."
        try:
            result = eval(sanitized_expression.replace('plus', '+').replace('minus', '-').replace('times', '*').replace('over', '/'))
            return result
        except ZeroDivisionError:
            return "Error: Division by zero."
        except Exception as e:
            return f"Error in calculation: {e}"

    if command == 'sqrt':
        if len(numbers) != 1 or not re.match(r'^-?\d+(\.\d+)?$', numbers[0]):
            return "Square root requires exactly one number."
        return np.sqrt(float(numbers[0]))

    if command == 'mean':
        if not numbers:
            return "No numbers provided."
        num_list = [float(num) for num in numbers if re.match(r'^-?\d+(\.\d+)?$', num)]
        return np.mean(num_list)

    if command == 'mode':
        if not numbers:
            return "No numbers provided."
        num_list = [float(num) for num in numbers if re.match(r'^-?\d+(\.\d+)?$', num)]
        return stats.mode(num_list).mode[0] if num_list else "No valid numbers provided."

    if command == 'derivative':
        if len(numbers) != 1:
            return "Derivative requires one function in the format 'x^n'."
        x = sp.symbols('x')
        func = x**float(numbers[0])  # Example: taking derivative of x^n
        derivative = sp.diff(func, x)
        return derivative

    if command == 'integral':
        if len(numbers) != 1:
            return "Integral requires one function in the format 'x^n'."
        x = sp.symbols('x')
        func = x**float(numbers[0])  # Example: integrating x^n
        integral = sp.integrate(func, x)
        return integral

    return "Invalid command."

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your command...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            return "Sorry, I did not understand that."
        except sr.RequestError:
            return "Could not request results from Google Speech Recognition service."

def main():
    print("Welcome to the advanced sentence calculator!")
    while True:
        use_voice = input("Would you like to use voice input? (yes/no): ").strip().lower()
        if use_voice == 'yes':
            sentence = listen_for_command()
        else:
            sentence = input("Enter a calculation (or 'exit' to quit): ")
       
        if sentence.lower() == 'exit':
            break
       
        command, numbers = extract_command(sentence)
        result = calculate(command, numbers)
        print(f"Result: {result}")

if __name__ == "__main__":
    main()