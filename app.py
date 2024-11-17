from flask import Flask
import requests
from PIL import Image
from io import BytesIO
import json
from tflite_runtime.interpreter import Interpreter
import numpy as np

app = Flask(__name__)
app.config.from_pyfile('settings.py')


def download_image(url):
    """Download an image from a URL and return it as a PIL Image."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        raise


@app.route('/')
def main():
    return 'Monch!'


def food_query(query):
    API_KEY = app.config['API_KEY']
    query = query.replace("_", " ")
    poss_queries = [query]

    if query[-1] != 's':
        poss_queries.append(query + 's')

    poss_queries += query.split(' ')

    for q in poss_queries:
        try:
            url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={API_KEY}&query={q}"
            response = requests.get(url)
            data = response.json()

            # servingSize = data['foods'][0]['servingSize']
            servingSizeUnit = data['foods'][0]['servingSizeUnit']

            nutrients_lst = data['foods'][0]['foodNutrients']

            protein = nutrients_lst[0]['value']
            fats = nutrients_lst[1]['value']
            carbs = nutrients_lst[2]['value']
            Cals = nutrients_lst[3]['value']
            return {'name': q,
                    'protein': protein, 'fats': fats,
                    'carbs': carbs, 'calories': Cals}
        except:
            continue
    return "Data Not Found"


@app.route('/process/<cid>')
def process(cid):
    url = "https://gold-legal-fish-789.mypinata.cloud/ipfs/" + cid
    img = download_image(url).convert("RGB")
    with open('food_nums.json', 'r') as file:
        food_nums = json.load(file)

    tflite_model_path = 'food101_classifier.tflite'
    interpreter = Interpreter(model_path=tflite_model_path)
    interpreter.allocate_tensors()

    # input and output details
    input = interpreter.get_input_details()
    output = interpreter.get_output_details()

    img = img.resize((256, 256), Image.LANCZOS)
    img_vec = np.array(img).astype("float32") * (1 / 255.0)
    img_vec = np.expand_dims(img_vec, axis=0)

    input = interpreter.get_input_details()
    output = interpreter.get_output_details()

    interpreter.set_tensor(input[0]['index'], img_vec)
    interpreter.invoke()

    prediction = interpreter.get_tensor(output[0]['index'])
    predicted_class = np.argmax(prediction)
    return food_query(food_nums[str(predicted_class)])
