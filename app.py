from flask import Flask, render_template, request
from project_db import Conversion, Session, create_db
import requests

app = Flask(__name__)

create_db()

@app.route('/', methods=['GET', 'POST'])
def convert():
    result = None
    to_currency = None

    if request.method == 'POST':
        from_currency = request.form['from_currency']
        to_currency = request.form['to_currency']
        amount = float(request.form['amount'])

        response = requests.get("https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5")
        rates = {item['ccy']: float(item['sale']) for item in response.json() if item['ccy'] in ['USD', 'EUR']}
        rates['UAH'] = 1.0

        if from_currency != 'UAH':
            amount_in_uah = amount * rates[from_currency]
        else:
            amount_in_uah = amount

        if to_currency != 'UAH':
            converted_amount = amount_in_uah / rates[to_currency]
        else:
            converted_amount = amount_in_uah

        with Session() as cursor:
            conversion = Conversion(
                from_currency=from_currency,
                to_currency=to_currency,
                amount=amount,
                result=converted_amount
            )
            cursor.add(conversion)
            cursor.commit()

        result = round(converted_amount, 2)

    return render_template('index.html', result=result, to_currency=to_currency)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
