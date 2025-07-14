import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go # plotly.graph_objects 임포트
from plotly.subplots import make_subplots # make_subplots 임포트
import io

# --------------------
# 1. 페이지 설정 (하위 페이지에도 설정 가능)
# --------------------
st.set_page_config(
    page_title="요인 분석",
    page_icon="📈",
    layout="wide"
)

# --------------------
# 2. 데이터 로드 (메인 앱과 동일하게 캐시 사용)
# --------------------
@st.cache_data
def load_data():
    """
    CSV 파일을 로드하고 필요한 컬럼명을 통일합니다.
    세계 지도 시각화를 위해 국가명과 ISO-ALPHA-3 코드 매핑을 시도합니다.
    """
    try:
        df = pd.read_csv('processed_whr.csv')

        expected_raw_columns = [
            'Country', 'year', 'generosity', 'life_ladder', 'log_gdp_per_capita',
            'social_support', 'healthy_life_expectancy_at_birth',
            'freedom_to_make_life_choices', 'perceptions_of_corruption',
            'positive_affect', 'negative_affect', 'confidence_in_national_government'
        ]

        missing_columns_in_csv = [col for col in expected_raw_columns if col not in df.columns]
        if missing_columns_in_csv:
            st.error(f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns_in_csv)}. 파일의 컬럼명을 확인해주세요.")
            return pd.DataFrame()

        df.rename(columns={
            'Country': 'Country',
            'year': 'Year',
            'generosity': 'Generosity',
            'life_ladder': 'Life Ladder',
            'log_gdp_per_capita': 'Log GDP per capita',
            'social_support': 'Social Support',
            'healthy_life_expectancy_at_birth': 'Healthy Life Expectancy at Birth',
            'freedom_to_make_life_choices': 'Freedom to Make Life Choices',
            'perceptions_of_corruption': 'Perceptions of Corruption',
            'positive_affect': 'Positive Affect',
            'negative_affect': 'Negative Affect',
            'confidence_in_national_government': 'Confidence in National Government'
        }, inplace=True)

        display_columns = [
            'Country', 'Year', 'Generosity', 'Life Ladder', 'Log GDP per capita',
            'Social Support', 'Healthy Life Expectancy at Birth',
            'Freedom to Make Life Choices', 'Perceptions of Corruption',
            'Positive Affect', 'Negative Affect', 'Confidence in National Government'
        ]
        df = df[[col for col in display_columns if col in df.columns]].copy()

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

        unmapped_countries = df[df['iso_alpha'].isnull()]['Country'].unique().tolist()
        if unmapped_countries:
            st.warning(f"경고: 다음 국가들은 ISO 코드를 찾을 수 없어 지도에 표시되지 않을 수 있습니다: {', '.join(unmapped_countries)}. 'processed_whr.csv' 파일의 국가명과 코드 매핑을 확인해주세요.")

        return df
    except FileNotFoundError:
        st.error("`processed_whr.csv` 파일을 찾을 수 없습니다. 파일을 업로드하거나 경로를 확인해주세요.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# 데이터 로드
df = load_data()

if df.empty:
    st.stop()

# 최신 연도 계산 (필요한 경우)
latest_year = df['Year'].max() if 'Year' in df.columns else None

# --------------------
# 3. 요인 분석 섹션
# --------------------
st.header("📈 관대함 지수 요인 분석")
st.markdown("""
이 섹션에서는 국가별 관대함 지수와 다양한 사회경제적 요인 간의 관계를 탐색합니다.
**전체 연도 데이터**를 기반으로 선택된 요인들이 관대함에 미치는 영향을 분석합니다.
""")

# 분석에 사용할 요인 컬럼 목록 (표시 이름)
factor_columns = [
    'Generosity', 'Life Ladder', 'Log GDP per capita', 'Social Support',
    'Healthy Life Expectancy at Birth', 'Freedom to Make Life Choices',
    'Perceptions of Corruption', 'Positive Affect', 'Negative Affect',
    'Confidence in National Government'
]

# df에 실제로 존재하는 요인들만 필터링
available_factors = [col for col in factor_columns if col in df.columns]

if not available_factors:
    st.warning("분석할 수 있는 요인 컬럼이 데이터에 없습니다. `processed_whr.csv` 파일에 해당 컬럼들이 포함되어 있는지 확인해주세요.")
else:
    selected_factors = st.multiselect(
        "관대함 지수와의 상관성을 분석할 요인을 선택하세요:",
        options=available_factors,
        default=['Log GDP per capita'] if 'Log GDP per capita' in available_factors else (available_factors[0] if available_factors else [])
    )

    if selected_factors:
        st.markdown("### 📊 선택된 요인과 관대함 지수 상관성")
        st.markdown("""
        * **상관계수 해석:**
            * `+1`에 가까울수록 양의 선형 관계 (요인 값이 높을수록 관대함도 높음)
            * `-1`에 가까울수록 음의 선형 관계 (요인 값이 높을수록 관대함은 낮음)
            * `0`에 가까울수록 선형 관계가 약함
        """)
        
        for factor in selected_factors:
            st.subheader(f"📈 {factor}와 관대함 지수")
            
            correlation_data = df[['Country', 'Year', 'Generosity', factor]].copy()
            
            correlation_data['Generosity'] = pd.to_numeric(correlation_data['Generosity'], errors='coerce')
            correlation_data[factor] = pd.to_numeric(correlation_data[factor], errors='coerce')

            correlation_data.dropna(inplace=True)

            if not correlation_data.empty:
                st.markdown("#### 🌍 전체 데이터 상관계수 (Pooled Correlation)")
                
                # OLS 추세선 관련 에러 처리를 위한 try-except 블록 추가
                try:
                    if (correlation_data[factor].std() > 1e-9 and 
                        correlation_data['Generosity'].std() > 1e-9 and 
                        len(correlation_data) >= 2):
                        
                        pooled_correlation = correlation_data['Generosity'].corr(correlation_data[factor])
                        st.metric(label=f"전체 데이터 '{factor}'와 관대함 지수 간 피어슨 상관계수", value=f"{pooled_correlation:.3f}")

                        fig_scatter = px.scatter(correlation_data, x=factor, y='Generosity',
                                                 hover_name='Country',
                                                 color='Country',
                                                 title=f'전체 데이터: {factor} vs. 관대함 지수',
                                                 labels={factor: factor, 'Generosity': '관대함 지수'},
                                                 trendline='ols', # 선형 회귀 추세선 추가
                                                 color_discrete_sequence=px.colors.qualitative.Plotly)
                        fig_scatter.update_layout(template="plotly_white", title_x=0.5,
                                                  margin=dict(t=50, b=50, l=50, r=50))
                        st.plotly_chart(fig_scatter, use_container_width=True)
                    else:
                        st.info(f"전체 데이터에서 '{factor}' 또는 '관대함 지수' 데이터에 충분한 변화가 없거나 데이터 포인트가 부족하여 산점도 및 상관관계를 그릴 수 없습니다. (OLS 추세선 제외)")
                        if len(correlation_data) > 0:
                            fig_scatter = px.scatter(correlation_data, x=factor, y='Generosity',
                                                     hover_name='Country',
                                                     color='Country',
                                                     title=f'전체 데이터: {factor} vs. 관대함 지수 (추세선 없음 - 데이터 부족)',
                                                     labels={factor: factor, 'Generosity': '관대함 지수'},
                                                     color_discrete_sequence=px.colors.qualitative.Plotly)
                            fig_scatter.update_layout(template="plotly_white", title_x=0.5,
                                                      margin=dict(t=50, b=50, l=50, r=50))
                            st.plotly_chart(fig_scatter, use_container_width=True)
                except ModuleNotFoundError:
                    st.error("오류: 'statsmodels' 라이브러리가 설치되어 있지 않아 OLS 추세선을 그릴 수 없습니다.")
                    st.info("터미널에서 `pip install statsmodels`를 실행하여 설치해 주세요. 추세선 없이 산점도를 표시합니다.")
                    if len(correlation_data) > 0:
                        fig_scatter = px.scatter(correlation_data, x=factor, y='Generosity',
                                                 hover_name='Country',
                                                 color='Country',
                                                 title=f'전체 데이터: {factor} vs. 관대함 지수 (추세선 없음)',
                                                 labels={factor: factor, 'Generosity': '관대함 지수'},
                                                 color_discrete_sequence=px.colors.qualitative.Plotly)
                        fig_scatter.update_layout(template="plotly_white", title_x=0.5,
                                                  margin=dict(t=50, b=50, l=50, r=50))
                        st.plotly_chart(fig_scatter, use_container_width=True)
                except Exception as e:
                    st.error(f"산점도 생성 중 알 수 없는 오류가 발생했습니다: {e}. 추세선 없이 산점도를 표시합니다.")
                    if len(correlation_data) > 0:
                        fig_scatter = px.scatter(correlation_data, x=factor, y='Generosity',
                                                 hover_name='Country',
                                                 color='Country',
                                                 title=f'전체 데이터: {factor} vs. 관대함 지수 (추세선 없음 - 오류 발생)',
                                                 labels={factor: factor, 'Generosity': '관대함 지수'},
                                                 color_discrete_sequence=px.colors.qualitative.Plotly)
                        fig_scatter.update_layout(template="plotly_white", title_x=0.5,
                                                  margin=dict(t=50, b=50, l=50, r=50))
                        st.plotly_chart(fig_scatter, use_container_width=True)
                
                st.markdown("---")

                st.markdown("#### 🏘️ 국가 내 상관계수 평균 (Average Within-Country Correlation)")
                country_correlations = []
                for country in correlation_data['Country'].unique():
                    country_df = correlation_data[correlation_data['Country'] == country]
                    if len(country_df) >= 2 and country_df[factor].std() > 1e-9 and country_df['Generosity'].std() > 1e-9:
                        corr = country_df['Generosity'].corr(country_df[factor])
                        country_correlations.append({'Country': country, 'Correlation': corr})
                
                if country_correlations:
                    country_corr_df = pd.DataFrame(country_correlations)
                    avg_within_country_corr = country_corr_df['Correlation'].mean()
                    st.metric(label=f"국가 내 '{factor}'와 관대함 지수 간 평균 피어슨 상관계수", value=f"{avg_within_country_corr:.3f}")
                    st.info(f"({len(country_correlations)}개 국가의 상관계수 평균)")

                    # 상관관계 상위 3개국, 하위 3개국 추출
                    top_3_countries = country_corr_df.nlargest(3, 'Correlation')['Country'].tolist()
                    bottom_3_countries = country_corr_df.nsmallest(3, 'Correlation')['Country'].tolist()

                    st.markdown("---")
                    st.markdown(f"#### 🎯 '{factor}'와 관대함 지수 상관성 주요 국가")
                    
                    # Plotting specific countries for correlation scatter plot
                    countries_to_plot_corr = set(['전체 평균', 'South Korea']) # Use a set to avoid duplicates
                    countries_to_plot_corr.update(top_3_countries)
                    countries_to_plot_corr.update(bottom_3_countries)
                    
                    # Filter correlation_data for these specific countries
                    # If '전체 평균' is included, it should come from the yearly_overall_average, not correlation_data directly
                    # For this specific scatter plot, we'll just filter the original correlation_data
                    # and add '전체 평균' as a separate trace if needed.
                    
                    # For scatter plot, we need data for each country.
                    # We'll re-filter the original df for specific countries.
                    specific_countries_data = df[df['Country'].isin(list(countries_to_plot_corr))].copy()
                    specific_countries_data['Generosity'] = pd.to_numeric(specific_countries_data['Generosity'], errors='coerce')
                    specific_countries_data[factor] = pd.to_numeric(specific_countries_data[factor], errors='coerce')
                    specific_countries_data.dropna(subset=['Generosity', factor], inplace=True)

                    if not specific_countries_data.empty:
                        fig_specific_scatter = px.scatter(specific_countries_data, x=factor, y='Generosity',
                                                          hover_name='Country',
                                                          color='Country', # Color by country
                                                          title=f"'{factor}' vs. 관대함 지수 (주요 국가)",
                                                          labels={factor: factor, 'Generosity': '관대함 지수'},
                                                          trendline='ols', # OLS 추세선 추가
                                                          color_discrete_sequence=px.colors.qualitative.Bold) # Use a bold palette
                        
                        fig_specific_scatter.update_layout(template="plotly_white", title_x=0.5,
                                                            margin=dict(t=50, b=50, l=50, r=50))
                        st.plotly_chart(fig_specific_scatter, use_container_width=True)
                    else:
                        st.info("선택된 주요 국가에 대한 데이터가 부족하여 산점도를 그릴 수 없습니다.")

                else:
                    st.info("각 국가 내에서 상관계수를 계산하기에 충분한 데이터가 없습니다.")

            else:
                st.info(f"{factor}와 관대함 지수 상관관계를 분석할 데이터가 부족합니다. 해당 요인에 결측치가 많을 수 있습니다.")
            st.markdown("---")
    else:
        st.info("분석할 요인을 하나 이상 선택해주세요.")

# --- 연도별 추이 분석 섹션 ---
st.markdown("---")
st.header("📈 요인 및 관대함 지수 연도별 추이 분석")
st.markdown("""
이 섹션에서는 선택된 요인 또는 관대함 지수의 연도별 변화 추이를 시각화합니다.
전체 국가의 평균 추이와 특정 국가의 추이를 비교할 수 있습니다.
""")

# Prepare data for trend analysis
trend_data_cols = ['Year', 'Country'] + available_factors 
trend_data_numeric = df[trend_data_cols].copy()

for col in available_factors: 
    trend_data_numeric[col] = pd.to_numeric(trend_data_numeric[col], errors='coerce')
trend_data_numeric.dropna(subset=available_factors, inplace=True) 

if not trend_data_numeric.empty:
    # Calculate overall yearly average for Generosity and selected factors
    yearly_overall_average = trend_data_numeric.groupby('Year')[available_factors].mean().reset_index()
    yearly_overall_average['Country'] = '전체 평균'

    # Get South Korea data
    korea_data = trend_data_numeric[trend_data_numeric['Country'] == 'South Korea'].copy()
    
    # Options for country multiselect: all countries + '전체 평균'
    all_plot_countries_options = sorted(trend_data_numeric['Country'].unique().tolist())
    if '전체 평균' not in all_plot_countries_options:
        all_plot_countries_options.insert(0, '전체 평균')
    
    # Define default selected countries for the multiselect
    robust_default_countries_selection = []
    if '전체 평균' in all_plot_countries_options:
        robust_default_countries_selection.append('전체 평균')
    
    if 'South Korea' in all_plot_countries_options:
        robust_default_countries_selection.append('South Korea')
    else:
        st.warning("데이터에 'South Korea'가 없어 해당 국가의 추이를 기본으로 표시할 수 없습니다.")


    selected_countries_for_plot = st.multiselect(
        "추이를 비교할 국가를 선택하세요:",
        options=all_plot_countries_options,
        default=robust_default_countries_selection
    )

    # Filter data based on selected countries
    plot_df_final = pd.DataFrame()
    
    if '전체 평균' in selected_countries_for_plot:
        plot_df_final = pd.concat([plot_df_final, yearly_overall_average])
    
    actual_countries_selected = [c for c in selected_countries_for_plot if c != '전체 평균']
    if actual_countries_selected:
        other_selected_countries_data = trend_data_numeric[trend_data_numeric['Country'].isin(actual_countries_selected)].copy()
        plot_df_final = pd.concat([plot_df_final, other_selected_countries_data])

    if plot_df_final.empty:
        st.info("선택된 국가에 대한 데이터가 없습니다. 국가를 선택해주세요.")
    else:
        plot_df_final['Country'] = plot_df_final['Country'].astype('category')

        # Multiselect for variables to plot on the Y-axis
        default_selected_trend_variables = ['Generosity'] if 'Generosity' in available_factors else []
        final_selected_variables_for_plot = st.multiselect(
            "추이를 볼 변수를 선택하세요:",
            options=available_factors,
            default=default_selected_trend_variables
        )

        if final_selected_variables_for_plot:
            # Create a subplot with secondary y-axis
            fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

            # Define which variables go on which axis
            primary_y_variables = ['Generosity'] if 'Generosity' in final_selected_variables_for_plot else []
            secondary_y_variables = [var for var in final_selected_variables_for_plot if var != 'Generosity']

            # Define a color palette for metrics
            # Using Plotly's qualitative colors for distinctness
            colors = px.colors.qualitative.Bold
            metric_color_map = {metric: colors[i % len(colors)] for i, metric in enumerate(available_factors)}

            # Define dash styles for countries
            dash_styles = ['solid', 'dash', 'dot', 'longdash', 'dashdot', 'longdashdot']
            country_dash_map = {country: dash_styles[i % len(dash_styles)] for i, country in enumerate(plot_df_final['Country'].unique())}

            # Add traces for primary Y-axis (Generosity)
            if primary_y_variables:
                for country in plot_df_final['Country'].unique():
                    country_data = plot_df_final[plot_df_final['Country'] == country]
                    for metric in primary_y_variables:
                        if metric in country_data.columns:
                            fig_trend.add_trace(
                                go.Scatter(
                                    x=country_data['Year'],
                                    y=country_data[metric],
                                    mode='lines+markers',
                                    name=f"{country} ({metric})",
                                    legendgroup=metric, # Group by metric for consistent color
                                    showlegend=True,
                                    line=dict(
                                        color=metric_color_map.get(metric, 'black'), # Color by metric
                                        dash=country_dash_map.get(country, 'solid') # Dash by country
                                    )
                                ),
                                secondary_y=False, # Primary Y-axis
                            )
            
            # Add traces for secondary Y-axis (other selected factors)
            if secondary_y_variables:
                for country in plot_df_final['Country'].unique():
                    country_data = plot_df_final[plot_df_final['Country'] == country]
                    for metric in secondary_y_variables:
                        if metric in country_data.columns:
                            fig_trend.add_trace(
                                go.Scatter(
                                    x=country_data['Year'],
                                    y=country_data[metric],
                                    mode='lines+markers',
                                    name=f"{country} ({metric})",
                                    legendgroup=metric, # Group by metric for consistent color
                                    showlegend=True,
                                    line=dict(
                                        color=metric_color_map.get(metric, 'black'), # Color by metric
                                        dash=country_dash_map.get(country, 'solid') # Dash by country
                                    )
                                ),
                                secondary_y=True, # Secondary Y-axis
                            )

            # Update layout for dual axes
            fig_trend.update_layout(
                title_text=f'선택된 변수들의 연도별 추이 (전체 평균 및 선택 국가)',
                template="plotly_white",
                title_x=0.5,
                margin=dict(t=50, b=50, l=50, r=50),
                hovermode="x unified",
                yaxis=dict(title='관대함 지수 (좌측 축)'),
                yaxis2=dict(title='다른 요인 값 (우측 축)', overlaying='y', side='right')
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("추이를 볼 변수를 하나 이상 선택해주세요. '관대함' 지수는 기본으로 표시됩니다.")
else:
    st.warning("연도별 추이 분석을 위한 데이터가 부족합니다. 원본 데이터를 확인해주세요.")

st.markdown("""
### 💡 고급 분석 고려사항: 반복 측정 데이터의 특성 (추가 설명)

이 앱은 패널 데이터의 특성을 고려하여 **전체 상관관계**와 **국가 내 상관계수 평균**을 제공합니다.
연도별 추이 그래프는 시간 흐름에 따른 변화를 시각적으로 보여주어, 각 국가의 특성과 전체적인 경향을 파악하는 데 도움을 줍니다.

* **전체 평균:** 모든 국가의 해당 연도 데이터를 평균 낸 값으로, 전 세계적인 추세를 나타냅니다.
* **개별 국가:** 특정 국가의 연도별 변화를 보여줍니다.

이러한 시각화는 데이터의 복잡성을 이해하는 데 유용하지만, 더 깊이 있는 통계적 추론을 위해서는 위에서 언급된 **혼합 효과 모델**이나 **패널 데이터 분석**과 같은 고급 방법론을 고려해야 합니다.
""")
