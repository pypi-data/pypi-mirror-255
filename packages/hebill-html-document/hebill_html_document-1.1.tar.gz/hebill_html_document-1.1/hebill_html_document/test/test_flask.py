from flask import Flask

app = Flask(__name__)

language = "zhCN"


@app.route('/')
def root():
    from main import output
    return output


if __name__ == '__main__':
    app.run(debug=True)
