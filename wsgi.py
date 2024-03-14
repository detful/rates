from flask import Flask, request, render_template_string
import requests
import csv

# Pobranie danych z API i zapis do pliku CSV
def fetch_and_save_rates():
    response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
    data = response.json()

    rates = data[0]['rates']

    with open('rates.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['currency', 'code', 'bid', 'ask']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writeheader()
        for rate in rates:
            writer.writerow(rate)
    
    return rates

app = Flask(__name__)

HTML = '''
<!doctype html>
<html>
<head><title>Kalkulator walut</title></head>
<body>
    <h2>Kalkulator walut</h2>
    <form method="post">
        <label for="currency">Wybierz walutę:</label>
        <select name="currency" id="currency">
            {% for rate in rates %}
            <option value="{{rate['code']}}">{{rate['code']}}</option>
            {% endfor %}
        </select>
        <label for="amount">Ilość:</label>
        <input type="number" id="amount" name="amount" value="1">
        <input type="submit" value="Przelicz">
    </form>
    {% if result %}
    <h3>Koszt w PLN: {{ result }}</h3>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def calculator():
    rates = fetch_and_save_rates()  # Pobranie aktualnych kursów walut i zapis do CSV przy każdym żądaniu
    result = None
    if request.method == 'POST':
        selected_currency = request.form['currency']
        amount = float(request.form['amount'])
        for rate in rates:
            if rate['code'] == selected_currency:
                result = amount * float(rate['ask'])
                break
    return render_template_string(HTML, rates=rates, result=result)

if __name__ == '__main__':
    app.run(debug=True)
