import streamlit as st
import pandas as pd
import plotly.express as px
import time

st.set_page_config(page_title="SME Pricing Tool", layout="wide", page_icon="🔧")

# ===================== CSS =====================
st.markdown("""
<style>
.big-title {font-size:42px; font-weight:bold; margin-bottom:10px; text-align:center;}
.subtitle {font-size:20px; text-align:center; color:#555;}
.card {padding:25px; border-radius:15px; background-color:#f8f9fa; margin:15px 0;}
</style>
""", unsafe_allow_html=True)

# ===================== SESSION STATE =====================
if 'page' not in st.session_state:
    st.session_state.page = "intro"

# ===================== PAGE 1: GIỚI THIỆU =====================
if st.session_state.page == "intro":
    st.markdown('<p class="big-title">🔧 SME Pricing Simulation Tool</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Công cụ mô phỏng tăng giá thông minh dành cho doanh nghiệp SME Việt Nam</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://source.unsplash.com/800x400/?pricing,strategy", use_container_width=True)
        
        st.markdown("""
        ### Công cụ giúp bạn:
        - Xem lợi nhuận sẽ thay đổi khi tăng giá
        - Đánh giá rủi ro giảm đơn hàng
        - Nhận khuyến nghị chiến lược: **Aggressive - Balanced - Conservative**
        """)
        
        if st.button("🚀 Get Started", type="primary", use_container_width=True):
            st.session_state.page = "input"
            st.rerun()

# ===================== PAGE 2: INPUT =====================
elif st.session_state.page == "input":
    st.title("⚙️ Thiết lập thông số doanh nghiệp")
    st.caption("Nhập thông tin để công cụ phân tích")

    with st.sidebar:
        st.header("📌 Thông tin đầu vào")
        
        st.subheader("Nguyên vật liệu")
        material = st.selectbox("Loại vật liệu", ["Thép (15.5M/tấn)", "Inox (58M/tấn)", "Nhôm (65M/tấn)", "Đồng (240M/tấn)"])
        material_price = {"Thép (15.5M/tấn)": 15500000, "Inox (58M/tấn)": 58000000,
                         "Nhôm (65M/tấn)": 65000000, "Đồng (240M/tấn)": 240000000}
        
        tons = st.number_input("Sản lượng hiện tại (tấn/tháng)", value=120)
        
        st.subheader("Chi phí")
        workers = st.number_input("Số công nhân", value=25)
        salary = st.number_input("Lương trung bình/tháng (VNĐ)", value=9000000)
        electricity = st.number_input("Điện + mặt bằng/tháng (VNĐ)", value=320000000)
        maintenance_year = st.number_input("Bảo trì/năm (VNĐ)", value=250000000)
        machine_value = st.number_input("Giá trị máy móc (VNĐ)", value=3000000000)
        machine_life = st.number_input("Tuổi thọ máy (năm)", value=10)
        
        st.subheader("Kinh doanh")
        current_margin = st.slider("Margin hiện tại (%)", 0, 40, 18)
        win_rate = st.slider("Win rate hiện tại (%)", 0, 100, 35)
        orders = st.number_input("Số đơn hàng/tháng", value=40)
        
        st.subheader("Giả định thị trường")
        elasticity = st.slider("Độ nhạy giá (Elasticity)", 0.5, 3.0, 1.5)
        industry_growth = st.slider("Tăng trưởng ngành (%)", 0, 15, 5)
        inflation = st.slider("Lạm phát dự kiến (%)", 0, 12, 4)

        price_increases = [0, 5, 8, 10, 12, 15, 20]
        
        if st.button("🚀 Bắt đầu tính toán", type="primary"):
            st.session_state.page = "loading"
            st.session_state.inputs = {
                "material": material, "material_price": material_price[material], "tons": tons,
                "workers": workers, "salary": salary, "electricity": electricity,
                "maintenance_year": maintenance_year, "machine_value": machine_value,
                "machine_life": machine_life, "current_margin": current_margin,
                "win_rate": win_rate, "orders": orders, "elasticity": elasticity,
                "industry_growth": industry_growth, "inflation": inflation,
                "price_increases": price_increases
            }
            st.rerun()

# ===================== PAGE 3: LOADING =====================
elif st.session_state.page == "loading":
    st.title("Đang chạy mô phỏng...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(101):
        progress_bar.progress(i)
        if i < 30:
            status_text.text("Đang tính chi phí hiện tại...")
        elif i < 60:
            status_text.text("Đang mô phỏng các mức tăng giá...")
        elif i < 85:
            status_text.text("Phân tích rủi ro và lợi nhuận...")
        else:
            status_text.text("Đang tạo khuyến nghị chiến lược...")
        time.sleep(0.035)  # Tạo cảm giác loading
    
    # Chuyển sang trang kết quả
    st.session_state.page = "result"
    st.rerun()

# ===================== PAGE 4: KẾT QUẢ =====================
elif st.session_state.page == "result":
    inputs = st.session_state.inputs
    
    # ==================== TÍNH TOÁN ====================
    # Baseline
    mat_cost = inputs["material_price"] * inputs["tons"]
    labor_cost = inputs["workers"] * inputs["salary"]
    maintenance_month = inputs["maintenance_year"] / 12
    depreciation = inputs["machine_value"] / (inputs["machine_life"] * 12)
    fixed_cost = inputs["electricity"] + maintenance_month + depreciation
    total_cost = mat_cost + labor_cost + fixed_cost
    
    real_orders = inputs["orders"] * (inputs["win_rate"] / 100)
    cost_per_order = total_cost / max(real_orders, 1)
    current_price = cost_per_order / (1 - inputs["current_margin"] / 100)
    baseline_profit = (current_price - cost_per_order) * real_orders
    
    # Tính cho từng mức tăng giá
    results = []
    for inc in inputs["price_increases"]:
        demand_change = (inputs["industry_growth"]/100) - inputs["elasticity"] * (inc / 100)
        new_quantity = real_orders * (1 + demand_change)
        
        new_cost = cost_per_order * (1 + inputs["inflation"]/100)
        new_price = current_price * (1 + inc / 100)
        new_profit = (new_price - new_cost) * max(new_quantity, 0)
        profit_change = (new_profit - baseline_profit) / baseline_profit * 100 if baseline_profit != 0 else 0
        
        results.append({
            "Mức tăng giá (%)": inc,
            "Sản lượng mới": round(new_quantity, 1),
            "Giá bán mới": round(new_price, 0),
            "Lợi nhuận mới": round(new_profit, 0),
            "Thay đổi LN (%)": round(profit_change, 1)
        })
    
    df = pd.DataFrame(results)
    
    # ==================== HIỂN THỊ ====================
    st.success("✅ Hoàn thành mô phỏng!")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Lợi nhuận hiện tại", f"{baseline_profit:,.0f} VNĐ")
    best_row = df.loc[df["Lợi nhuận mới"].idxmax()]
    col2.metric("Lợi nhuận cao nhất", f"{best_row['Lợi nhuận mới']:,.0f} VNĐ", 
                f"{best_row['Thay đổi LN (%)']:+.1f}%")
    col3.metric("Khuyến nghị tăng", f"{best_row['Mức tăng giá (%)']}%")
    
    st.subheader("📊 Bảng so sánh chi tiết")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Biểu đồ
    fig1 = px.bar(df, x="Mức tăng giá (%)", y="Lợi nhuận mới", text_auto=True,
                  title="Lợi nhuận theo mức tăng giá")
    st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = px.line(df, x="Mức tăng giá (%)", y="Thay đổi LN (%)", markers=True,
                   title="Phần trăm thay đổi lợi nhuận")
    st.plotly_chart(fig2, use_container_width=True)
    
    # ===================== 3 KHUYẾN NGHỊ =====================
    st.subheader("🎯 Khuyến nghị Chiến lược")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("**🔥 Aggressive (Tối đa lợi nhuận)**")
        agg = df.loc[df["Lợi nhuận mới"].idxmax()]
        st.success(f"Tăng **{agg['Mức tăng giá (%)']}%**\nLợi nhuận: **{agg['Lợi nhuận mới']:,.0f} VNĐ**")
    
    with c2:
        st.markdown("**⚖️ Balanced (Cân bằng)**")
        balanced = df[(df["Thay đổi LN (%)"] > 5) & (df["Mức tăng giá (%)"] <= 12)]
        if not balanced.empty:
            bal = balanced.loc[balanced["Lợi nhuận mới"].idxmax()]
            st.info(f"Tăng **{bal['Mức tăng giá (%)']}%**\nLợi nhuận: **{bal['Lợi nhuận mới']:,.0f} VNĐ**")
        else:
            st.warning("Không có kịch bản cân bằng")
    
    with c3:
        st.markdown("**🛡️ Conservative (An toàn)**")
        cons = df.loc[df["Thay đổi LN (%)"].idxmax() if (df["Thay đổi LN (%)"] > 0).any() else df["Mức tăng giá (%)"].idxmin()]
        st.success(f"Tăng **{cons['Mức tăng giá (%)']}%**\nLợi nhuận: **{cons['Lợi nhuận mới']:,.0f} VNĐ**")
    
    if st.button("🔄 Thử lại với thông số khác"):
        st.session_state.page = "input"
        st.rerun()