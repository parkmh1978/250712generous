st.header("📈 관대함 지수 요인 분석")
st.markdown("""
   이 섹션에서는 국가별 관대함 지수와 다양한 사회경제적 요인 간의 관계를 탐색합니다.
    최신 연도 데이터를 기반으로 선택된 요인들이 관대함에 미치는 영향을 분석합니다.
    **전체 연도 데이터**를 기반으로 선택된 요인들이 관대함에 미치는 영향을 분석합니다.
   """)

# 분석에 사용할 요인 컬럼 목록 (표시 이름)
@@ -382,8 +382,8 @@ def load_data():
'Confidence in National Government'
]

    # df_latest_year에 실제로 존재하는 요인들만 필터링
    available_factors = [col for col in factor_columns if col in df_latest_year.columns]
    # df에 실제로 존재하는 요인들만 필터링 (df_latest_year 대신 df 사용)
    available_factors = [col for col in factor_columns if col in df.columns]

if not available_factors:
st.warning("분석할 수 있는 요인 컬럼이 데이터에 없습니다. `processed_whr.csv` 파일에 해당 컬럼들이 포함되어 있는지 확인해주세요.")
@@ -395,7 +395,7 @@ def load_data():
)

if selected_factors:
            st.markdown(f"### 선택된 요인과 관대함 지수 상관성 ({latest_year if latest_year else '전체'}년)")
            st.markdown("### 📊 선택된 요인과 관대함 지수 상관성")
st.markdown("""
           * **상관계수 해석:**
               * `+1`에 가까울수록 양의 선형 관계 (요인 값이 높을수록 관대함도 높음)
@@ -404,8 +404,10 @@ def load_data():
           """)

for factor in selected_factors:
                # Make a copy to avoid SettingWithCopyWarning and ensure numeric types
                correlation_data = df_latest_year[['Generosity', factor]].copy()
                st.subheader(f"📈 {factor}와 관대함 지수")
                
                # 전체 데이터 사용 (df_latest_year 대신 df 사용)
                correlation_data = df[['Country', 'Year', 'Generosity', factor]].copy()

# Ensure columns are numeric, coercing errors to NaN
correlation_data['Generosity'] = pd.to_numeric(correlation_data['Generosity'], errors='coerce')
@@ -414,36 +416,58 @@ def load_data():
correlation_data.dropna(inplace=True) # Drop NaNs after coercion

if not correlation_data.empty:
                    # 1. 전체 데이터를 사용한 상관계수 (Pooled Correlation)
                    st.markdown("#### 🌍 전체 데이터 상관계수 (Pooled Correlation)")
# Check if there's enough variance (std dev > a very small number) for OLS trendline and at least 2 data points
                    # 표준 편차가 0에 가까운 경우를 방지하여 OLS 에러를 줄입니다.
if (correlation_data[factor].std() > 1e-9 and 
correlation_data['Generosity'].std() > 1e-9 and 
len(correlation_data) >= 2):

                        correlation = correlation_data['Generosity'].corr(correlation_data[factor])
                        st.metric(label=f"{factor}와 관대함 지수 간 피어슨 상관계수", value=f"{correlation:.3f}")
                        pooled_correlation = correlation_data['Generosity'].corr(correlation_data[factor])
                        st.metric(label=f"전체 데이터 '{factor}'와 관대함 지수 간 피어슨 상관계수", value=f"{pooled_correlation:.3f}")

fig_scatter = px.scatter(correlation_data, x=factor, y='Generosity',
hover_name='Country',
                                                 title=f'{factor} vs. 관대함 지수',
                                                 color='Country', # 국가별 색상 구분
                                                 title=f'전체 데이터: {factor} vs. 관대함 지수',
labels={factor: factor, 'Generosity': '관대함 지수'},
trendline='ols', # 선형 회귀 추세선 추가
color_discrete_sequence=px.colors.qualitative.Plotly)
fig_scatter.update_layout(template="plotly_white", title_x=0.5,
margin=dict(t=50, b=50, l=50, r=50))
st.plotly_chart(fig_scatter, use_container_width=True)
else:
                        st.info(f"'{factor}' 또는 '관대함 지수' 데이터에 충분한 변화가 없거나 데이터 포인트가 부족하여 산점도 및 상관관계를 그릴 수 없습니다. (OLS 추세선 제외)")
                        # Optionally, plot scatter without trendline if data points are > 0 but not enough for OLS
                        st.info(f"전체 데이터에서 '{factor}' 또는 '관대함 지수' 데이터에 충분한 변화가 없거나 데이터 포인트가 부족하여 산점도 및 상관관계를 그릴 수 없습니다. (OLS 추세선 제외)")
if len(correlation_data) > 0:
fig_scatter = px.scatter(correlation_data, x=factor, y='Generosity',
hover_name='Country',
                                                     title=f'{factor} vs. 관대함 지수 (추세선 없음 - 데이터 부족)',
                                                     color='Country',
                                                     title=f'전체 데이터: {factor} vs. 관대함 지수 (추세선 없음 - 데이터 부족)',
labels={factor: factor, 'Generosity': '관대함 지수'},
color_discrete_sequence=px.colors.qualitative.Plotly)
fig_scatter.update_layout(template="plotly_white", title_x=0.5,
margin=dict(t=50, b=50, l=50, r=50))
st.plotly_chart(fig_scatter, use_container_width=True)
                    
                    st.markdown("---")

                    # 2. 국가별 상관계수 평균 (Average Within-Country Correlation)
                    st.markdown("#### 🏘️ 국가 내 상관계수 평균 (Average Within-Country Correlation)")
                    country_correlations = []
                    for country in correlation_data['Country'].unique():
                        country_df = correlation_data[correlation_data['Country'] == country]
                        # 각 국가별로 최소 2개 이상의 데이터 포인트와 분산이 있어야 상관계수 계산 가능
                        if len(country_df) >= 2 and country_df[factor].std() > 1e-9 and country_df['Generosity'].std() > 1e-9:
                            corr = country_df['Generosity'].corr(country_df[factor])
                            country_correlations.append(corr)
                    
                    if country_correlations:
                        avg_within_country_corr = pd.Series(country_correlations).mean()
                        st.metric(label=f"국가 내 '{factor}'와 관대함 지수 간 평균 피어슨 상관계수", value=f"{avg_within_country_corr:.3f}")
                        st.info(f"({len(country_correlations)}개 국가의 상관계수 평균)")
                    else:
                        st.info("각 국가 내에서 상관계수를 계산하기에 충분한 데이터가 없습니다.")

else:
st.info(f"{factor}와 관대함 지수 상관관계를 분석할 데이터가 부족합니다. 해당 요인에 결측치가 많을 수 있습니다.")
st.markdown("---") # 각 요인 분석 섹션 구분
@@ -454,14 +478,12 @@ def load_data():
st.markdown("""
   ### 💡 고급 분석 고려사항: 반복 측정 데이터의 특성

    이 분석은 특정 연도(최신 연도)의 데이터를 기반으로 한 **단순 상관관계**입니다.
    이 분석은 **전체 데이터**를 기반으로 한 **전체 상관관계(Pooled Correlation)**와 **국가 내 상관관계의 평균**을 제공합니다.
   국가별 관대함 지수는 여러 해에 걸쳐 반복 측정된 데이터이므로, 다음과 같은 특성을 고려한 고급 통계 분석이 필요할 수 있습니다.

    * **국가 내 변화 (Within-country variation):** 각 국가의 관대함 지수가 시간이 지남에 따라 어떻게 변하는지.
    * **국가 간 차이 (Between-country variation):** 국가마다 관대함 지수의 평균 수준이 다른 이유.
    * **시간 효과 (Time effects):** 특정 연도에 전반적으로 관대함 지수가 높거나 낮아지는 경향.
    * **전체 상관관계의 한계:** 모든 데이터 포인트를 독립적인 관측치로 간주하여 계산한 상관계수입니다. 이는 국가별 고유한 특성이나 시간 경과에 따른 변화를 충분히 반영하지 못할 수 있습니다. 예를 들어, 특정 국가 내에서 요인과 관대함 지수가 양의 관계를 보여도, 국가 간의 평균 수준 차이 때문에 전체 상관관계는 다르게 나타날 수 있습니다.

    단순 상관관계는 이러한 복합적인 요인들을 모두 설명하지 못하며, 특히 상관관계가 인과관계를 의미하지는 않습니다. 예를 들어, GDP가 관대함에 직접적인 영향을 미칠 수도 있지만, 다른 숨겨진 사회적, 문화적 요인들이 GDP와 관대함 모두에 영향을 미칠 수도 있습니다.
    * **국가 내 상관계수 평균의 의미:** 각 국가 내부에서 시간이 지남에 따라 요인과 관대함 지수가 어떻게 함께 변하는지를 나타내는 경향의 평균입니다. 이는 개별 국가의 변화 패턴을 더 잘 포착할 수 있습니다.

    보다 심층적인 분석을 위해서는 **혼합 효과 모델(Mixed-effects models)** 또는 **패널 데이터 분석(Panel data analysis)**과 같은 통계 기법이 활용될 수 있습니다. 이러한 기법들은 국가별 고유한 특성과 시간 경과에 따른 변화를 동시에 고려하여 더 정확한 관계를 파악하는 데 도움을 줍니다.
    * **고급 통계 분석의 필요성:** 단순 상관관계는 인과관계를 의미하지 않으며, 패널 데이터의 복합적인 구조를 완전히 설명하지 못합니다. 예를 들어, GDP가 관대함에 직접적인 영향을 미칠 수도 있지만, 다른 숨겨진 사회적, 문화적 요인들이 GDP와 관대함 모두에 영향을 미칠 수도 있습니다. 보다 심층적인 분석을 위해서는 **혼합 효과 모델(Mixed-effects models)**, **고정 효과 모델(Fixed-effects models)** 또는 **동적 패널 모델(Dynamic Panel Models)**과 같은 통계 기법이 활용될 수 있습니다. 이러한 기법들은 국가별 고유한 특성과 시간 경과에 따른 변화를 동시에 고려하여 더 정확한 관계를 파악하고, 잠재적인 내생성 문제를 다루는 데 도움을 줍니다.
   """)

