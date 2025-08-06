from app import app
from apis import api

api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)
