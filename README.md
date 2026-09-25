# 💰 PriceWise AI

PriceWise AI is an intelligent shopping, price-estimation, and negotiation assistant designed to help buyers make smarter purchasing decisions. Built with **Streamlit** and powered by **Google Gemini AI**, the application analyzes product images and seller details to recommend a fair price for effective bargaining.

---

## 🌟 Key Features

* **AI Product Identification:** Automatically recognizes product categories, brands, models, and visible specifications from uploaded photos.
* **Smart Price Estimation:** Generates a single, data-backed recommended target price based on product condition, location, and seller pricing.
* **Negotiation Assistant:** Creates customized, natural messages tailored for communicating with sellers.
* **Pre-Purchase Buyer Checks:** Outlines up to 5 essential quality and condition checkpoints before finalizing a purchase.
* **Model Fallback Resilience:** Features automatic retry logic and seamless fallback across multiple Gemini Flash models to ensure high availability during peak traffic.

---

## 🛠️ Tech Stack

* **Frontend & UI:** Streamlit, Custom CSS
* **AI Engine:** Google GenAI SDK (`google-genai`), Gemini Flash Models
* **Image Processing:** Pillow (PIL)
* **Environment Management:** Python-dotenv

---

## 🚀 Local Installation & Setup

Follow these steps to set up and run the project locally on your machine:

1. Clone the Repository
2. Install Dependencies
Make sure you have Python installed, then run:
pip install -r requirements.txt
3. Configure Environment Variables
Create a .env file in the root directory of your project and add your Google Gemini API key:
GEMINI_API_KEY=your_gemini_api_key_here
4. Run the Application
Launch the Streamlit app:
streamlit run app.py
