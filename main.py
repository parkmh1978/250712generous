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
            st.warning("경고: 'Year' 컬럼을 찾을 수 없습니다. 연도별 분석 기능은 비활성화됩니다.")

        # 필수 컬럼이 모두 있는지 확인
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"필수 컬럼이 부족합니다: {', '.join(missing_columns)}. 파일의 컬럼명을 확인해주세요.")
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
            st.warning("경고: 일부 국가에 대한 ISO 코드를 찾을 수 없어 지도에 표시되지 않을 수 있습니다.")
            st.warning("누락된 국가: " + ", ".join(df[df['iso_alpha'].isnull()]['Country'].unique().tolist()))

        return df
    except FileNotFoundError:
        st.error("`processed_whr_short.csv` 파일을 찾을 수 없습니다. 파일을 업로드하거나 경로를 확인해주세요.")
        return pd.DataFrame() # 빈 데이터프레임 반환
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
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
    st.header("설정")
    st.write("이 앱은 세계 행복 보고서(World Happiness Report) 데이터를 기반으로 국가별 관대함을 비교합니다.")
    st.caption("데이터 출처: processed_whr_short.csv")

    df_display = df.copy() # 필터링을 위한 초기 데이터프레임

    if 'Year' in df.columns:
        st.subheader("데이터 연도 선택")
        selected_year = st.slider(
            "분석할 연도를 선택하세요",
            int(df['Year'].min()),
            int(df['Year'].max()),
            int(df['Year'].max()) # 기본값으로 최신 연도 설정
        )
        df_display = df[df['Year'] == selected_year].copy()
    else:
        st.caption("연도별 데이터가 없습니다. 전체 데이터를 사용합니다.")
        # df_display는 이미 전체 데이터로 초기화됨

    if not df_display.empty:
        st.subheader("관대함 지수 범위 필터")
        min_generosity, max_generosity = st.slider(
            "관대함 지수 범위",
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
st.title("🌍 국가별 관대함 지수 비교")

# 탭 구현
tab1, tab2, tab3, tab4 = st.tabs(["대시보드 개요", "국가별 상세 분석", "국가 비교 분석", "데이터 테이블"])

with tab1: # 대시보드 개요
    st.header("� 대시보드 개요")

    if not df_display.empty:
        col1, col2 = st.columns(2)

        with col1:
            avg_generosity = df_display['Generosity'].mean()
            st.metric(label=f"{'선택 연도' if 'Year' in df.columns else '전체'} 평균 관대함 지수", value=f"{avg_generosity:.3f}")
            st.write("### 🥇 관대함 상위 5개 국가")
            top_5_generosity = df_display.nlargest(5, 'Generosity')
            st.dataframe(top_5_generosity[['Country', 'Generosity']].reset_index(drop=True), use_container_width=True)

        with col2:
            st.write("### 🥉 관대함 하위 5개 국가")
            bottom_5_generosity = df_display.nsmallest(5, 'Generosity')
            st.dataframe(bottom_5_generosity[['Country', 'Generosity']].reset_index(drop=True), use_container_width=True)

        st.subheader(f"{'선택 연도' if 'Year' in df.columns else '전체'} 국가별 관대함 분포")
        fig_hist = px.histogram(df_display, x='Generosity', nbins=20,
                                title='관대함 지수 분포',
                                labels={'Generosity': '관대함 지수'})
        st.plotly_chart(fig_hist, use_container_width=True)

        # 세계 지도 시각화 ( Choropleth Map )
        st.subheader(f"🗺️ {'선택 연도' if 'Year' in df.columns else '전체'} 관대함 지수 세계 지도")
        # ISO 코드가 있는 데이터만 필터링하여 지도에 표시
        df_map = df_display.dropna(subset=['iso_alpha'])
        if not df_map.empty:
            fig_map = px.choropleth(df_map,
                                    locations="iso_alpha",
                                    color="Generosity",
                                    hover_name="Country",
                                    color_continuous_scale=px.colors.sequential.Plasma, # 색상 스케일
                                    title='세계 국가별 관대함 지수',
                                    labels={'Generosity': '관대함 지수'})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("지도에 표시할 국가 데이터가 없습니다. ISO 코드가 매핑된 국가가 없거나 데이터가 필터링되었습니다.")


        # 간단한 국가별 막대 차트
        st.subheader(f"{'선택 연도' if 'Year' in df.columns else '전체'} 국가별 관대함 지수 (막대 차트)")
        fig_bar_all = px.bar(df_display.sort_values('Generosity', ascending=False), x='Country', y='Generosity',
                             title=f"{'선택 연도' if 'Year' in df.columns else '전체'} 국가별 관대함 지수",
                             labels={'Country': '국가', 'Generosity': '관대함 지수'})
        st.plotly_chart(fig_bar_all, use_container_width=True)
    else:
        st.warning("표시할 데이터가 없습니다. 필터를 조정하거나 원본 데이터를 확인해주세요.")


with tab2: # 국가별 상세 분석
    st.header("🔍 국가별 상세 분석")
    if not df_display.empty:
        selected_country_detail = st.selectbox(
            "상세 정보를 볼 국가를 선택하세요:",
            options=df_display['Country'].sort_values().unique()
        )

        if selected_country_detail:
            country_data = df_display[df_display['Country'] == selected_country_detail].iloc[0]
            st.subheader(f"선택 국가: {selected_country_detail}")
            col_det1, col_det2 = st.columns(2)
            with col_det1:
                st.metric(label="관대함 지수", value=f"{country_data['Generosity']:.3f}")
            with col_det2:
                # 순위 계산
                df_sorted = df_display.sort_values(by='Generosity', ascending=False).reset_index(drop=True)
                rank = df_sorted[df_sorted['Country'] == selected_country_detail].index[0] + 1
                st.metric(label="전체 국가 중 순위", value=f"{int(rank)}위")

            if 'Year' in df.columns:
                st.subheader(f"{selected_country_detail}의 관대함 지수 추이")
                country_time_series = df[df['Country'] == selected_country_detail].sort_values('Year')
                if not country_time_series.empty:
                    fig_line = px.line(country_time_series, x='Year', y='Generosity',
                                       title=f'{selected_country_detail} 관대함 지수 추이',
                                       labels={'Generosity': '관대함 지수', 'Year': '연도'})
                    st.plotly_chart(fig_line, use_container_width=True)
                else:
                    st.info("선택된 국가의 연도별 데이터가 없습니다.")
            else:
                st.info("연도별 데이터가 없어 관대함 지수 추이를 표시할 수 없습니다.")
    else:
        st.warning("표시할 데이터가 없습니다. 필터를 조정하거나 원본 데이터를 확인해주세요.")

with tab3: # 국가 비교 분석
    st.header("🆚 국가 비교 분석")
    if not df_display.empty:
        compare_countries = st.multiselect(
            "비교할 국가들을 선택하세요 (최대 5개 권장):",
            options=df_display['Country'].sort_values().unique(),
            default=df_display['Country'].head(2).tolist() # 기본값으로 2개 국가 선택
        )

        if compare_countries:
            compare_df = df_display[df_display['Country'].isin(compare_countries)].sort_values('Generosity', ascending=False)
            st.subheader("선택 국가별 관대함 지수 비교")
            fig_compare = px.bar(compare_df, x='Country', y='Generosity',
                                 title='국가별 관대함 지수 비교',
                                 labels={'Country': '국가', 'Generosity': '관대함 지수'},
                                 color='Country',
                                 text='Generosity') # 값 표시
            fig_compare.update_traces(texttemplate='%{text:.3f}', textposition='outside')
            st.plotly_chart(fig_compare, use_container_width=True)

            st.subheader("선택 국가 상세 비교 테이블")
            st.dataframe(compare_df[['Country', 'Generosity']].reset_index(drop=True), use_container_width=True)
        else:
            st.info("비교할 국가를 하나 이상 선택해주세요.")
    else:
        st.warning("비교할 데이터가 없습니다. 필터를 조정하거나 원본 데이터를 확인해주세요.")

with tab4: # 데이터 테이블
    st.header("📋 원시 데이터 테이블")
    if not df_display.empty:
        st.write("필터링된 원시 데이터를 확인하고 정렬할 수 있습니다.")
        st.dataframe(df_display.sort_values(by='Generosity', ascending=False).reset_index(drop=True), use_container_width=True)

        st.subheader("앱 설명 및 배경 정보")
        st.markdown("""
        이 웹 앱은 **세계 행복 보고서(World Happiness Report)** 데이터를 기반으로 각 국가의 '관대함(Generosity)' 지수를 시각화하고 비교 분석합니다.

        **관대함 지수란?**
        * '관대함'은 보통 시간에 따라 기부하는 것에 대한 국가의 평균 응답으로 측정됩니다.
        * 이는 사회적 책임감과 다른 사람들을 돕는 경향을 나타내는 중요한 지표 중 하나입니다.

        **데이터 사용:**
        * `processed_whr_short.csv` 파일에서 데이터를 가져옵니다.
        * 각 탭에서 다양한 시각화와 통계 분석을 통해 국가별 관대함 수준을 파악할 수 있습니다.

        **세계 지도 시각화 참고:**
        * 세계 지도에 국가별 관대함 지수를 표시하기 위해 **ISO-ALPHA-3 국가 코드**가 필요합니다.
        * 현재 코드에는 일부 국가에 대한 수동 매핑이 포함되어 있습니다. 모든 국가를 정확히 표시하려면 `processed_whr_short.csv` 파일에 해당 국가의 ISO-ALPHA-3 코드를 포함하거나, `pycountry`와 같은 라이브러리를 사용하여 동적으로 매핑하는 것이 좋습니다.
        """)
    else:
        st.warning("표시할 데이터가 없습니다. 필터를 조정하거나 원본 데이터를 확인해주세요.")
�

