import streamlit as st
from deta import Deta
from datetime import datetime

deta = Deta(st.secrets["data_key"])
db = deta.Base("config-scraper")

def main():
    st.title("Scraper Configuration App")
    
    # Define default configuration
    default_config = {
        "base_url": "https://www.tokopedia.com/",
        "min_delay": 8,
        "max_delay": 15,
        "scroll_step": 7,
        "min_scroll_delay": 10,
        "max_scroll_delay": 14,
        "proxy": None,
        "selectors": {
            "product": ["div", "css-bk6tzz e1nlzfl2"],
            "title": ["span", "css-20kt3o"],
            "price": ["span", "css-o5uqvq"],
            "sold": ["span", "ycJITt9ym8j_SF77Kv5q"],
            "location": ["span", "css-ywdpwd"]
        },
        "categories": [
            "https://www.tokopedia.com/p/makanan-minuman/bahan-kue",
            "https://www.tokopedia.com/p/makanan-minuman/daging",
            "https://www.tokopedia.com/p/makanan-minuman/makanan-kering",
            "https://www.tokopedia.com/p/makanan-minuman/minuman",
            "https://www.tokopedia.com/p/makanan-minuman/seafood",
            "https://www.tokopedia.com/p/makanan-minuman/beras-shirataki-dan-porang",
            "https://www.tokopedia.com/p/makanan-minuman/hampers-parsel-dan-paket-makanan",
            "https://www.tokopedia.com/p/makanan-minuman/makanan-ringan",
            "https://www.tokopedia.com/p/makanan-minuman/susu-olahan-susu",
            "https://www.tokopedia.com/p/makanan-minuman/buah",
            "https://www.tokopedia.com/p/makanan-minuman/kue",
            "https://www.tokopedia.com/p/makanan-minuman/makanan-sarapan",
            "https://www.tokopedia.com/p/makanan-minuman/produk-mengandung-babi",
            "https://www.tokopedia.com/p/makanan-minuman/telur",
            "https://www.tokopedia.com/p/makanan-minuman/bumbu-bahan-masakan",
            "https://www.tokopedia.com/p/makanan-minuman/makanan-jadi",
            "https://www.tokopedia.com/p/makanan-minuman/mie-pasta",
            "https://www.tokopedia.com/p/makanan-minuman/sayur",
            "https://www.tokopedia.com/p/makanan-minuman/tepung"
        ]
    }
    
    # Split into two columns
    col1, col2 = st.columns(2)
    
    # Left column for general configuration
    with col1:
        st.subheader("General Configuration")
        base_url = st.text_input("Base URL", default_config["base_url"], key="base_url_input")
        min_delay = st.number_input("Min Delay", value=default_config["min_delay"], key="min_delay_input")
        max_delay = st.number_input("Max Delay", value=default_config["max_delay"], key="max_delay_input")
        scroll_step = st.number_input("Scroll Step", value=default_config["scroll_step"], key="scroll_step_input")
        min_scroll_delay = st.number_input("Min Scroll Delay", value=default_config["min_scroll_delay"], key="min_scroll_delay_input")
        max_scroll_delay = st.number_input("Max Scroll Delay", value=default_config["max_scroll_delay"], key="max_scroll_delay_input")
        proxy = st.text_input("Proxy", default_config["proxy"], key="proxy_input")
    
    # Right column for selectors configuration
    with col2:
        st.subheader("Selectors Configuration")
        
        # Product Selector
        st.write("Product Selector:")
        with st.expander("Product"):
            product_tag = st.text_input("Tag", default_config["selectors"]["product"][0], key="product_tag_input")
            product_class = st.text_input("Class Name", default_config["selectors"]["product"][1], key="product_class_input")
        
        # Title Selector
        st.write("Title Selector:")
        with st.expander("Title"):
            title_tag = st.text_input("Tag", default_config["selectors"]["title"][0], key="title_tag_input")
            title_class = st.text_input("Class Name", default_config["selectors"]["title"][1], key="title_class_input")
        
        # Price Selector
        st.write("Price Selector:")
        with st.expander("Price"):
            price_tag = st.text_input("Tag", default_config["selectors"]["price"][0], key="price_tag_input")
            price_class = st.text_input("Class Name", default_config["selectors"]["price"][1], key="price_class_input")
        
        # Sold Selector
        st.write("Sold Selector:")
        with st.expander("Sold"):
            sold_tag = st.text_input("Tag", default_config["selectors"]["sold"][0], key="sold_tag_input")
            sold_class = st.text_input("Class Name", default_config["selectors"]["sold"][1], key="sold_class_input")
        
        # Location Selector
        st.write("Location Selector:")
        with st.expander("Location"):
            location_tag = st.text_input("Tag", default_config["selectors"]["location"][0], key="location_tag_input")
            location_class = st.text_input("Class Name", default_config["selectors"]["location"][1], key="location_class_input")
    
    # Categories section below two columns
    st.subheader("Categories")
    categories = st.text_area("Categories (one per line)", "\n".join(default_config["categories"]), key="categories_input")
    categories = [cat.strip() for cat in categories.split("\n") if cat.strip()]
    
    # Button to save configuration
    if st.button("Save Configuration"):
        config = {
            "base_url": base_url,
            "min_delay": min_delay,
            "max_delay": max_delay,
            "scroll_step": scroll_step,
            "min_scroll_delay": min_scroll_delay,
            "max_scroll_delay": max_scroll_delay,
            "proxy": proxy,
            "selectors": {
                "product": [product_tag, product_class],
                "title": [title_tag, title_class],
                "price": [price_tag, price_class],
                "sold": [sold_tag, sold_class],
                "location": [location_tag, location_class]
            },
            "categories": categories,
            "timestamp": str(datetime.now())
        }
        db.put(config)

        # db_content = db.fetch().items

if __name__ == "__main__":
    main()