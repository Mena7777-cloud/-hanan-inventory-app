import streamlit as st
from sqlalchemy import or_
from database import SessionLocal, Product, create_db
from ui import draw_header, draw_add_edit_form, draw_product_list

# --- الإعدادات الأولية ---
st.set_page_config(page_title="نظام إدارة المخزون", page_icon="📦", layout="wide")
create_db() # إنشاء قاعدة البيانات عند أول تشغيل
db = SessionLocal()

# --- رسم الواجهة الرئيسية ---
draw_header()

# --- تقسيم الشاشة لعمودين ---
col1, col2 = st.columns([2, 1])

with col1:
    # تحديد المنتج للتعديل
    products_list = db.query(Product).order_by(Product.name).all()
    selected_product_name = st.selectbox("لتعديل منتج، اختره من هنا. للإضافة، اترك الحقل فارغًا.", 
                                         options=[p.name for p in products_list], 
                                         index=None,
                                         placeholder="اختر منتجًا لتعديله...")
        
    product_to_edit = None
    if selected_product_name:
        product_to_edit = db.query(Product).filter(Product.name == selected_product_name).first()

    # رسم فورم الإضافة والتعديل
    draw_add_edit_form(db, Product, product_to_edit)

with col2:
    # مربع البحث
    st.header("🔍 بحث في المخزون")
    search_term = st.text_input("ابحث بالاسم أو المورّد...")

st.markdown("---")

# --- منطق البحث وعرض المنتجات ---
query = db.query(Product)
if search_term:
    query = query.filter(or_(
        Product.name.ilike(f"%{search_term}%"),
        Product.supplier.ilike(f"%{search_term}%")
    ))
    
all_products = query.order_by(Product.id.desc()).all()
    
# رسم جدول المنتجات
draw_product_list(db, Product, all_products)

db.close()
