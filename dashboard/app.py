"""
OBA Smart Assistant - Admin Dashboard
Streamlit-based analytics and management dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# Page configuration
st.set_page_config(
    page_title="OBA Smart Assistant - Admin Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# Helper functions
@st.cache_data(ttl=300)
def load_data(filename):
    """Load data from CSV file with caching."""
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return pd.DataFrame()


def format_currency(value):
    """Format value as currency."""
    return f"{value:,.2f} AZN"


def format_number(value):
    """Format large numbers with K/M suffix."""
    if value >= 1000000:
        return f"{value/1000000:.1f}M"
    elif value >= 1000:
        return f"{value/1000:.1f}K"
    return str(int(value))


# Sidebar navigation
st.sidebar.markdown('<p class="main-header">📊 OBA Admin</p>', unsafe_allow_html=True)
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Səhifə seçin",
    ["🏠 Ana Səhifə", "📈 Satış Analitikası", "👥 İstifadəçilər", 
     "📦 Məhsullar", "⚠️ Şikayətlər", "🔮 Proqnoz", "💬 Sentiment"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filterlər")

# Date range filter
date_range = st.sidebar.date_input(
    "Tarix aralığı",
    value=(datetime.now() - timedelta(days=30), datetime.now()),
    max_value=datetime.now()
)


# Main content based on selected page
if page == "🏠 Ana Səhifə":
    st.markdown('<p class="main-header">📊 OBA Smart Assistant Dashboard</p>', unsafe_allow_html=True)
    st.markdown("Ağıllı Alış-veriş Platforması - Real-time Analitika")
    
    # Load data
    orders_df = load_data('orders.csv')
    users_df = load_data('users.csv')
    products_df = load_data('products.csv')
    complaints_df = load_data('complaints.csv')
    
    # KPI Metrics Row
    st.markdown("### 📊 Əsas Göstəricilər")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = orders_df['total_amount'].sum() if not orders_df.empty else 0
        st.metric(
            label="Ümumi Satış",
            value=format_currency(total_revenue),
            delta="+12.5%"
        )
    
    with col2:
        total_orders = len(orders_df) if not orders_df.empty else 0
        st.metric(
            label="Sifariş Sayı",
            value=format_number(total_orders),
            delta="+8.2%"
        )
    
    with col3:
        total_users = len(users_df) if not users_df.empty else 0
        st.metric(
            label="İstifadəçi Sayı",
            value=format_number(total_users),
            delta="+15.3%"
        )
    
    with col4:
        avg_order = orders_df['total_amount'].mean() if not orders_df.empty else 0
        st.metric(
            label="Orta Sifariş",
            value=format_currency(avg_order),
            delta="+3.1%"
        )
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Son 30 Günlük Satışlar")
        if not orders_df.empty:
            orders_df['created_at'] = pd.to_datetime(orders_df['created_at'])
            daily_sales = orders_df.groupby(orders_df['created_at'].dt.date)['total_amount'].sum().reset_index()
            daily_sales.columns = ['Tarix', 'Satış']
            
            fig = px.line(
                daily_sales, 
                x='Tarix', 
                y='Satış',
                title="",
                labels={'Satış': 'Satış (AZN)'}
            )
            fig.update_traces(line_color='#1E88E5', line_width=2)
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Satış (AZN)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Satış məlumatları yüklənir...")
    
    with col2:
        st.markdown("### 🥧 Kateqoriyalara görə Satış")
        if not products_df.empty and 'sold_count' in products_df.columns:
            # Sample category distribution
            categories_df = load_data('categories.csv')
            if not categories_df.empty:
                # Merge products with categories
                merged = products_df.merge(
                    categories_df[['id', 'name']], 
                    left_on='category_id', 
                    right_on='id',
                    how='left',
                    suffixes=('', '_category')
                )
                category_sales = merged.groupby('name')['sold_count'].sum().reset_index()
                category_sales.columns = ['Kateqoriya', 'Satış']
                
                fig = px.pie(
                    category_sales.head(8),
                    values='Satış',
                    names='Kateqoriya',
                    hole=0.4
                )
                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Kateqoriya məlumatları yüklənir...")
    
    # Second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📦 Sifariş Statusları")
        if not orders_df.empty:
            status_counts = orders_df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Say']
            
            status_names = {
                'delivered': 'Çatdırıldı',
                'processing': 'Hazırlanır',
                'shipped': 'Yolda',
                'cancelled': 'Ləğv edildi',
                'pending': 'Gözləyir'
            }
            status_counts['Status'] = status_counts['Status'].map(status_names).fillna(status_counts['Status'])
            
            fig = px.bar(
                status_counts,
                x='Status',
                y='Say',
                color='Status',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Sifariş Sayı")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### ⚠️ Şikayət Statusları")
        if not complaints_df.empty:
            complaint_status = complaints_df['status'].value_counts().reset_index()
            complaint_status.columns = ['Status', 'Say']
            
            status_names = {
                'pending': 'Gözləyir',
                'in_progress': 'Baxılır',
                'resolved': 'Həll edildi',
                'closed': 'Bağlandı'
            }
            complaint_status['Status'] = complaint_status['Status'].map(status_names).fillna(complaint_status['Status'])
            
            colors = {'Gözləyir': '#FFA726', 'Baxılır': '#42A5F5', 
                     'Həll edildi': '#66BB6A', 'Bağlandı': '#78909C'}
            
            fig = px.bar(
                complaint_status,
                x='Status',
                y='Say',
                color='Status',
                color_discrete_map=colors
            )
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Şikayət Sayı")
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.markdown("---")
    st.markdown("### 🕐 Son Aktivlik")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Son Sifarişlər")
        if not orders_df.empty:
            recent_orders = orders_df.sort_values('created_at', ascending=False).head(5)
            recent_orders = recent_orders[['order_number', 'total_amount', 'status', 'created_at']]
            recent_orders.columns = ['Sifariş №', 'Məbləğ (AZN)', 'Status', 'Tarix']
            st.dataframe(recent_orders, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### Son Şikayətlər")
        if not complaints_df.empty:
            recent_complaints = complaints_df.sort_values('created_at', ascending=False).head(5)
            recent_complaints = recent_complaints[['ticket_number', 'category', 'priority', 'status']]
            recent_complaints.columns = ['Bilet №', 'Kateqoriya', 'Prioritet', 'Status']
            st.dataframe(recent_complaints, use_container_width=True, hide_index=True)


elif page == "📈 Satış Analitikası":
    st.markdown('<p class="main-header">📈 Satış Analitikası</p>', unsafe_allow_html=True)
    
    orders_df = load_data('orders.csv')
    order_items_df = load_data('order_items.csv')
    
    if not orders_df.empty:
        orders_df['created_at'] = pd.to_datetime(orders_df['created_at'])
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Ümumi Satış", format_currency(orders_df['total_amount'].sum()))
        with col2:
            st.metric("Orta Sifariş", format_currency(orders_df['total_amount'].mean()))
        with col3:
            st.metric("Sifariş Sayı", format_number(len(orders_df)))
        with col4:
            delivered = len(orders_df[orders_df['status'] == 'delivered'])
            st.metric("Çatdırılma %", f"{delivered/len(orders_df)*100:.1f}%")
        
        st.markdown("---")
        
        # Sales trend chart
        st.markdown("### 📈 Satış Trendi")
        
        time_granularity = st.selectbox(
            "Zaman ölçüsü",
            ["Günlük", "Həftəlik", "Aylıq"]
        )
        
        if time_granularity == "Günlük":
            grouped = orders_df.groupby(orders_df['created_at'].dt.date)['total_amount'].sum()
        elif time_granularity == "Həftəlik":
            grouped = orders_df.groupby(orders_df['created_at'].dt.isocalendar().week)['total_amount'].sum()
        else:
            grouped = orders_df.groupby(orders_df['created_at'].dt.month)['total_amount'].sum()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=grouped.index,
            y=grouped.values,
            mode='lines+markers',
            name='Satış',
            line=dict(color='#1E88E5', width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(
            xaxis_title="Zaman",
            yaxis_title="Satış (AZN)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top products
        st.markdown("### 🏆 Ən Çox Satılan Məhsullar")
        if not order_items_df.empty:
            top_products = order_items_df.groupby('product_name').agg({
                'quantity': 'sum',
                'subtotal': 'sum'
            }).sort_values('subtotal', ascending=False).head(10)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    top_products.reset_index(),
                    x='subtotal',
                    y='product_name',
                    orientation='h',
                    title="Satışa görə"
                )
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    top_products.reset_index(),
                    x='quantity',
                    y='product_name',
                    orientation='h',
                    title="Miqdarına görə",
                    color_discrete_sequence=['#66BB6A']
                )
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sifariş məlumatları tapılmadı.")


elif page == "👥 İstifadəçilər":
    st.markdown('<p class="main-header">👥 İstifadəçi Analitikası</p>', unsafe_allow_html=True)
    
    users_df = load_data('users.csv')
    orders_df = load_data('orders.csv')
    
    if not users_df.empty:
        # User metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Ümumi İstifadəçi", format_number(len(users_df)))
        with col2:
            active_users = len(users_df[users_df['is_active'] == True])
            st.metric("Aktiv İstifadəçi", format_number(active_users))
        with col3:
            avg_points = users_df['points'].mean()
            st.metric("Orta Xal", f"{avg_points:.0f}")
        with col4:
            total_points = users_df['points'].sum()
            st.metric("Ümumi Xal", format_number(total_points))
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏅 Xal Dağılımı")
            
            # Create tier categories
            def get_tier(points):
                if points >= 5000:
                    return 'Platinum'
                elif points >= 2000:
                    return 'Gold'
                elif points >= 500:
                    return 'Silver'
                return 'Bronze'
            
            users_df['tier'] = users_df['points'].apply(get_tier)
            tier_counts = users_df['tier'].value_counts()
            
            fig = px.pie(
                values=tier_counts.values,
                names=tier_counts.index,
                color=tier_counts.index,
                color_discrete_map={
                    'Bronze': '#CD7F32',
                    'Silver': '#C0C0C0',
                    'Gold': '#FFD700',
                    'Platinum': '#E5E4E2'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Qeydiyyat Trendi")
            users_df['created_at'] = pd.to_datetime(users_df['created_at'])
            monthly_users = users_df.groupby(users_df['created_at'].dt.to_period('M')).size()
            
            fig = px.bar(
                x=[str(x) for x in monthly_users.index],
                y=monthly_users.values,
                labels={'x': 'Ay', 'y': 'Yeni İstifadəçi'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # User table
        st.markdown("### 📋 İstifadəçi Siyahısı")
        
        search_term = st.text_input("Axtar (email və ya ad)")
        
        display_df = users_df[['email', 'full_name', 'phone', 'points', 'is_active', 'created_at']].copy()
        display_df.columns = ['Email', 'Ad Soyad', 'Telefon', 'Xal', 'Aktiv', 'Qeydiyyat']
        
        if search_term:
            mask = (display_df['Email'].str.contains(search_term, case=False, na=False) |
                   display_df['Ad Soyad'].str.contains(search_term, case=False, na=False))
            display_df = display_df[mask]
        
        st.dataframe(display_df.head(20), use_container_width=True, hide_index=True)


elif page == "📦 Məhsullar":
    st.markdown('<p class="main-header">📦 Məhsul Analitikası</p>', unsafe_allow_html=True)
    
    products_df = load_data('products.csv')
    categories_df = load_data('categories.csv')
    
    if not products_df.empty:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Ümumi Məhsul", format_number(len(products_df)))
        with col2:
            active = len(products_df[products_df['is_active'] == True])
            st.metric("Aktiv Məhsul", format_number(active))
        with col3:
            low_stock = len(products_df[products_df['stock_quantity'] < 10])
            st.metric("Az Stok", format_number(low_stock))
        with col4:
            avg_rating = products_df['avg_rating'].mean()
            st.metric("Orta Reytinq", f"{avg_rating:.1f} ⭐")
        
        st.markdown("---")
        
        # Category filter
        if not categories_df.empty:
            category_options = ['Hamısı'] + categories_df['name'].tolist()
            selected_category = st.selectbox("Kateqoriya", category_options)
            
            if selected_category != 'Hamısı':
                category_id = categories_df[categories_df['name'] == selected_category]['id'].values[0]
                products_df = products_df[products_df['category_id'] == category_id]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Stok Vəziyyəti")
            
            def stock_status(qty):
                if qty == 0:
                    return 'Stokda yoxdur'
                elif qty < 10:
                    return 'Az qaldı'
                elif qty < 50:
                    return 'Normal'
                return 'Çox'
            
            products_df['stock_status'] = products_df['stock_quantity'].apply(stock_status)
            stock_counts = products_df['stock_status'].value_counts()
            
            fig = px.pie(
                values=stock_counts.values,
                names=stock_counts.index,
                color=stock_counts.index,
                color_discrete_map={
                    'Stokda yoxdur': '#F44336',
                    'Az qaldı': '#FF9800',
                    'Normal': '#4CAF50',
                    'Çox': '#2196F3'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### ⭐ Reytinq Dağılımı")
            
            fig = px.histogram(
                products_df,
                x='avg_rating',
                nbins=10,
                labels={'avg_rating': 'Reytinq', 'count': 'Məhsul Sayı'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Low stock alerts
        st.markdown("### ⚠️ Az Stoklu Məhsullar")
        low_stock_products = products_df[products_df['stock_quantity'] < 10][
            ['name', 'stock_quantity', 'price', 'sold_count']
        ].sort_values('stock_quantity')
        low_stock_products.columns = ['Məhsul', 'Stok', 'Qiymət', 'Satış']
        
        st.dataframe(low_stock_products.head(10), use_container_width=True, hide_index=True)


elif page == "⚠️ Şikayətlər":
    st.markdown('<p class="main-header">⚠️ Şikayət İdarəetməsi</p>', unsafe_allow_html=True)
    
    complaints_df = load_data('complaints.csv')
    
    if not complaints_df.empty:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        pending = len(complaints_df[complaints_df['status'] == 'pending'])
        in_progress = len(complaints_df[complaints_df['status'] == 'in_progress'])
        resolved = len(complaints_df[complaints_df['status'] == 'resolved'])
        high_priority = len(complaints_df[complaints_df['priority'] == 'high'])
        
        with col1:
            st.metric("Gözləyən", pending, delta=None)
        with col2:
            st.metric("Baxılır", in_progress)
        with col3:
            st.metric("Həll edildi", resolved)
        with col4:
            st.metric("Yüksək Prioritet", high_priority, delta_color="inverse")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Kateqoriyaya görə")
            category_counts = complaints_df['category'].value_counts()
            
            category_names = {
                'product': 'Məhsul',
                'service': 'Xidmət',
                'delivery': 'Çatdırılma',
                'pricing': 'Qiymət',
                'other': 'Digər'
            }
            
            fig = px.pie(
                values=category_counts.values,
                names=[category_names.get(x, x) for x in category_counts.index],
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Prioritetə görə")
            priority_counts = complaints_df['priority'].value_counts()
            
            priority_names = {'high': 'Yüksək', 'medium': 'Orta', 'low': 'Aşağı'}
            
            fig = px.bar(
                x=[priority_names.get(x, x) for x in priority_counts.index],
                y=priority_counts.values,
                color=[priority_names.get(x, x) for x in priority_counts.index],
                color_discrete_map={
                    'Yüksək': '#F44336',
                    'Orta': '#FF9800',
                    'Aşağı': '#4CAF50'
                }
            )
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Say")
            st.plotly_chart(fig, use_container_width=True)
        
        # Complaints table
        st.markdown("### 📋 Şikayət Siyahısı")
        
        status_filter = st.selectbox(
            "Status",
            ['Hamısı', 'Gözləyir', 'Baxılır', 'Həll edildi', 'Bağlandı']
        )
        
        status_map = {
            'Gözləyir': 'pending',
            'Baxılır': 'in_progress',
            'Həll edildi': 'resolved',
            'Bağlandı': 'closed'
        }
        
        display_df = complaints_df.copy()
        if status_filter != 'Hamısı':
            display_df = display_df[display_df['status'] == status_map[status_filter]]
        
        display_df = display_df[['ticket_number', 'category', 'priority', 'subject', 'status', 'created_at']]
        display_df.columns = ['Bilet №', 'Kateqoriya', 'Prioritet', 'Mövzu', 'Status', 'Tarix']
        
        st.dataframe(display_df.head(20), use_container_width=True, hide_index=True)


elif page == "🔮 Proqnoz":
    st.markdown('<p class="main-header">🔮 Tələb Proqnozu</p>', unsafe_allow_html=True)
    
    sales_df = load_data('sales_history.csv')
    products_df = load_data('products.csv')
    
    if not sales_df.empty:
        st.markdown("### 📈 Məhsul Tələb Proqnozu")
        
        # Get product options
        product_ids = sales_df['product_id'].unique()[:10]
        
        if not products_df.empty:
            product_options = products_df[products_df['id'].isin(product_ids)]['name'].tolist()
            selected_product = st.selectbox("Məhsul seçin", product_options)
            
            if selected_product:
                product_id = products_df[products_df['name'] == selected_product]['id'].values[0]
                product_sales = sales_df[sales_df['product_id'] == product_id].copy()
                product_sales['date'] = pd.to_datetime(product_sales['date'])
                product_sales = product_sales.sort_values('date')
                
                # Simple moving average forecast
                window = st.slider("Hərəkətli orta pəncərəsi (gün)", 3, 14, 7)
                
                product_sales['ma'] = product_sales['quantity'].rolling(window=window).mean()
                
                # Forecast next 7 days
                last_ma = product_sales['ma'].iloc[-1]
                forecast_dates = pd.date_range(
                    start=product_sales['date'].max() + timedelta(days=1),
                    periods=7
                )
                
                fig = go.Figure()
                
                # Historical data
                fig.add_trace(go.Scatter(
                    x=product_sales['date'],
                    y=product_sales['quantity'],
                    mode='lines',
                    name='Faktiki',
                    line=dict(color='#1E88E5')
                ))
                
                # Moving average
                fig.add_trace(go.Scatter(
                    x=product_sales['date'],
                    y=product_sales['ma'],
                    mode='lines',
                    name='Hərəkətli Orta',
                    line=dict(color='#FF9800', dash='dash')
                ))
                
                # Forecast
                fig.add_trace(go.Scatter(
                    x=forecast_dates,
                    y=[last_ma] * 7,
                    mode='lines+markers',
                    name='Proqnoz',
                    line=dict(color='#4CAF50', dash='dot')
                ))
                
                fig.update_layout(
                    xaxis_title="Tarix",
                    yaxis_title="Satış Miqdarı",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Stock recommendation
                current_stock = products_df[products_df['name'] == selected_product]['stock_quantity'].values[0]
                forecast_demand = last_ma * 7
                
                st.markdown("### 📊 Stok Tövsiyəsi")
                col1, col2, col2 = st.columns(3)
                
                with col1:
                    st.metric("Cari Stok", int(current_stock))
                with col2:
                    st.metric("7 Günlük Proqnoz Tələbi", int(forecast_demand))
                with col2:
                    if current_stock < forecast_demand:
                        st.warning(f"⚠️ {int(forecast_demand - current_stock)} ədəd sifariş verin")
                    else:
                        st.success("✅ Stok kifayətdir")
    else:
        st.warning("Satış tarixi məlumatları tapılmadı.")


elif page == "💬 Sentiment":
    st.markdown('<p class="main-header">💬 Sentiment Analizi</p>', unsafe_allow_html=True)
    
    reviews_df = load_data('reviews.csv')
    
    if not reviews_df.empty:
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        positive = len(reviews_df[reviews_df['sentiment'] == 'positive'])
        neutral = len(reviews_df[reviews_df['sentiment'] == 'neutral'])
        negative = len(reviews_df[reviews_df['sentiment'] == 'negative'])
        total = len(reviews_df)
        
        with col1:
            st.metric("Pozitiv 😊", f"{positive} ({positive/total*100:.1f}%)")
        with col2:
            st.metric("Neytral 😐", f"{neutral} ({neutral/total*100:.1f}%)")
        with col3:
            st.metric("Neqativ 😞", f"{negative} ({negative/total*100:.1f}%)")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Sentiment Dağılımı")
            sentiment_counts = reviews_df['sentiment'].value_counts()
            
            fig = px.pie(
                values=sentiment_counts.values,
                names=['Pozitiv', 'Neytral', 'Neqativ'],
                color=['Pozitiv', 'Neytral', 'Neqativ'],
                color_discrete_map={
                    'Pozitiv': '#4CAF50',
                    'Neytral': '#FF9800',
                    'Neqativ': '#F44336'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### ⭐ Reytinq Dağılımı")
            rating_counts = reviews_df['rating'].value_counts().sort_index()
            
            fig = px.bar(
                x=rating_counts.index,
                y=rating_counts.values,
                color=rating_counts.index,
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(
                xaxis_title="Reytinq",
                yaxis_title="Rəy Sayı",
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent reviews
        st.markdown("### 📝 Son Rəylər")
        
        sentiment_filter = st.selectbox(
            "Sentiment",
            ['Hamısı', 'Pozitiv', 'Neytral', 'Neqativ']
        )
        
        display_df = reviews_df.copy()
        if sentiment_filter != 'Hamısı':
            sentiment_map = {'Pozitiv': 'positive', 'Neytral': 'neutral', 'Neqativ': 'negative'}
            display_df = display_df[display_df['sentiment'] == sentiment_map[sentiment_filter]]
        
        display_df = display_df[['rating', 'comment', 'sentiment', 'created_at']].sort_values('created_at', ascending=False)
        display_df.columns = ['Reytinq', 'Rəy', 'Sentiment', 'Tarix']
        
        st.dataframe(display_df.head(20), use_container_width=True, hide_index=True)
        
        # Test sentiment analyzer
        st.markdown("### 🧪 Sentiment Test")
        test_text = st.text_area("Rəy mətni daxil edin")
        
        if st.button("Analiz et"):
            if test_text:
                # Simple rule-based analysis for demo
                positive_words = ['yaxşı', 'əla', 'gözəl', 'super', 'mükəmməl', 'tövsiyə']
                negative_words = ['pis', 'xarab', 'köhnə', 'baha', 'xətə', 'problem']
                
                text_lower = test_text.lower()
                pos_count = sum(1 for word in positive_words if word in text_lower)
                neg_count = sum(1 for word in negative_words if word in text_lower)
                
                if pos_count > neg_count:
                    st.success(f"😊 Pozitiv (güvən: {pos_count/(pos_count+neg_count+1)*100:.0f}%)")
                elif neg_count > pos_count:
                    st.error(f"😞 Neqativ (güvən: {neg_count/(pos_count+neg_count+1)*100:.0f}%)")
                else:
                    st.warning("😐 Neytral")
    else:
        st.warning("Rəy məlumatları tapılmadı.")


# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📞 Dəstək")
st.sidebar.info("Texniki dəstək: support@oba.az")
st.sidebar.markdown(f"v1.0.0 | © {datetime.now().year} OBA")
