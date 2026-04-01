import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import database as db

# --- PAGE CONFIG ---
st.set_page_config(page_title="Tambang OS", layout="wide", page_icon="⛏️")

# Make sure tables exist
db.create_tables()

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3204/3204781.png", width=80)
st.sidebar.title("Tambang OS")
page = st.sidebar.radio("Navigasi", ["📊 Dashboard Manajemen", "📝 Form Input Harian", "⚙️ Sync Data Excel"])
st.sidebar.markdown("---")

if page == "📊 Dashboard Manajemen":
    # Load Data from SQLite
    try:
        df_prod = db.load_data_to_df("production")
        df_unit = db.load_data_to_df("unit_performance")
        df_delay = db.load_data_to_df("delays")
    except Exception as e:
        st.error(f"Error loading database: {e}")
        df_prod = pd.DataFrame()
        df_unit = pd.DataFrame()
        df_delay = pd.DataFrame()

    if df_prod.empty:
        st.warning("Database kosong. Silakan masuk ke menu 'Sync Data Excel' untuk memuat 12 bulan data, atau isi manual di 'Form Input Harian'.")
    else:
        # --- FILTERS ---
        st.sidebar.subheader("Filter Data")
        min_date = df_prod['date'].min()
        max_date = df_prod['date'].max()
        
        date_range = st.sidebar.date_input("Periode", [min_date, max_date], min_value=min_date, max_value=max_date)
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range[0]
            
        shifts = df_prod['shift'].unique()
        shift_filter = st.sidebar.multiselect("Shift", shifts, default=shifts)

        # Apply Filters
        mask_prod = (df_prod['date'] >= start_date) & (df_prod['date'] <= end_date) & (df_prod['shift'].isin(shift_filter))
        filtered_prod = df_prod[mask_prod]
        
        mask_unit = (df_unit['date'] >= start_date) & (df_unit['date'] <= end_date) & (df_unit['shift'].isin(shift_filter))
        filtered_unit = df_unit[mask_unit]
        
        mask_delay = (df_delay['date'] >= start_date) & (df_delay['date'] <= end_date) & (df_delay['shift'].isin(shift_filter))
        filtered_delay = df_delay[mask_delay]

        # --- DASHBOARD HEADER ---
        st.title("📊 Operational Dashboard (12 Months Data)")
        st.markdown("Monitoring KPI Produksi, Alat, dan Hambatan.")

        # --- TOP KPIs ---
        col1, col2, col3, col4 = st.columns(4)
        
        ore_prod = filtered_prod[filtered_prod['material'] == 'Ore']
        total_ore_plan = ore_prod['plan'].sum()
        total_ore_actual = ore_prod['actual'].sum()
        achiev_ore = (total_ore_actual / total_ore_plan) * 100 if total_ore_plan > 0 else 0
        
        ob_prod = filtered_prod[filtered_prod['material'] == 'OB']
        total_ob_actual = ob_prod['actual'].sum()
        
        avg_pa = filtered_unit['pa'].mean() if not filtered_unit.empty else 0
        avg_ua = filtered_unit['ua'].mean() if not filtered_unit.empty else 0

        col1.metric("Total Ore Actual", f"{total_ore_actual:,.0f} MT", f"{achiev_ore:.1f}% vs Plan")
        col2.metric("Total OB Actual", f"{total_ob_actual:,.0f} BCM")
        col3.metric("Rata-rata PA", f"{avg_pa:.1f}%")
        col4.metric("Rata-rata UA", f"{avg_ua:.1f}%")
        
        st.markdown("---")

        # --- CHARTS ---
        c1, c2 = st.columns((2, 1))

        with c1:
            st.subheader("📈 Trend Produksi Ore (Plan vs Actual)")
            if not ore_prod.empty:
                ore_daily = ore_prod.groupby('date')[['plan', 'actual']].sum().reset_index()
                fig_prod = go.Figure()
                fig_prod.add_trace(go.Bar(x=ore_daily['date'], y=ore_daily['actual'], name='Actual', marker_color='#1f77b4'))
                fig_prod.add_trace(go.Scatter(x=ore_daily['date'], y=ore_daily['plan'], name='Plan', mode='lines', line=dict(color='#d62728', width=2)))
                fig_prod.update_layout(margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
                st.plotly_chart(fig_prod, use_container_width=True)
            else:
                st.info("Tidak ada data Ore di periode ini.")

        with c2:
            st.subheader("⏱️ Proporsi Delay/Hambatan")
            if not filtered_delay.empty:
                delay_summary = filtered_delay.groupby('cause')['hours'].sum().reset_index()
                fig_delay = px.pie(delay_summary, values='hours', names='cause', hole=0.4)
                fig_delay.update_layout(margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_delay, use_container_width=True)
            else:
                st.info("Tidak ada data Delay.")

        # --- UNIT PERFORMANCE ---
        st.subheader("🚜 Performa Unit (10 Teratas)")
        if not filtered_unit.empty:
            unit_summary = filtered_unit.groupby('unit')[['pa', 'ua', 'mohh', 'ewh', 'productivity']].mean().reset_index()
            unit_summary = unit_summary.sort_values(by='productivity', ascending=False).head(10)
            st.dataframe(unit_summary.style.format({"pa": "{:.1f}%", "ua": "{:.1f}%", "mohh": "{:.1f}", "ewh": "{:.1f}", "productivity": "{:.0f}"}), use_container_width=True)
        else:
            st.info("Tidak ada data performa unit.")

        st.markdown("---")
        
        # --- AI INSIGHTS FEATURE (DUMMY) ---
        st.subheader("🤖 AI Executive Summary")
        if st.button("✨ Generate AI Insights"):
            with st.spinner("Analyzing 12-month data patterns..."):
                insight_text = f"""
                **Analisis Otomatis (Periode: {start_date} hingga {end_date}):**
                
                *   **Pencapaian Produksi**: Pencapaian produksi berada di angka **{achiev_ore:.1f}%**. Target harian secara kumulatif {"terpenuhi dengan sangat baik." if achiev_ore >= 100 else "mengalami sedikit ketertinggalan, direkomendasikan evaluasi ketersediaan unit."}
                *   **Kesiapan Alat**: Physical Availability (PA) armada tercatat rata-rata **{avg_pa:.1f}%**. Nilai ini menunjukkan kondisi mekanis armada {"sehat dan prima." if avg_pa > 85 else "memerlukan perhatian khusus dari tim Maintenance/Plant."}
                *   **Faktor Hambatan Utama**: Kehilangan waktu terbesar disumbangkan oleh **{filtered_delay.groupby('cause')['hours'].sum().idxmax() if not filtered_delay.empty else 'N/A'}**. 
                """
                st.success("Analysis Complete!")
                st.info(insight_text)

elif page == "📝 Form Input Harian":
    st.title("📝 Data Entry Produksi & Unit")
    st.markdown("Form ini digunakan oleh *Checker* atau *Site Admin* untuk menginput data aktual harian ke dalam database.")
    
    tab1, tab2 = st.tabs(["Input Produksi", "Input Hambatan/Delay"])
    
    with tab1:
        with st.form("form_produksi"):
            st.subheader("Entry Produksi Ore & OB")
            col1, col2 = st.columns(2)
            input_date = col1.date_input("Tanggal Produksi", date.today())
            input_shift = col2.selectbox("Shift Kerja", ["Shift 1", "Shift 2"])
            
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            input_material = c1.selectbox("Material", ["Ore", "OB"])
            input_plan = c2.number_input("Target Plan (MT/BCM)", min_value=0, value=4500)
            input_actual = c3.number_input("Aktual (MT/BCM)", min_value=0, value=4000)
            
            submitted = st.form_submit_button("Simpan Data Produksi")
            if submitted:
                db.insert_production(input_date.strftime("%Y-%m-%d"), input_shift, input_material, input_plan, input_actual)
                st.success("✅ Data Produksi berhasil disimpan ke database!")

    with tab2:
        with st.form("form_delay"):
            st.subheader("Entry Hambatan/Delay Unit")
            col1, col2 = st.columns(2)
            d_date = col1.date_input("Tanggal", date.today())
            d_shift = col2.selectbox("Shift", ["Shift 1", "Shift 2"])
            
            d_unit = st.text_input("Nomor Unit (e.g., EX-101, DT-205)")
            c1, c2 = st.columns(2)
            d_cause = c1.selectbox("Penyebab Delay", ["Weather", "Breakdown", "Standby", "Refueling", "Meal Break"])
            d_hours = c2.number_input("Durasi Delay (Jam)", min_value=0.0, step=0.1, value=1.0)
            
            submitted_delay = st.form_submit_button("Simpan Data Delay")
            if submitted_delay:
                if d_unit:
                    conn = db.get_connection()
                    c = conn.cursor()
                    c.execute('INSERT INTO delays (date, shift, unit, cause, hours) VALUES (?, ?, ?, ?, ?)',
                              (d_date.strftime("%Y-%m-%d"), d_shift, d_unit, d_cause, d_hours))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Data delay untuk {d_unit} berhasil disimpan!")
                else:
                    st.error("Nomor unit harus diisi!")

elif page == "⚙️ Sync Data Excel":
    st.title("⚙️ Sinkronisasi Database dari Excel")
    st.markdown("Fitur ini digunakan untuk membaca seluruh 12 file Excel produksi dan memuatnya secara otomatis ke dalam **Database SQLite** agar bisa dibaca oleh Dashboard.")
    
    st.warning("Perhatian: Melakukan sinkronisasi ulang akan menghapus data lama dan membaca ulang file dari awal (12 Bulan).")
    
    if st.button("🔄 Jalankan Sinkronisasi (ETL)"):
        with st.spinner("Memproses 12 File Excel... Ini mungkin memakan waktu beberapa saat..."):
            import etl_script
            etl_script.run_etl()
            st.success("✅ Sinkronisasi 12 bulan data selesai! Silakan kembali ke Dashboard Manajemen.")
