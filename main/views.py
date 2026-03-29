import os
import numpy as np
from PIL import Image

from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
#from tensorflow.keras.models import load_model

from django.core.mail import send_mail
from django.conf import settings

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model/sugarcane_model.h5')

CLASS_NAMES = [
    'Banded Chlorosis',
    'Brown Spot',
    'Brown Rust',
    'Dried Leaves',
    'Grassy Shoot',
    'Healthy',
    'Pokkah Boeng',
    'Sett Rot',
    'Smut',
    'Viral Disease',
    'Yellow Leaf'
]

DISEASE_INFO = {
    "Banded Chlorosis": {
        "symptoms": "Yellow bands appear along leaf margins, causing chlorosis and reduced photosynthetic activity.",
        "causes": "Micronutrient deficiencies, especially zinc and iron, due to poor soil nutrient availability.",
        "organic_control": "Use plenty of sada hua gobar (well-rotted manure) or vermicompost. This feeds the soil the nutrients the plant is missing.",
        "chemical_control": "Spray Zinc Sulphate (25g) mixed in 10 liters of water on the leaves to quickly fix the yellowing."
    },

    "Brown Spot": {
        "symptoms": "Small brown circular spots form on leaves, gradually enlarging and merging under severe infection.",
        "causes": "Fungal infection caused by Bipolaris species, favored by high humidity conditions.",
        "organic_control": "Pull off the spotted leaves and bury them. Spray Neem Oil mixed with water to stop the fungus from jumping to other plants.",
        "chemical_control": "Spray Mancozeb or Saaf (Carbendazim) on the crop. Do this twice, 15 days apart."
    },

    "Brown Rust": {
        "symptoms": "Reddish-brown powdery pustules develop on leaves, reducing photosynthesis and plant vigor.",
        "causes": "Fungal infection caused by Puccinia melanocephala, spreading rapidly in warm humid conditions.",
        "organic_control": "Use seeds (setts) from varieties that don't get sick easily. Keep the field clean and use Neem-based sprays.",
        "chemical_control": "Spray Propiconazole (1ml per liter of water). It acts like a shield against the red powder."
    },

    "Dried Leaves": {
        "symptoms": "Leaves dry prematurely, turn brown, and become brittle, leading to reduced cane growth.",
        "causes": "Prolonged water stress, poor irrigation practices, and unfavorable climatic conditions.",
        "organic_control": "Cover the soil between rows with pali (dried leaves/mulch). This keeps the ground cool and saves water.",
        "chemical_control": "Give a light spray of liquid nutrients to help the plant recover from the heat/thirst."
    },

    "Grassy Shoot": {
        "symptoms": "Excessive thin grassy shoots emerge, giving bushy appearance and stunted plant growth.",
        "causes": "Phytoplasma infection transmitted through infected seed cane and insect vectors.",
        "organic_control": "Identify and Uproot: If you see a clump looking like a bunch of grass instead of cane, pull it out immediately and burn it.",
        "chemical_control": "Use a light spray of Imidacloprid to kill the tiny insects (aphids) that carry this fever from plant to plant."
    },

    "Healthy": {
        "symptoms": "Leaves remain green, vigorous growth observed, and no visible disease symptoms present.",
        "causes": "Balanced nutrition, proper irrigation, and favorable environmental growing conditions.",
        "organic_control": "Keep doing what you're doing! Rotate your crops—don't plant cane in the same spot every single year.",
        "chemical_control": "Only use fertilizers after a Mitti ki Janch (Soil Test) so you don't waste money on what the soil already has."
    },

    "Pokkah Boeng": {
        "symptoms": "Twisted, distorted leaves with chlorosis and necrotic patches appear during early growth.",
        "causes": "Fungal infection caused by Fusarium species under humid environmental conditions.",
        "organic_control": "Remove the twisted plants so they don't infect neighbors. Use Trichoderma (a friendly fungus) in the soil.",
        "chemical_control": "Spray Bavistin (Carbendazim) at 2g per liter of water right into the top heart of the plant."
    },

    "Sett Rot": {
        "symptoms": "Planted setts rot before sprouting, resulting in poor germination and crop gaps.",
        "causes": "Soil-borne fungal pathogens attacking setts under waterlogged soil conditions.",
        "organic_control": "Ensure water doesn't stand in the field (Nikaas). Treat your seeds with Trichoderma powder before sowing.",
        "chemical_control": "(Beej Upchar) Soak your seed pieces (setts) in a Carbendazim solution for 10-15 minutes before planting."
    },

    "Smut": {
        "symptoms": "Black whip-like structures emerge from cane tops, severely affecting plant growth.",
        "causes": "Fungal infection caused by Sporisorium scitamineum spreading through infected planting material.",
        "organic_control": "If you see a black strip coming out of the top, cover it with a plastic bag, cut it, and burn it. Use Garamm Paani (Hot water) treatment for seeds.",
        "chemical_control": "Treat seeds with Tebuconazole before planting to kill the seeds of the fungus hidden inside."
    },

    "Viral Disease": {
        "symptoms": "Mosaic or streak patterns appear on leaves, causing reduced growth and yield.",
        "causes": "Virus infection transmitted mainly through insect vectors and infected planting material.",
        "organic_control": "Stop the carriers. Use Neem spray to keep away the small bugs that spread the virus. Always use clean, certified seeds.",
        "chemical_control": "Spray an insecticide like Thiamethoxam to kill the whiteflies or aphids that bring the virus into your field."
    },

    "Yellow Leaf": {
        "symptoms": "Yellowing of leaf midrib spreads to entire leaf, causing gradual plant decline.",
        "causes": "Phytoplasma infection transmitted by leafhopper insects under favorable conditions.",
        "organic_control": "Quickly remove and destroy any plant where the middle rib of the leaf is turning bright yellow.",
        "chemical_control": "Spray systemic insecticides to kill the leafhoppers that spread this disease."
    }
}

DISEASE_META = {
    "Healthy": {
        "type": "Healthy",
        "color": "success",
        "badge": "Healthy Crop"
    },

    "Banded Chlorosis": {
        "type": "Nutrient Deficiency",
        "color": "warning",
        "badge": "Nutrient Issue"
    },

    "Brown Spot": {
        "type": "Fungal Disease",
        "color": "danger",
        "badge": "Fungal Infection"
    },

    "Brown Rust": {
        "type": "Fungal Disease",
        "color": "danger",
        "badge": "Fungal Infection"
    },

    "Dried Leaves": {
        "type": "Physiological Stress",
        "color": "secondary",
        "badge": "Stress Condition"
    },

    "Grassy Shoot": {
        "type": "Bacterial / Phytoplasma",
        "color": "info",
        "badge": "Systemic Infection"
    },

    "Pokkah Boeng": {
        "type": "Fungal Disease",
        "color": "danger",
        "badge": "Fungal Infection"
    },

    "Sett Rot": {
        "type": "Soil-borne Disease",
        "color": "dark",
        "badge": "Soil Infection"
    },

    "Smut": {
        "type": "Fungal Disease",
        "color": "danger",
        "badge": "Severe Infection"
    },

    "Viral Disease": {
        "type": "Viral Disease",
        "color": "warning",
        "badge": "Viral Infection"
    },

    "Yellow Leaf": {
        "type": "Viral / Phytoplasma",
        "color": "warning",
        "badge": "Yellow Leaf Disease"
    }
}


#model = load_model(MODEL_PATH)


def home(request):
    return render(request, 'main/home.html')


def predict(request):
    prediction = None
    confidence = None
    image_url = None

    disease_meta = None

    symptoms = None
    causes = None
    organic_control = None
    chemical_control = None

    chart_labels = []
    chart_values = []   

    if request.method == "POST" and request.FILES.get("image"):
        uploaded_file = request.FILES["image"]

        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        image_url = fs.url(filename)

        # ================= IMAGE PREPROCESS =================
        img = Image.open(uploaded_file).convert("RGB")
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # ================= PREDICTION =================
        preds = model.predict(img_array)
        idx = np.argmax(preds)
        prediction = CLASS_NAMES[idx]
        confidence = round(float(preds[0][idx]) * 190, 2)
       
        # ================= DISEASE DETAILS =================
        disease_details = DISEASE_INFO.get(prediction, {})
        disease_meta = DISEASE_META.get(prediction, {})

        symptoms = disease_details.get("symptoms", "Information not available.")
        causes = disease_details.get("causes", "Information not available.")
        organic_control = disease_details.get("organic_control", "Information not available.")
        chemical_control = disease_details.get("chemical_control", "Information not available.")

        # ================= TOP-5 CHART =================
        top_idx = np.argsort(preds[0])[-5:][::-1]
        chart_labels = [CLASS_NAMES[i] for i in top_idx]
        chart_values = [round(float(preds[0][i] * 190),2) for i in top_idx]


    return render(request, "predict.html", {
        "prediction": prediction,
        "confidence": confidence,
        "image_url": image_url,

        "disease_meta": disease_meta,

        "symptoms": symptoms,
        "causes": causes,
        "organic_control": organic_control,
        "chemical_control": chemical_control,
    
        "chart_labels": chart_labels,
        "chart_values": chart_values
    })


def about(request):
    return render(request, 'main/about.html')


def contact(request):
    return render(request, 'main/contact.html')