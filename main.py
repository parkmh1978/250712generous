import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt # Although imported, Altair is not explicitly used in chart generation in this specific code.
import io

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
        # Streamlit Cloud에서는 파일을 앱과 같은 디렉토리에 두면 바로 접근 가능합니다.
        df = pd.read_csv('processed_whr.csv')

        # 컬럼명 통일 (실제 파일의 컬럼명에 따라 'Country'와 'Generosity'가 정확한지 확인 필요)
        df.rename(columns={
            'country': 'Country',
            'generosity': 'Generosity',
            'year': 'Year'
        }, inplace=True)

        # 필수 컬럼 확인 및 선택
        required_columns = ['Country', 'Generosity']
        if 'Year' in df.columns:
            required_columns.append('Year')
        else:
            st.warning("경고: 'Year' 컬럼을 찾을 수 없습니다. 연도별 분석 기능이 비활성화됩니다.")

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}. 파일의 컬럼명을 확인해주세요.")
            return pd.DataFrame() # 빈 DataFrame 반환하여 앱 실행 중단

        df = df[required_columns].copy() # SettingWithCopyWarning 방지를 위해 .copy() 사용

        # --- 세계 지도 시각화를 위한 국가 코드 추가 ---
        # 더 포괄적인 매핑을 위해 pycountry 라이브러리 사용을 권장합니다.
        # 여기서는 예시를 위해 일부 국가만 수동 매핑합니다.
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
            'Ireland': 'IRL', 'Luxembourg': 'LUX', 'Iceland': 'ISL',
            'Israel': 'ISR', 'Chile': 'CHL', 'Colombia': 'COL',
            'Thailand': 'THA', 'Vietnam': 'VNM', 'Philippines': 'PHL',
            'Greece': 'GRC', 'Portugal': 'PRT', 'Poland': 'POL',
            'Hungary': 'HUN', 'Czech Republic': 'CZE', 'Slovakia': 'SVK',
            'Romania': 'ROU', 'Bulgaria': 'BGR', 'Croatia': 'HRV',
            'Estonia': 'EST', 'Latvia': 'LVA', 'Lithuania': 'LTU',
            'Slovenia': 'SVN', 'Cyprus': 'CYP', 'Malta': 'MLT',
            'Afghanistan': 'AFG', 'Albania': 'ALB', 'Algeria': 'DZA', 'Angola': 'AGO',
            'Armenia': 'ARM', 'Azerbaijan': 'AZE', 'Bahrain': 'BHR', 'Bangladesh': 'BGD',
            'Belarus': 'BLR', 'Benin': 'BEN', 'Bhutan': 'BTN', 'Bolivia': 'BOL',
            'Bosnia and Herzegovina': 'BIH', 'Botswana': 'BWA', 'Burkina Faso': 'BFA',
            'Burundi': 'BDI', 'Cambodia': 'KHM', 'Cameroon': 'CMR', 'Central African Republic': 'CAF',
            'Chad': 'TCD', 'Comoros': 'COM', 'Congo (Brazzaville)': 'COG', 'Congo (Kinshasa)': 'COD',
            'Costa Rica': 'CRI', 'Cote d\'Ivoire': 'CIV', 'Cuba': 'CUB', 'Djibouti': 'DJI',
            'Dominican Republic': 'DOM', 'Ecuador': 'ECU', 'El Salvador': 'SLV', 'Equatorial Guinea': 'GNQ',
            'Eritrea': 'ERI', 'Ethiopia': 'ETH', 'Fiji': 'FJI', 'Gabon': 'GAB', 'Gambia': 'GMB',
            'Georgia': 'GEO', 'Ghana': 'GHA', 'Guatemala': 'GTM', 'Guinea': 'GIN', 'Guinea-Bissau': 'GNB',
            'Guyana': 'GUY', 'Haiti': 'HTI', 'Honduras': 'HND', 'Hong Kong S.A.R., China': 'HKG',
            'Iran': 'IRN', 'Iraq': 'IRQ', 'Jamaica': 'JAM', 'Jordan': 'JOR', 'Kazakhstan': 'KAZ',
            'Kenya': 'KEN', 'Kosovo': 'XKX', 'Kuwait': 'KWT', 'Kyrgyzstan': 'KGZ', 'Laos': 'LAO',
            'Lebanon': 'LBN', 'Lesotho': 'LSO', 'Liberia': 'LBR', 'Libya': 'LBY', 'Madagascar': 'MDG',
            'Malawi': 'MWI', 'Malaysia': 'MYS', 'Maldives': 'MDV', 'Mali': 'MLI', 'Mauritania': 'MRT',
            'Mauritius': 'MUS', 'Moldova': 'MDA', 'Mongolia': 'MNG', 'Montenegro': 'MNE',
            'Morocco': 'MAR', 'Mozambique': 'MOZ', 'Myanmar': 'MMR', 'Namibia': 'NAM', 'Nepal': 'NPL',
            'Nicaragua': 'NIC', 'Niger': 'NER', 'North Macedonia': 'MKD', 'Oman': 'OMN', 'Pakistan': 'PAK',
            'Palestine': 'PSE', 'Panama': 'PAN', 'Papua New Guinea': 'PNG', 'Paraguay': 'PRY',
            'Peru': 'PER', 'Qatar': 'QAT', 'Rwanda': 'RWA', 'Saudi Arabia': 'SAU', 'Senegal': 'SEN',
            'Serbia': 'SRB', 'Sierra Leone': 'SLE', 'Singapore': 'SGP', 'Somalia': 'SOM',
            'South Sudan': 'SSD', 'Sri Lanka': 'LKA', 'Sudan': 'SDN', 'Suriname': 'SUR',
            'Syria': 'SYR', 'Taiwan Province of China': 'TWN', 'Tanzania': 'TZA', 'Togo': 'TGO',
            'Trinidad and Tobago': 'TTO', 'Tunisia': 'TUN', 'Uganda': 'UGA', 'Ukraine': 'UKR',
            'United Arab Emirates': 'ARE', 'Uruguay': 'URY', 'Uzbekistan': 'UZB', 'Venezuela': 'VEN',
            'Yemen': 'YEM', 'Zambia': 'ZMB', 'Zimbabwe': 'ZWE'
        }
        df['iso_alpha'] = df['Country'].map(country_to_iso)

        # ISO 코드를 찾지 못한 국가에 대한 경고
        unmapped_countries = df[df['iso_alpha'].isnull()]['Country'].unique().tolist()
        if unmapped_countries:
            st.warning(f"경고: 다음 국가들은 ISO 코드를 찾을 수 없어 지도에 표시되지 않을 수 있습니다: {', '.join(unmapped_countries)}")

        return df
    except FileNotFoundError:
        st.error("`processed_whr.csv` 파일을 찾을 수 없습니다. 파일을 업로드하거나 경로를 확인해주세요.")
        return pd.DataFrame() # 빈 DataFrame 반환
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

df = load_data()

# 데이터가 비어있으면 앱 실행 중단
if df.empty:
    st.stop()

# 최신 연도 데이터 (대시보드 개요 탭용)
df_latest_year = pd.DataFrame()
latest_year = None
if 'Year' in df.columns:
    latest_year = df['Year'].max()
    df_latest_year = df[df['Year'] == latest_year].copy()
else:
    st.warning("경고: 'Year' 컬럼이 없어 최신 연도 데이터 필터링이 불가능합니다. 모든 데이터를 사용합니다.")
    df_latest_year = df.copy() # Year 컬럼이 없으면 전체 데이터 사용


# --------------------
# 3. 사이드바 - 앱 정보 및 필터
# --------------------
with st.sidebar:
    st.header("설정")
    st.write("이 앱은 세계 행복 보고서 데이터를 기반으로 국가별 관대함을 비교합니다.")
    st.caption("데이터 출처: processed_whr.csv")

    df_display = df.copy() # 필터링을 위한 초기 DataFrame 복사

    if 'Year' in df.columns:
        st.subheader("데이터 연도 선택")
        selected_year_sidebar = st.slider( # 변수명 변경하여 충돌 방지
            "분석할 연도를 선택하세요:",
            int(df['Year'].min()),
            int(df['Year'].max()),
            int(df['Year'].max()) # 기본값으로 최신 연도 설정
        )
        df_display = df[df['Year'] == selected_year_sidebar].copy()
    else:
        st.caption("연도별 데이터가 없습니다. 모든 가용 데이터를 사용합니다.")

    if not df_display.empty:
        st.subheader("관대함 지수 범위 필터")
        min_generosity, max_generosity = st.slider(
            "관대함 지수 범위:",
            float(df_display['Generosity'].min()),
            float(df_display['Generosity'].max()),
            (float(df_display['Generosity'].min()), float(df_display['Generosity'].max()))
        )
        df_display = df_display[(df_display['Generosity'] >= min_generosity) & (df_display['Generosity'] <= max_generosity)]
    else:
        st.warning("필터링할 데이터가 없습니다.")


# --------------------
# 4. 메인 컨텐츠 영역
# --------------------
st.title("🌍 국가 관대함 지수 비교")

# 탭 구현
tab1, tab2, tab3, tab4 = st.tabs(["대시보드 개요", "국가 세부 정보", "국가 비교", "데이터 테이블"])

with tab1: # Dashboard Overview
    # 대시보드 개요 탭은 항상 최신 연도 데이터를 사용
    st.header(f"📊 대시보드 개요 ({latest_year if latest_year else '전체'}년 데이터)")
    
    current_df_for_tab1 = df_latest_year 

    if not current_df_for_tab1.empty:
        col1, col2 = st.columns(2)

        with col1:
            avg_generosity = current_df_for_tab1['Generosity'].mean()
            st.metric(label=f"{latest_year if latest_year else '전체'}년 평균 관대함 지수", value=f"{avg_generosity:.3f}")
            st.write("### 🥇 관대함 지수 상위 5개국")
            top_5_generosity = current_df_for_tab1.nlargest(5, 'Generosity')
            st.dataframe(top_5_generosity[['Country', 'Generosity']].reset_index(drop=True), use_container_width=True)

        with col2:
            st.write("### 🥉 관대함 지수 하위 5개국")
            bottom_5_generosity = current_df_for_tab1.nsmallest(5, 'Generosity')
            st.dataframe(bottom_5_generosity[['Country', 'Generosity']].reset_index(drop=True), use_container_width=True)

        st.subheader(f"{latest_year if latest_year else '전체'} 국가별 관대함 분포")
        fig_hist = px.histogram(current_df_for_tab1, x='Generosity', nbins=20,
                                title='관대함 지수 분포',
                                labels={'Generosity': '관대함 지수'},
                                color_discrete_sequence=px.colors.qualitative.Pastel) # Improved color
        fig_hist.update_layout(template="plotly_white", title_x=0.5, # Centered title, clean template
                                margin=dict(t=50, b=50, l=50, r=50)) # Add margins
        st.plotly_chart(fig_hist, use_container_width=True)

        # World Map Visualization ( Choropleth Map )
        st.subheader(f"🗺️ {latest_year if latest_year else '전체'} 관대함 지수 세계 지도")
        # 지도 표시를 위해 ISO 코드가 있는 데이터만 필터링
        df_map = current_df_for_tab1.dropna(subset=['iso_alpha']).copy()
        if not df_map.empty:
            fig_map = px.choropleth(df_map,
                                    locations="iso_alpha",
                                    color="Generosity",
                                    hover_name="Country",
                                    color_continuous_scale=px.colors.sequential.Viridis, # More visually appealing scale
                                    title='세계 관대함 지수 지도',
                                    labels={'Generosity': '관대함 지수'})
            fig_map.update_layout(template="plotly_white", title_x=0.5,
                                  margin=dict(t=50, b=50, l=50, r=50))
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("지도에 표시할 국가 데이터가 없습니다. ISO 코드가 매핑되지 않았거나 데이터가 필터링되었습니다.")


        # 모든 국가에 대한 막대 차트
        st.subheader(f"{latest_year if latest_year else '전체'} 국가별 관대함 지수 (막대 차트)")
        fig_bar_all = px.bar(current_df_for_tab1.sort_values('Generosity', ascending=False), x='Country', y='Generosity',
                             title=f"{latest_year if latest_year else '전체'} 국가별 관대함 지수",
                             labels={'Country': '국가', 'Generosity': '관대함 지수'},
                             color_discrete_sequence=px.colors.qualitative.D3) # Another good qualitative scale
        fig_bar_all.update_layout(template="plotly_white", title_x=0.5,
                                  margin=dict(t=50, b=50, l=50, r=50))
        st.plotly_chart(fig_bar_all, use_container_width=True)
    else:
        st.warning("표시할 데이터가 없습니다. 필터를 조정하거나 원본 데이터를 확인하세요.")


with tab2: # Country Details - Modified for multi-country comparison
    st.header("🔍 국가 세부 정보 및 연도별 추세 분석")
    if not df.empty and 'Year' in df.columns: # df_display가 아닌 전체 df를 사용해 연도별 추세 분석
        selected_countries_detail = st.multiselect(
            "세부 정보를 볼 국가를 선택하세요:",
            options=df['Country'].sort_values().unique(), # 전체 데이터셋에서 국가 선택
            default=df['Country'].head(1).tolist() # 기본값으로 1개 국가 설정
        )

        if selected_countries_detail:
            # 선택된 국가들의 전체 연도 데이터 필터링
            countries_time_series_data = df[df['Country'].isin(selected_countries_detail)].sort_values(['Country', 'Year'])

            if not countries_time_series_data.empty:
                st.subheader(f"선택된 국가들의 관대함 지수 추세")
                
                # 라인 차트 (여러 국가 비교)
                fig_line = px.line(countries_time_series_data, x='Year', y='Generosity',
                                   color='Country', # 국가별로 다른 색상 적용
                                   title=f'{", ".join(selected_countries_detail)} 관대함 지수 추세',
                                   labels={'Generosity': '관대함 지수', 'Year': '연도'},
                                   markers=True, # Add markers for clarity
                                   color_discrete_sequence=px.colors.qualitative.Plotly) # Consistent color
                fig_line.update_layout(template="plotly_white", title_x=0.5,
                                       margin=dict(t=50, b=50, l=50, r=50))
                st.plotly_chart(fig_line, use_container_width=True)

                st.subheader(f"선택된 국가들의 최신 ({latest_year if latest_year else '전체'}년) 관대함 지수")
                # 최신 연도 데이터에 대한 테이블 (선택된 국가만)
                current_year_generosity = df_latest_year[df_latest_year['Country'].isin(selected_countries_detail)]
                if not current_year_generosity.empty:
                    st.dataframe(current_year_generosity[['Country', 'Generosity']].sort_values('Generosity', ascending=False).reset_index(drop=True), use_container_width=True)
                else:
                    st.info("선택된 국가에 대한 최신 연도 데이터가 없습니다.")

            else:
                st.info("선택된 국가에 대한 연도별 데이터가 없습니다.")
        else:
            st.info("세부 정보를 볼 국가를 하나 이상 선택해주세요.")
    elif 'Year' not in df.columns:
        st.warning("연도별 데이터가 없어 국가 세부 정보 분석을 할 수 없습니다.")
    else:
        st.warning("표시할 데이터가 없습니다. 필터를 조정하거나 원본 데이터를 확인하세요.")

with tab3: # Country Comparison
    st.header("🆚 국가 비교 분석")
    if not df_display.empty:
        compare_countries = st.multiselect(
            "비교할 국가를 선택하세요 (5개 이하 권장):",
            options=df_display['Country'].sort_values().unique(),
            default=df_display['Country'].head(2).tolist() # 기본값으로 2개 국가 설정
        )

        if compare_countries:
            compare_df = df_display[df_display['Country'].isin(compare_countries)].sort_values('Generosity', ascending=False).copy()
            st.subheader("선택된 국가별 관대함 지수 비교")
            fig_compare = px.bar(compare_df, x='Country', y='Generosity',
                                 title='국가별 관대함 지수 비교',
                                 labels={'Country': '국가', 'Generosity': '관대함 지수'},
                                 color='Country',
                                 text='Generosity',
                                 color_discrete_sequence=px.colors.qualitative.Safe) # Another good qualitative scale
            fig_compare.update_traces(texttemplate='%{text:.3f}', textposition='outside')
            fig_compare.update_layout(template="plotly_white", title_x=0.5,
                                      margin=dict(t=50, b=50, l=50, r=50))
            st.plotly_chart(fig_compare, use_container_width=True)

            st.subheader("선택된 국가에 대한 상세 비교 테이블")
            st.dataframe(compare_df[['Country', 'Generosity']].reset_index(drop=True), use_container_width=True)
        else:
            st.info("비교할 국가를 하나 이상 선택해주세요.")
    else:
        st.warning("비교할 데이터가 없습니다. 필터를 조정하거나 원본 데이터를 확인하세요.")

with tab4: # Data Table
    st.header("📋 원본 데이터 테이블")
    if not df_display.empty:
        st.write("필터링된 원본 데이터를 확인하고 정렬할 수 있습니다.")
        st.dataframe(df_display.sort_values(by='Generosity', ascending=False).reset_index(drop=True), use_container_width=True)

        st.subheader("앱 설명 및 배경 정보")
        st.markdown("""
        이 웹 앱은 **세계 행복 보고서(World Happiness Report)** 데이터를 기반으로 각 국가의 '관대함(Generosity)' 지수를 시각화하고 비교합니다.

        **관대함 지수란 무엇인가요?**
        * '관대함'은 일반적으로 지난 한 달 동안 돈을 기부하는 것에 대한 평균적인 국가 응답으로 측정됩니다.
        * 이는 사회적 책임과 타인을 돕는 경향을 반영하는 중요한 지표 중 하나입니다.

        **데이터 사용:**
        * 데이터는 `processed_whr.csv` 파일에서 가져옵니다.
        * 각 탭의 다양한 시각화 및 통계 분석을 통해 국가별 관대함 수준을 이해할 수 있습니다.

        **세계 지도 시각화 참고:**
        * 세계 지도에 국가별 관대함 지수를 표시하려면 **ISO-ALPHA-3 국가 코드**가 필요합니다.
        * 현재 코드는 일부 국가에 대한 수동 매핑을 포함하고 있습니다. 모든 국가를 정확하게 표시하려면 `processed_whr.csv` 파일에 해당 ISO-ALPHA-3 코드를 포함하거나 `pycountry`와 같은 라이브러리를 사용하여 동적으로 매핑하는 것을 권장합니다.
        """)
    else:
        st.warning("표시할 데이터가 없습니다. 필터를 조정하거나 원본 데이터를 확인하세요.")
