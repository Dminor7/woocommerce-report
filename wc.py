import json
from woocommerce import API
import urllib
from dateutil import parser
from flatten_json import flatten
import pandas as pd
import streamlit as st

CONFIG = {
    "url": st.secrets["url"],
    "consumer_key": st.secrets["consumer_key"],
    "consumer_secret": st.secrets["consumer_secret"]
    
}

# after={0}&
ENDPOINTS = {
    "orders":"orders?orderby=date&order=asc&per_page=100&page={0}",
    "products":"products?per_page=100&page={0}"
}

def get_endpoint(endpoint, page):
    '''Get the full url for the endpoint'''
    if endpoint not in ENDPOINTS:
        raise ValueError("Invalid endpoint {}".format(endpoint))
    
    
    return ENDPOINTS[endpoint].format(page)

def gen_request(url):
    wcapi = API(**CONFIG)
    resp = wcapi.get(url)
    resp.raise_for_status()
    return resp.json()

def filter_items(item):
    filtered = {
        "id":int(item["id"]),
        "name":str(item["name"]),
        "product_id":int(item["product_id"]),
        "variation_id":int(item["variation_id"]),
        "quantity":int(item["quantity"]),
        "subtotal":float(item["subtotal"]),
        "subtotal_tax":float(item["subtotal_tax"]),
        "total":float(item["total"]),
        "sku":str(item["sku"]),
        "price":float(item["price"])
    }
    return filtered

def filter_coupons(coupon):
    filtered = {
        "id":int(coupon["id"]),
        "code":str(coupon["code"]),
        "discount":float(coupon["discount"])
    }
    return filtered

def filter_billing(bill):
    filtered = {
        "first_name":str(bill["first_name"]),
        "last_name":str(bill["last_name"]),
        "company":str(bill["company"])
    }
    return filtered

def filter_order(order):
    if "line_items" in order and len(order["line_items"])>0:
        line_items = [filter_items(item) for item in order["line_items"]]
    else:
        line_items = None
    if "coupon_lines" in order and len(order["coupon_lines"])>0:
        coupon_lines = [filter_coupons(coupon) for coupon in order["coupon_lines"]]
    else:
        coupon_lines = None
    if "billing" in order and len(order["billing"])>0:
        billing_lines = {** filter_billing(order["billing"])}
    else:
        billing_lines = None
    if "meta_data" in order and len(order["meta_data"]) > 0:
        ardc_id = None
        for data in order["meta_data"]:
            if data['key'] == "ardc_id":
                ardc_id = data["value"]
        
    filtered = {
        "order_id":int(order["id"]),
        "order_key":str(order["order_key"]),
        "status":str(order["status"]),
        "customer_id":str(order["customer_id"]),
        "transaction_id":str(order["transaction_id"]),
        "date_created":order["date_created"],
        "data_paid":order["date_paid"],
        "date_modified":order["date_modified"],
        "discount_total":float(order["discount_total"]),
        "shipping_total":float(order["shipping_total"]),
        "total":float(order["total"]),
        "line_items":line_items,
        "ardc_id":ardc_id,
        "first_name":billing_lines["first_name"],
        "last_name":billing_lines["last_name"],
        "company":billing_lines["company"],
    }
    return filtered

def filter_product(product):
    if "meta_data" in product and len(product["meta_data"]) > 0:
        pcam_id = None
        for data in product["meta_data"]:
            if data['key'] == "course_id":
                pcam_id = data["value"]
    filtered = {
        "product_id":product["id"],
        "product_name": product["name"],
        "pcam_id":pcam_id
    }
    return filtered

def get_orders(page_number):
    result = []
    while True:
        endpoint = get_endpoint("orders", page_number)
        orders = gen_request(endpoint)
        for order in orders:
            order = filter_order(order)
            result.append(order)
        
        if len(orders) < 100:
            break
        else:
            page_number +=1

    return result

def get_products(page_number):
    result = []
    while True:
        endpoint = get_endpoint("products", page_number)
        products = gen_request(endpoint)
        for product in products:
            product = filter_product(product)
            result.append(product)
        if len(product) < 100:
            break
        else:
            page_number +=1

    return result


def download_report():
    orders = get_orders(1)
    products = get_products(1)
    df = pd.DataFrame(orders)
    df = df.explode('line_items')
    orders_df = df['line_items'].apply(pd.Series).merge(df, left_index=True, right_index=True, how ='outer')
    products_df = pd.DataFrame(products)
    master = pd.merge(orders_df, products_df, how="left", on="product_id")
    result = master[['order_id','name', 'product_id', 'transaction_id', 'data_paid','date_created','ardc_id', 'first_name', 'last_name', 'product_name', 'pcam_id']].copy(deep=True)
    result = result.drop_duplicates(subset=['order_id', 'product_id'], keep="first")
    return result



