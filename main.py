import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------
# 1. 페이지 설정
# --------------------
st.set_page_config(
    page_title="국가별 관대함 비교 웹 앱",
    page_icon="🌍",
    layout="wide"
)

# --------------------
# 2. 데이터 로드
# --------------------
@st.cache_data
def load_data():
    """
    CSV 파일을 로드하고 필요한 컬럼명을 통일합니다.
    세계 지도 시각화를 위해 국가명과 ISO-ALPHA-3 코드 매핑을 시도합니다.
    """
    try:
        df = pd.read_csv('processed_whr_short.csv')
        # 컬럼명 통일 (예시: 실제 파일의 컬럼명에 따라 조정 필요)
        df.rename(columns={
            'country': 'Country',
            'Country': 'Country', # 이미 'Country'인 경우를 대비
            'generosity': 'Generosity',
            'Generosity': 'Generosity', # 이미 'Generosity'인 경우를 대비
            'year': 'Year', # 'Year' 컬럼이 있다면 사용
            'Year': 'Year' # 이미 'Year'인 경우를 대비
        }, inplace=True)

        # 필요한 컬럼만 선택
        required_columns = ['Country', 'Generosity']
        if 'Year' in df.columns:
            required_columns.append('Year')
        else:
            st.warning("Warning: 'Year' column not found. Year-based analysis features will be disabled.")

        # 필수 컬럼이 모두 있는지 확인
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}. Please check your file's column names.")
            return pd.DataFrame()

        df = df[required_columns]

        # --- 세계 지도 시각화를 위한 국가 코드 추가 ---
        # 실제 앱에서는 더 포괄적인 매핑 또는 pycountry 같은 라이브러리 사용을 권장합니다.
        # 여기서는 예시를 위해 몇몇 국가만 매핑합니다.
        country_to_iso = {
            'South Korea': 'KOR', 'United States': 'USA', 'Canada': 'CAN',
            'Germany': 'DEU', 'France': 'FRA', 'United Kingdom': 'GBR',
            'Japan': 'JPN', 'China': 'CHN', 'India': 'IND',
            'Australia': 'AUS', 'Brazil': 'BRA', 'Mexico': 'MEX',
            'Russia': 'RUS', 'Spain': 'ESP', 'Italy': 'ITA',
            'Sweden': 'SWE', 'Norway': 'NOR', 'Denmark': 'DNK',
            'Finland': 'FIN', 'Switzerland': 'CHE', 'Netherlands': 'NLD',
            'Belgium': 'BEL', 'Austria': 'AUT', 'New Zealand': 'NZL',
            'Argentina': 'ARG', 'South Africa': 'ZAF', 'Egypt': 'EGY',
            'Nigeria': 'NGA', 'Indonesia': 'IDN', 'Turkey': 'TUR',
            # Add more mappings as needed based on your CSV data
        }
        df['iso_alpha'] = df['Country'].map(country_to_iso)
        # ISO 코드를 찾지 못한 국가에 대한 경고
        if df['iso_alpha'].isnull().any():
            st.warning("Warning: Some countries could not be mapped to ISO codes and may not appear on the map.")
            st.warning("Missing countries: " + ", ".join(df[df['iso_alpha'].isnull()]['Country'].unique().tolist()))

        return df
    except FileNotFoundError:
        st.error("`processed_whr_short.csv` file not found. Please upload the file or check the path.")
        return pd.DataFrame() # Return empty DataFrame
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# 데이터가 비어있으면 앱 실행 중단
if df.empty:
    st.stop()

# 최신 연도 데이터 (만약 Year 컬럼이 있다면)
if 'Year' in df.columns:
    latest_year = df['Year'].max()
    df_latest = df[df['Year'] == latest_year].copy()
else:
    df_latest = df.copy() # Year 컬럼이 없으면 전체 데이터 사용

# --------------------
# 3. 사이드바 - 앱 정보 및 필터
# --------------------
with st.sidebar:
    st.header("Settings")
    st.write("This app compares generosity by country based on World Happiness Report data.")
    st.caption("Data source: processed_whr_short.csv")

    df_display = df.copy() # Filtering initial DataFrame

    if 'Year' in df.columns:
        st.subheader("Select Data Year")
        selected_year = st.slider(
            "Select the year for analysis",
            int(df['Year'].min()),
            int(df['Year'].max()),
            int(df['Year'].max()) # Set latest year as default
        )
        df_display = df[df['Year'] == selected_year].copy()
    else:
        st.caption("No year-specific data. Using all available data.")
        # df_display is already initialized with all data

    if not df_display.empty:
        st.subheader("Generosity Index Range Filter")
        min_generosity, max_generosity = st.slider(
            "Generosity index range",
            float(df_display['Generosity'].min()),
            float(df_display['Generosity'].max()),
            (float(df_display['Generosity'].min()), float(df_display['Generosity'].max()))
        )
        df_display = df_display[(df_display['Generosity'] >= min_generosity) & (df_display['Generosity'] <= max_generosity)]
    else:
        st.warning("No data to filter.")


# --------------------
# 4. 메인 컨텐츠 영역
# --------------------
st.title("🌍 Country Generosity Index Comparison")

# 탭 구현
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard Overview", "Country Details", "Country Comparison", "Data Table"])

with tab1: # Dashboard Overview
    st.header("📊 Dashboard Overview")

    if not df_display.empty:
        col1, col2 = st.columns(2)

        with col1:
            avg_generosity = df_display['Generosity'].mean()
            st.metric(label=f"{'Selected Year' if 'Year' in df.columns else 'Overall'} Average Generosity Index", value=f"{avg_generosity:.3f}")
            st.write("### 🥇 Top 5 Most Generous Countries")
            top_5_generosity = df_display.nlargest(5, 'Generosity')
            st.dataframe(top_5_generosity[['Country', 'Generosity']].reset_index(drop=True), use_container_width=True)

        with col2:
            st.write("### 🥉 Bottom 5 Least Generous Countries")
            bottom_5_generosity = df_display.nsmallest(5, 'Generosity')
            st.dataframe(bottom_5_generosity[['Country', 'Generosity']].reset_index(drop=True), use_container_width=True)

        st.subheader(f"{'Selected Year' if 'Year' in df.columns else 'Overall'} Generosity Distribution by Country")
        fig_hist = px.histogram(df_display, x='Generosity', nbins=20,
                                title='Generosity Index Distribution',
                                labels={'Generosity': 'Generosity Index'})
        st.plotly_chart(fig_hist, use_container_width=True)

        # World Map Visualization ( Choropleth Map )
        st.subheader(f"🗺️ {'Selected Year' if 'Year' in df.columns else 'Overall'} Generosity Index World Map")
        # Filter data with ISO codes for map display
        df_map = df_display.dropna(subset=['iso_alpha'])
        if not df_map.empty:
            fig_map = px.choropleth(df_map,
                                    locations="iso_alpha",
                                    color="Generosity",
                                    hover_name="Country",
                                    color_continuous_scale=px.colors.sequential.Plasma, # Color scale
                                    title='World Map of Generosity Index',
                                    labels={'Generosity': 'Generosity Index'})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No country data to display on the map. Either no ISO codes are mapped or data is filtered out.")


        # Simple Bar Chart for all countries
        st.subheader(f"{'Selected Year' if 'Year' in df.columns else 'Overall'} Generosity Index by Country (Bar Chart)")
        fig_bar_all = px.bar(df_display.sort_values('Generosity', ascending=False), x='Country', y='Generosity',
                             title=f"{'Selected Year' if 'Year' in df.columns else 'Overall'} Generosity Index by Country",
                             labels={'Country': 'Country', 'Generosity': 'Generosity Index'})
        st.plotly_chart(fig_bar_all, use_container_width=True)
    else:
        st.warning("No data to display. Adjust filters or check original data.")


with tab2: # Country Details
    st.header("🔍 Country Details Analysis")
    if not df_display.empty:
        selected_country_detail = st.selectbox(
            "Select a country to view details:",
            options=df_display['Country'].sort_values().unique()
        )

        if selected_country_detail:
            country_data = df_display[df_display['Country'] == selected_country_detail].iloc[0]
            st.subheader(f"Selected Country: {selected_country_detail}")
            col_det1, col_det2 = st.columns(2)
            with col_det1:
                st.metric(label="Generosity Index", value=f"{country_data['Generosity']:.3f}")
            with col_det2:
                # Calculate rank
                df_sorted = df_display.sort_values(by='Generosity', ascending=False).reset_index(drop=True)
                rank = df_sorted[df_sorted['Country'] == selected_country_detail].index[0] + 1
                st.metric(label="Rank among all countries", value=f"{int(rank)}th")

            if 'Year' in df.columns:
                st.subheader(f"{selected_country_detail}'s Generosity Index Trend")
                country_time_series = df[df['Country'] == selected_country_detail].sort_values('Year')
                if not country_time_series.empty:
                    fig_line = px.line(country_time_series, x='Year', y='Generosity',
                                       title=f'{selected_country_detail} Generosity Index Trend',
                                       labels={'Generosity': 'Generosity Index', 'Year': 'Year'})
                    st.plotly_chart(fig_line, use_container_width=True)
                else:
                    st.info("No year-specific data for the selected country.")
            else:
                st.info("No year-specific data available to display generosity index trends.")
    else:
        st.warning("No data to display. Adjust filters or check original data.")

with tab3: # Country Comparison
    st.header("🆚 Country Comparison Analysis")
    if not df_display.empty:
        compare_countries = st.multiselect(
            "Select countries to compare (up to 5 recommended):",
            options=df_display['Country'].sort_values().unique(),
            default=df_display['Country'].head(2).tolist() # Default to 2 countries
        )

        if compare_countries:
            compare_df = df_display[df_display['Country'].isin(compare_countries)].sort_values('Generosity', ascending=False)
            st.subheader("Generosity Index Comparison by Selected Countries")
            fig_compare = px.bar(compare_df, x='Country', y='Generosity',
                                 title='Generosity Index Comparison by Country',
                                 labels={'Country': 'Country', 'Generosity': 'Generosity Index'},
                                 color='Country',
                                 text='Generosity') # Display values
            fig_compare.update_traces(texttemplate='%{text:.3f}', textposition='outside')
            st.plotly_chart(fig_compare, use_container_width=True)

            st.subheader("Detailed Comparison Table for Selected Countries")
            st.dataframe(compare_df[['Country', 'Generosity']].reset_index(drop=True), use_container_width=True)
        else:
            st.info("Please select one or more countries to compare.")
    else:
        st.warning("No data to compare. Adjust filters or check original data.")

with tab4: # Data Table
    st.header("📋 Raw Data Table")
    if not df_display.empty:
        st.write("You can view and sort the filtered raw data.")
        st.dataframe(df_display.sort_values(by='Generosity', ascending=False).reset_index(drop=True), use_container_width=True)

        st.subheader("App Description and Background Information")
        st.markdown("""
        This web app visualizes and compares the 'Generosity' index of each country based on **World Happiness Report** data.

        **What is the Generosity Index?**
        * 'Generosity' is typically measured by the average national response to donating money in the past month.
        * It is one of the important indicators reflecting social responsibility and the tendency to help others.

        **Data Usage:**
        * Data is fetched from the `processed_whr_short.csv` file.
        * Through various visualizations and statistical analyses in each tab, you can understand the level of generosity by country.

        **World Map Visualization Note:**
        * **ISO-ALPHA-3 country codes** are required to display the generosity index by country on the world map.
        * The current code includes manual mapping for some countries. To accurately display all countries, it is recommended to include the corresponding ISO-ALPHA-3 codes in your `processed_whr_short.csv` file or use libraries like `pycountry` for dynamic mapping.
        """)
    else:
        st.warning("No data to display. Adjust filters or check original data.")
