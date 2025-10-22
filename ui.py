import streamlit as st

def draw_header():
    """يرسم العنوان الرئيسي للتطبيق"""
    st.title("📦 نظام إدارة المخزون")
    st.markdown("---")

def draw_add_edit_form(db, Product, product_to_edit):
    """يرسم فورم الإضافة والتعديل"""
    with st.form("product_form"):
        st.header("➕ إضافة / تعديل منتج")
        name = st.text_input("اسم المنتج", value=product_to_edit.name if product_to_edit else "")
        quantity = st.number_input("الكمية", min_value=0, step=1, value=product_to_edit.quantity if product_to_edit else 0)
        price = st.number_input("السعر", min_value=0.0, format="%.2f", value=product_to_edit.price if product_to_edit else 0.0)
        supplier = st.text_input("المورّد", value=product_to_edit.supplier if product_to_edit else "")
            
        submitted = st.form_submit_button("💾 حفظ البيانات")
        if submitted:
            if not name:
                st.error("❌ اسم المنتج مطلوب!")
                return

            if product_to_edit: # وضع التعديل
                product_to_edit.name = name
                product_to_edit.quantity = quantity
                product_to_edit.price = price
                product_to_edit.supplier = supplier
                st.success(f"✅ تم تعديل المنتج '{name}' بنجاح!")
            else: # وضع الإضافة
                new_product = Product(name=name, quantity=quantity, price=price, supplier=supplier)
                db.add(new_product)
                st.success(f"🎉 تم إضافة المنتج '{name}' بنجاح!")
                
            db.commit()
            st.rerun()

def draw_product_list(db, Product, products_to_display):
    """يرسم جدول عرض المنتجات مع زر الحذف"""
    st.header("📋 المنتجات في المخزون")
    if not products_to_display:
        st.info("ℹ️ لا توجد منتجات لعرضها.")
        return

    # عناوين الجدول
    c1, c2, c3, c4, c5, c6 = st.columns([2, 1, 1, 2, 2, 1])
    c1.markdown("اسم المنتج")
    c2.markdown("الكمية")
    c3.markdown("السعر")
    c4.markdown("المورّد")
    c5.markdown("زمن الإضافة")
    c6.markdown("حذف")

    # بيانات الجدول
    for p in products_to_display:
        col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 2, 2, 1])
        col1.write(p.name)
        col2.write(p.quantity)
        col3.write(f"{p.price:,.2f}")
        col4.write(p.supplier)
        col5.write(p.added_at.strftime("%Y-%m-%d %H:%M"))
        if col6.button("🗑️", key=f"del_{p.id}"):
            db.delete(p)
            db.commit()
            st.rerun()
