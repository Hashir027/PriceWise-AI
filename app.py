import os
import io
import time
import re
import textwrap
import streamlit as st

from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("GEMINI_API_KEY is missing from your .env file.")
    st.stop()

client = genai.Client(api_key=API_KEY)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="PriceWise AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# LOAD CSS
# =========================================================

def load_css():
    try:
        with open("style.css", "r", encoding="utf-8") as file:
            css = file.read()

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )

    except FileNotFoundError:
        st.error(
            "style.css not found. Make sure it is in the same folder as app.py."
        )
        st.stop()


load_css()


# =========================================================
# HTML HELPER
# =========================================================

def render_html(html):
    clean_html = textwrap.dedent(html).strip()

    st.markdown(
        clean_html,
        unsafe_allow_html=True
    )


# =========================================================
# SESSION STATE
# =========================================================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "recommended_price" not in st.session_state:
    st.session_state.recommended_price = None


# =========================================================
# GEMINI MODELS (Original)
# =========================================================

MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash"
]


TEMPORARY_ERRORS = [
    "503",
    "unavailable",
    "high demand",
    "overloaded",
    "429",
    "resource_exhausted",
    "500",
    "deadline",
    "timeout",
    "temporarily"
]


# =========================================================
# IMAGE OPTIMIZATION
# =========================================================

def optimize_image(uploaded_file):
    image = Image.open(uploaded_file)

    if image.mode != "RGB":
        image = image.convert("RGB")

    image.thumbnail((1200, 1200))

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=75,
        optimize=True
    )

    return buffer.getvalue()


# =========================================================
# TEMPORARY ERROR CHECK
# =========================================================

def is_temporary_error(error):
    error_text = str(error).lower()

    return any(
        item in error_text
        for item in TEMPORARY_ERRORS
    )


# =========================================================
# GEMINI
# =========================================================

def generate_with_gemini(contents):
    last_error = None

    for model_name in MODELS:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(
                            thinking_level="low"
                        )
                    )
                )

                if response and response.text:
                    return response.text

                raise Exception(
                    f"{model_name} returned an empty response."
                )

            except Exception as error:
                last_error = error

                if not is_temporary_error(error):
                    break

                if attempt < 2:
                    time.sleep(2 ** attempt)

    raise last_error


# =========================================================
# EXTRACT PRICE
# =========================================================

def extract_recommended_price(text):
    if not text:
        return None

    patterns = [
        r"Recommended Price\s*:\s*PKR\s*([\d,]+)",
        r"Recommended Price\s*:\s*Rs\.?\s*([\d,]+)",
        r"Recommended Price\s*:\s*([\d,]+)"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            try:
                return int(
                    match.group(1).replace(",", "")
                )
            except:
                pass

    return None


# =========================================================
# HERO
# =========================================================

render_html("""
<div class="hero">
    <div class="hero-badge">
        ✦ AI-Powered Price Assistant
    </div>
    <div class="hero-title">
        Price<span>Wise</span> AI
    </div>
    <div class="hero-subtitle">
        Know the Price. Negotiate Smarter.
        <br>
        Get an AI-powered recommended price
        before negotiating with a seller.
    </div>
</div>
""")


# =========================================================
# PRODUCT ANALYSIS
# =========================================================

render_html("""
<div class="section-title">
    Product Analysis
</div>
<div class="section-subtitle">
    Add the product image and seller information below.
</div>
""")


left_col, right_col = st.columns(
    [1.15, 1],
    gap="large"
)


# =========================================================
# LEFT SIDE - IMAGE
# =========================================================

with left_col:
    render_html("""
    <div class="custom-card">
        <div class="card-title">
            Product Image
        </div>
        <div class="card-description">
            Upload a clear photo of the product.
            AI will analyze the visible product details.
        </div>
    </div>
    """)

    uploaded_file = st.file_uploader(
        "Upload Product Image",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ],
        label_visibility="collapsed"
    )

    if uploaded_file:
        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Product Preview",
            use_container_width=True
        )

    else:
        render_html("""
        <div class="info-box">
            Upload a product photo to get started.
        </div>
        """)


# =========================================================
# RIGHT SIDE
# =========================================================

with right_col:
    render_html("""
    <div class="custom-card">
        <div class="card-title">
            Price & Product Details
        </div>
        <div class="card-description">
            Enter the seller's price and your target price.
        </div>
    </div>
    """)

    shopkeeper_price = st.number_input(
        "Seller / Shopkeeper Price (PKR)",
        min_value=0.0,
        step=100.0,
        format="%.0f"
    )

    target_price = st.number_input(
        "Your Target Price (PKR)",
        min_value=0.0,
        step=100.0,
        format="%.0f"
    )

    location = st.text_input(
        "Location",
        placeholder="e.g. Gulshan-e-Iqbal, Karachi"
    )

    condition = st.selectbox(
        "Product Condition",
        [
            "New",
            "Like New",
            "Used",
            "Refurbished",
            "Damaged"
        ]
    )

    seller_comment = st.text_area(
        "Seller / Product Details",
        placeholder=(
            "e.g. 1 year warranty, slightly used, "
            "box available, urgent sale..."
        ),
        height=120
    )


# =========================================================
# ANALYZE
# =========================================================

render_html("""
<div class="section-title">
    Analyze Product
</div>
<div class="section-subtitle">
    PriceWise AI will identify the product and generate
    one recommended price.
</div>
""")


analyze_button = st.button(
    "Analyze & Get Recommended Price",
    type="primary",
    use_container_width=True
)


# =========================================================
# RUN ANALYSIS
# =========================================================

if analyze_button:
    st.session_state.analysis_result = None
    st.session_state.recommended_price = None

    if not uploaded_file:
        st.warning(
            "Please upload a product image first."
        )

    elif shopkeeper_price <= 0:
        st.warning(
            "Please enter the seller/shopkeeper price."
        )

    elif target_price <= 0:
        st.warning(
            "Please enter your target price."
        )

    elif not location.strip():
        st.warning(
            "Please enter your location."
        )

    else:
        image_bytes = optimize_image(
            uploaded_file
        )

        prompt = f"""
You are PriceWise AI.

You are an AI-powered shopping,
price-estimation and negotiation assistant.

Analyze the uploaded product image and provide
ONE recommended price that the buyer should aim
to pay.

The app does NOT use live internet search.

BUYER INFORMATION:

Seller Price:
PKR {shopkeeper_price:,.0f}

Buyer Target Price:
PKR {target_price:,.0f}

Location:
{location}

Condition:
{condition}

Seller Details:
{seller_comment if seller_comment else "No additional information provided."}


PRODUCT IDENTIFICATION

Identify only information that can reasonably be
determined from the image.

Include:

- Product
- Brand
- Model
- Category
- Variant
- Storage
- RAM
- Size
- Generation
- Color
- Visible specifications

Never invent specifications.

If information cannot be determined:

"Not clearly identifiable from the image."


CONDITION

Analyze visible condition only.

Mention:

- Scratches
- Wear
- Damage
- Missing visible parts
- Overall visible condition

Do not claim hidden defects.


RECOMMENDED PRICE

Give EXACTLY ONE recommended price.

Consider:

- Product
- Brand
- Model
- Variant
- Specifications
- Condition
- Visible condition
- Seller information
- Buyer target
- Location

Use exactly:

Recommended Price: PKR XX,XXX

Give a short explanation.

Do NOT provide:

- Minimum price
- Maximum price
- Price range
- Typical price
- Fair price range
- Multiple recommended prices

The recommendation is an AI-generated estimate,
not a guaranteed market price.


PRICE COMPARISON

Show:

Seller Price:
Your Target:
Recommended Price:

Then briefly explain the difference.


NEGOTIATION MESSAGE

Create ONE short natural message for the seller.


BUYER CHECKS

Give up to 5 relevant checks before purchasing.


CONFIDENCE

Product Identification:
High / Medium / Low

Price Recommendation:
High / Medium / Low

Explain briefly.


RULES

Never:

- Claim a live market price
- Claim you searched online
- Invent specifications
- Invent hidden defects
- Give a price range
- Give multiple recommended prices
- Give BUY / DON'T BUY verdict


FINAL FORMAT

# Product Identification

Product:
Brand:
Model:
Category:
Variant:
Visible Specifications:


# Condition

Selected Condition:
Visible Condition:


# Recommended Price

Recommended Price: PKR XX,XXX

Why:


# Price Comparison

Seller Price: PKR {shopkeeper_price:,.0f}
Your Target: PKR {target_price:,.0f}
Recommended Price: PKR XX,XXX

Short comparison.


# Negotiation Message

Short seller message.


# Things To Check

1.
2.
3.
4.
5.


# Confidence

Product Identification:
Price Recommendation:

Explanation:
"""

        with st.spinner(
            "AI is analyzing your product..."
        ):
            try:
                contents = [
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg"
                    ),
                    prompt
                ]

                result = generate_with_gemini(
                    contents
                )

                recommended_price = (
                    extract_recommended_price(result)
                )

                st.session_state.analysis_result = result

                st.session_state.recommended_price = (
                    recommended_price
                )

                st.success(
                    "Analysis completed successfully!"
                )

            except Exception as error:
                st.error(
                    "Analysis failed. Please try again."
                )

                st.info(
                    "Gemini may be temporarily busy. "
                    "Please wait a moment and try again."
                )

                with st.expander(
                    "Technical Error"
                ):
                    st.code(str(error))


# =========================================================
# RESULTS
# =========================================================

if st.session_state.analysis_result:
    render_html("""
    <div class="section-title">
        Your PriceWise Analysis
    </div>

    <div class="section-subtitle">
        Here's what AI found from your product.
    </div>
    """)

    if st.session_state.recommended_price:
        render_html(f"""
        <div class="price-card">
            <div class="price-label">
                Recommended Price
            </div>
            <div class="price-value">
                PKR {st.session_state.recommended_price:,.0f}
            </div>
            <div class="price-description">
                Aim for around this price when
                negotiating with the seller.
            </div>
        </div>
        """)

    render_html("""
    <div class="result-content">
    """)

    st.markdown(
        st.session_state.analysis_result
    )

    render_html("""
    </div>
    """)

    render_html("""
    <div class="section-title">
        Price Summary
    </div>
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Seller Price",
            f"PKR {shopkeeper_price:,.0f}"
        )

    with col2:
        st.metric(
            "Your Target",
            f"PKR {target_price:,.0f}"
        )

    with col3:
        if st.session_state.recommended_price:
            st.metric(
                "Recommended Price",
                f"PKR {st.session_state.recommended_price:,.0f}"
            )
        else:
            st.metric(
                "Recommended Price",
                "See analysis"
            )

    render_html(f"""
    <div class="info-box">
        <strong>Product Condition</strong>
        <br><br>
        {condition}
    </div>
    """)

    if st.session_state.recommended_price:
        render_html(f"""
        <div class="success-box">
            <strong>Your Price Goal</strong>
            <br><br>
            Aim for around
            <strong>
                PKR {st.session_state.recommended_price:,.0f}
            </strong>
            when negotiating with the seller.
            <br><br>
            Use this as a negotiation reference and
            verify the product condition and
            specifications before purchasing.
        </div>
        """)


# =========================================================
# FOOTER
# =========================================================

render_html("""
<div class="footer">
    <strong>PriceWise AI</strong>
    <br>
    AI-powered price guidance for smarter negotiations.
    <br><br>
    Recommendations are AI-generated for
    informational purposes only.
</div>
""")