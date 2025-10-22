import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, or_
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# --- إعدادات الصفحة والشكل الحلو ---
st.set_page_config(page_title="نظام إدارة المخزون", page_icon="📦", layout="wide")

# --- قاعدة البيانات (في نفس الملف لتبسيط الأمور) ---
DATABASE_URL = "sqlite:///./inventory_simple.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    tablename = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, default=0)
    price = Column(Float, default=0.0)
    supplier = Column(String, default="")
    added_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# --- عنوان التطبيق ---
st.title("📦 نظام إدارة المخزون")
st.markdown("---")

# --- 1. قسم الإضافة والبحث (في عمودين) ---
col1, col2 = st.columns([2, 1])

with col1:
    st.header("➕ إضافة / تعديل منتج")
        
    # اختيار المنتج للتعديل أو تركه فارغًا للإضافة
    products_list = db.query(Product).order_by(Product.name).all()
    selected_product_name = st.selectbox("لتعديل منتج، اختره من هنا. للإضافة، اترك الحقل فارغًا.", 
                                         options=[p.name for p in products_list], 
                                         index=None,
                                         placeholder="اختر منتجًا لتعديله...")

    # جلب بيانات المنتج المختار أو إنشاء منتج فارغ
    product_to_edit = None
    if selected_product_name:
        product_to_edit = db.query(Product).filter(Product.name == selected_product_name).first()

    with st.form("product_form", clear_on_submit=False):
        name = st.text_input("اسم المنتج", value=product_to_edit.name if product_to_edit else "")
        quantity = st.number_input("الكمية", min_value=0, step=1, value=product_to_edit.quantity if product_to_edit else 0)
        price = st.number_input("السعر", min_value=0.0, format="%.2f", value=product_to_edit.price if product_to_edit else 0.0)
        supplier = st.text_input("المورّد", value=product_to_edit.supplier if product_to_edit else "")
            
        submitted = st.form_submit_button("💾 حفظ البيانات")
        if submitted:
            if not name:
                st.error("❌ اسم المنتج مطلوب!")
            else:
                if product_to_edit: # هذا يعني أننا في وضع التعديل
                    product_to_edit.name = name
                    product_to_edit.quantity = quantity
                    product_to_edit.price = price
                    product_to_edit.supplier = supplier
                    st.success(f"✅ تم تعديل المنتج '{name}' بنجاح!")
                else: # هذا يعني أننا في وضع الإضافة
                    new_product = Product(name=name, quantity=quantity, price=price, supplier=supplier)
                    db.add(new_product)
                    st.success(f"🎉 تم إضافة المنتج '{name}' بنجاح!")
                    
                db.commit()
                st.rerun()

with col2:
    st.header("🔍 بحث في المخزون")
    search_term = st.text_input("ابحث بالاسم أو المورّد...")

st.markdown("---")

# --- 2. قسم عرض المنتجات ---
st.header("📋 المنتجات الموجودة في المخزون")

query = db.query(Product)
if search_term:
    query = query.filter(or_(
        Product.name.ilike(f"%{search_term}%"),
        Product.supplier.ilike(f"%{search_term}%")
    ))
    
all_products = query.order_by(Product.id.desc()).all()

if not all_products:
    st.info("ℹ️ لا توجد منتجات في المخزون حالياً.")
else:
    # إنشاء الأعمدة للعناوين
    c1, c2, c3, c4, c5, c6 = st.columns([2, 1, 1, 2, 2, 1])
    c1.markdown("اسم المنتج")
    c2.markdown("الكمية")
    c3.markdown("السعر")
    c4.markdown("المورّد")
    c5.markdown("زمن الإضافة")
    c6.markdown("حذف")
    for p in all_products:
        col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 2, 2, 1])
        with col1:
            st.write(p.name)
        with col2:
            st.write(p.quantity)
        with col3:
            st.write(f"{p.price:,.2f}")
        with col4:
            st.write(p.supplier)
        with col5:
            st.write(p.added_at.strftime("%Y-%m-%d %H:%M")) # تنسيق الزمن
        with col6:
            if st.button("🗑️", key=f"del_{p.id}"):
                db.delete(p)
                db.commit()
                st.rerun()
    
db.close()
