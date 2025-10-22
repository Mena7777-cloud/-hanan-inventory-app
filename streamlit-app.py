import streamlit as st
import sqlalchemy
from sqlalchemy import func
from database import SessionLocal, Product, User, verify_password, hash_password

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام المخزون الاحترافي", page_icon="🚀", layout="wide")

# --- دوال مساعدة لإنشاء المستخدمين ---
def create_initial_users():
    db = SessionLocal()
    # التأكد من عدم وجود مستخدمين قبل الإنشاء
    if db.query(User).count() == 0:
        # إنشاء مدير
        admin_pass = hash_password("admin123")
        admin_user = User(username="admin", password_hash=admin_pass, role="admin")
        db.add(admin_user)
        # إنشاء مستخدم عادي
        user_pass = hash_password("user123")
        normal_user = User(username="user", password_hash=user_pass, role="user")
        db.add(normal_user)
        db.commit()
    db.close()

# --- بداية التطبيق ---
# إنشاء المستخدمين عند أول تشغيل فقط
create_initial_users()

# التحقق من حالة تسجيل الدخول
if "user" not in st.session_state:
    st.session_state.user = None

# --- صفحة تسجيل الدخول ---
if st.session_state.user is None:
    st.title("🔐 تسجيل الدخول - نظام المخزون")
    with st.form("login_form"):
        username = st.text_input("اسم المستخدم", help="جرب: admin أو user")
        password = st.text_input("كلمة المرور", type="password", help="جرب: admin123 أو user123")
        submitted = st.form_submit_button("تسجيل الدخول")
        if submitted:
            db = SessionLocal()
            user_from_db = db.query(User).filter(User.username == username).first()
            db.close()
            if user_from_db and verify_password(password, user_from_db.password_hash):
                st.session_state.user = user_from_db
                st.experimental_rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
# --- الواجهة الرئيسية بعد تسجيل الدخول ---
else:
    user = st.session_state.user
    st.sidebar.title(f"👋 أهلاً, {user.username}")
    st.sidebar.info(f"صلاحياتك: {user.role.upper()}")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.user = None
        st.experimental_rerun()

    st.title("🚀 نظام إدارة المخزون الاحترافي الكامل")
    
    # تعريف التابات بناءً على صلاحيات المستخدم
    tabs_list = ["📊 لوحة التحكم", "📋 عرض المخزون"]
    if user.role == "admin":
        tabs_list.append("➕ إضافة منتج")
        tabs_list.append("✏️ تعديل منتج")

    selected_tab = st.sidebar.radio("اختر القسم:", tabs_list)
    db = SessionLocal()

    # --- تاب لوحة التحكم ---
    if selected_tab == "📊 لوحة التحكم":
        st.header("📊 لوحة التحكم والإحصائيات")
        total_products = db.query(Product).count()
        total_units = db.query(func.sum(Product.quantity)).scalar() or 0
        total_value = db.query(func.sum(Product.price * Product.quantity)).scalar() or 0.0
        col1, col2, col3 = st.columns(3)
        col1.metric("إجمالي أصناف المنتجات", total_products)
        col2.metric("إجمالي الوحدات في المخزون", total_units)
        col3.metric("القيمة الإجمالية للمخزون", f"{total_value:,.2f} ج.م")

    # --- تاب عرض المخزون ---
    elif selected_tab == "📋 عرض المخزون":
        st.header("📋 عرض المخزون والبحث")
        search_term = st.text_input("ابحث بالاسم، SKU، المجموعة، أو العلامة التجارية...")
        query = db.query(Product)
        if search_term:
            search_filter = f"%{search_term}%"
            query = query.filter(sqlalchemy.or_(
                Product.name.ilike(search_filter), Product.sku.ilike(search_filter),
                Product.group.ilike(search_filter), Product.brand.ilike(search_filter)
            ))
        products = query.order_by(Product.id.desc()).all()
        
        if not products:
            st.info("لا توجد منتجات تطابق بحثك.")
        
        for p in products:
            with st.expander(f"{p.name} (الكمية: {p.quantity})"):
              st.markdown(f"""
                - SKU: {p.sku if p.sku else 'غير متوفر'}
                - الوصف: {p.description if p.description else 'لا يوجد'}
                - السعر: {p.price:,.2f} ج.م
                - المجموعة: {p.group if p.group else 'لا يوجد'} | العلامة التجارية: {p.brand if p.brand else 'لا يوجد'} | المورّد: {p.supplier if p.supplier else 'لا يوجد'}
                """)
                if user.role == "admin":
                    if st.button("🗑️ حذف", key=f"del_{p.id}", type="primary"):
                        db.delete(p)
                        db.commit()
                        st.success(f"تم حذف المنتج '{p.name}' بنجاح!")
                        st.experimental_rerun()

    # --- تاب إضافة منتج ---
    elif selected_tab == "➕ إضافة منتج" and user.role == "admin":
        st.header("➕ إضافة منتج جديد")
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("اسم المنتج*")
            sku = st.text_input("SKU (رقم المنتج الفريد)")
            description = st.text_area("وصف المنتج")
            quantity = st.number_input("الكمية*", min_value=0)
            price = st.number_input("السعر*", min_value=0.0, format="%.2f")
            group = st.text_input("المجموعة")
            brand = st.text_input("العلامة التجارية")
            supplier = st.text_input("المورّد")
            submitted = st.form_submit_button("✅ حفظ المنتج")
            if submitted:
                if not name or price <= 0:
                    st.error("❌ الرجاء إدخال اسم المنتج وسعر صحيح.")
                else:
                    new_product = Product(name=name, sku=sku, description=description, quantity=quantity, price=price, group=group, brand=brand, supplier=supplier)
                    db.add(new_product)
                    db.commit()
                    st.success("🎉 تم إضافة المنتج بنجاح!")
                    st.balloons()
                    st.experimental_rerun()

    # --- تاب تعديل منتج ---
    elif selected_tab == "✏️ تعديل منتج" and user.role == "admin":
        st.header("✏️ تعديل بيانات منتج")
        products = db.query(Product).order_by(Product.name).all()
        if not products:
            st.warning("لا توجد منتجات لتعديلها. قم بإضافة منتج أولاً.")
        else:
            product_to_edit = st.selectbox("اختر المنتج للتعديل:", options=products, format_func=lambda p: f"{p.name} (SKU: {p.sku if p.sku else 'N/A'})")
            if product_to_edit:
                with st.form("edit_form"):
                    st.write(f"جاري تعديل المنتج: {product_to_edit.name}")
                    name = st.text_input("اسم المنتج", value=product_to_edit.name)
                    sku = st.text_input("SKU", value=product_to_edit.sku)
                    description = st.text_area("الوصف", value=product_to_edit.description)
                    quantity = st.number_input("الكمية", value=product_to_edit.quantity)
                    price = st.number_input("السعر", value=product_to_edit.price, format="%.2f")
                    group = st.text_input("المجموعة", value=product_to_edit.group)
                    brand = st.text_input("العلامة التجارية", value=product_to_edit.brand)
                    supplier = st.text_input("المورّد", value=product_to_edit.supplier)
                    update_submitted = st.form_submit_button("💾 تحديث البيانات")
                    if update_submitted:
                        if not name or price <= 0:
                            st.error("❌ الرجاء إدخال اسم المنتج وسعر صحيح.")
                        else:
                            # تحديث البيانات في قاعدة البيانات
                            product_to_edit.name = name
                            product_to_edit.sku = sku
                            product_to_edit.description = description
                          product_to_edit.quantity = quantity
                            product_to_edit.price = price
                            product_to_edit.group = group
                            product_to_edit.brand = brand
                            product_to_edit.supplier = supplier
                            db.commit()
                            st.success("✅ تم تحديث بيانات المنتج بنجاح!")
                            st.experimental_rerun()
    db.close()
