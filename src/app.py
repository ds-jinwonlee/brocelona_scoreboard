

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_data, process_match_results, process_attendance, count_goals, get_scorers_list


# 페이지 설정
st.set_page_config(
    page_title="Brocelona League Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed" # 모바일 친화적
)

# --- 스타일링 (CSS) ---
st.markdown("""
<style>
    /* 시스템 다크모드 무시 - 항상 라이트 테마로 고정 */
    .stApp {
        background-color: #ffffff !important;
        color: #212529 !important;
    }
    
    /* 메인 컨테이너 배경 고정 */
    .main .block-container {
        background-color: #ffffff !important;
    }
    
    /* 전체 body 배경 */
    body {
        background-color: #ffffff !important;
        color: #212529 !important;
    }
    
    /* 헤더 스타일 */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #1a1a1a !important;
    }
    
    /* 일반 텍스트 */
    p, span, div, label {
        color: #212529 !important;
    }
    
    /* 탭 스타일 - 모바일 최적화 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: nowrap;
        background-color: #e9ecef !important;
        border-radius: 4px;
        color: #495057 !important;
        padding: 10px 12px;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0d6efd !important;
        color: white !important;
    }
    
    /* 메트릭 박스 */
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #0d6efd !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #212529 !important;
    }
    
    /* 테이블 스타일 */
    div[data-testid="stDataFrame"] {
        width: 100%;
        background-color: #ffffff !important;
    }
    
    /* 테이블 내 텍스트 가독성 향상 */
    table {
        color: #212529 !important;
        background-color: #ffffff !important;
    }
    
    th {
        background-color: #dee2e6 !important;
        color: #212529 !important;
    }
    
    td {
        background-color: #ffffff !important;
        color: #212529 !important;
    }
    
    /* Expander 스타일 수정 - 모바일 가독성 */
    .streamlit-expanderHeader {
        background-color: #f8f9fa !important;
        color: #212529 !important;
    }
    
    details summary {
        background-color: #f8f9fa !important;
        color: #212529 !important;
    }
    
    details {
        background-color: #ffffff !important;
    }
    
    /* Markdown 텍스트 */
    .stMarkdown {
        color: #212529 !important;
    }
    
    /* Caption 텍스트 */
    .css-1629p8f, [data-testid="stCaptionContainer"] {
        color: #6c757d !important;
    }
    
    /* Sidebar (사용시) */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 메인 타이틀 ---
st.title("⚽ Brocelona League Dashboard")
st.markdown("매주 업데이트되는 브로셀로나 리그의 경기 결과와 승점 현황입니다.")

# --- 데이터 로딩 ---
try:
    df_match, df_att = load_data()
    df_teams, df_history, df_scorers = process_match_results(df_match)
    df_att_processed = process_attendance(df_att)
except Exception as e:
    st.error(f"데이터 로딩 중 오류가 발생했습니다: {e}")
    st.stop()

# --- 탭 구성 ---
tab1, tab2, tab3 = st.tabs(["🏆 종합 순위", "🏃 개인 기록", "📈 트렌드 분석"])

# ==========================================
# 탭 1: 종합 순위
# ==========================================
with tab1:
    st.subheader("종합 순위")
    
    # 순위표 (3팀만 표시) - 한글 컬럼명
    df_teams_display = df_teams.copy()
    df_teams_display = df_teams_display.rename(columns={
        'Team': '팀',
        'Points': '승점',
        'Played': '경기수',
        'W': '승',
        'D': '무',
        'L': '패',
        'GF': '득점',
        'GA': '실점',
        'GD': '득실차'
    })
    
    display_cols = ['팀', '승점', '경기수', '승', '무', '패', '득점', '실점', '득실차']
    
    st.dataframe(
        df_teams_display[display_cols].head(3),
        use_container_width=True,
        height=180
    )
    
    # 팀별 통합 승점 테이블
    st.subheader("Team Stats Comparison")
    st.markdown("### 주차별 및 누적 승점")
    
    # 주차별 팀 승점 계산
    weekly_points = df_history.pivot_table(index='Week', columns='Team', values='PointsGained', aggfunc='sum').fillna(0)
    
    # 누적 승점 계산
    total_points = df_teams.set_index('Team')['Points'].to_dict()
    
    # 통합 테이블 생성
    points_table = pd.DataFrame({
        '비고': ['종합'] + [f'{w}주차' for w in sorted(weekly_points.index, reverse=True)],
        '레드': [total_points.get('레드', 0)] + [weekly_points.loc[w, '레드'] if w in weekly_points.index and '레드' in weekly_points.columns else 0 for w in sorted(weekly_points.index, reverse=True)],
        '블루': [total_points.get('블루', 0)] + [weekly_points.loc[w, '블루'] if w in weekly_points.index and '블루' in weekly_points.columns else 0 for w in sorted(weekly_points.index, reverse=True)],
        '옐로': [total_points.get('옐로', 0)] + [weekly_points.loc[w, '옐로'] if w in weekly_points.index and '옐로' in weekly_points.columns else 0 for w in sorted(weekly_points.index, reverse=True)]
    })
    
    st.dataframe(
        points_table.style.format(precision=0),
        use_container_width=True,
        height=200
    )
    
    st.markdown("### 주차별 및 누적 득점/실점")
    
    # 주차별 득실 계산
    weekly_stats = []
    for idx, row in df_match.iterrows():
        week = row['주차']
        for team in ['레드', '블루', '옐로']:
            scorer_val = row[team]
            goals = count_goals(scorer_val)
            if goals is not None:
                weekly_stats.append({
                    '주차': week,
                    '팀': team,
                    '지표': '득점',
                    '값': goals
                })
    
    # 실점 계산
    for week in df_match['주차'].unique():
        week_data = df_match[df_match['주차'] == week]
        for team in ['레드', '블루', '옐로']:
            conceded = 0
            for _, row in week_data.iterrows():
                my_goals = count_goals(row[team])
                if my_goals is not None:
                    for opp_team in ['레드', '블루', '옐로']:
                        if opp_team != team:
                            opp_goals = count_goals(row[opp_team])
                            if opp_goals is not None:
                                conceded += opp_goals
            weekly_stats.append({
                '주차': week,
                '팀': team,
                '지표': '실점',
                '값': conceded
            })
    
    df_weekly = pd.DataFrame(weekly_stats)
    
    # 주차별 득점/실점 테이블
    df_goals_weekly = df_weekly[df_weekly['지표'] == '득점'].pivot_table(
        index='주차', columns='팀', values='값', aggfunc='sum'
    ).fillna(0)
    
    df_conceded_weekly = df_weekly[df_weekly['지표'] == '실점'].pivot_table(
        index='주차', columns='팀', values='값', aggfunc='sum'
    ).fillna(0)
    
    # 누적 득점/실점
    total_gf = df_teams.set_index('Team')['GF'].to_dict()
    total_ga = df_teams.set_index('Team')['GA'].to_dict()
    total_gd = df_teams.set_index('Team')['GD'].to_dict()
    
    # 각 팀별 테이블 데이터 생성
    weeks_sorted = sorted(df_goals_weekly.index, reverse=True)
    row_labels = ['종합'] + [f'{w}주차' for w in weeks_sorted]
    
    # 레드 팀 데이터
    red_data = []
    for idx, label in enumerate(row_labels):
        if idx == 0:  # 종합
            red_data.append({
                '비고': label,
                '득점': total_gf.get('레드', 0),
                '실점': total_ga.get('레드', 0),
                '득실': total_gd.get('레드', 0)
            })
        else:
            w = weeks_sorted[idx - 1]
            gf = df_goals_weekly.loc[w, '레드'] if w in df_goals_weekly.index and '레드' in df_goals_weekly.columns else 0
            ga = df_conceded_weekly.loc[w, '레드'] if w in df_conceded_weekly.index and '레드' in df_conceded_weekly.columns else 0
            red_data.append({
                '비고': label,
                '득점': gf,
                '실점': ga,
                '득실': gf - ga
            })
    
    # 블루 팀 데이터
    blue_data = []
    for idx, label in enumerate(row_labels):
        if idx == 0:  # 종합
            blue_data.append({
                '비고': label,
                '득점': total_gf.get('블루', 0),
                '실점': total_ga.get('블루', 0),
                '득실': total_gd.get('블루', 0)
            })
        else:
            w = weeks_sorted[idx - 1]
            gf = df_goals_weekly.loc[w, '블루'] if w in df_goals_weekly.index and '블루' in df_goals_weekly.columns else 0
            ga = df_conceded_weekly.loc[w, '블루'] if w in df_conceded_weekly.index and '블루' in df_conceded_weekly.columns else 0
            blue_data.append({
                '비고': label,
                '득점': gf,
                '실점': ga,
                '득실': gf - ga
            })
    
    # 옐로 팀 데이터
    yellow_data = []
    for idx, label in enumerate(row_labels):
        if idx == 0:  # 종합
            yellow_data.append({
                '비고': label,
                '득점': total_gf.get('옐로', 0),
                '실점': total_ga.get('옐로', 0),
                '득실': total_gd.get('옐로', 0)
            })
        else:
            w = weeks_sorted[idx - 1]
            gf = df_goals_weekly.loc[w, '옐로'] if w in df_goals_weekly.index and '옐로' in df_goals_weekly.columns else 0
            ga = df_conceded_weekly.loc[w, '옐로'] if w in df_conceded_weekly.index and '옐로' in df_conceded_weekly.columns else 0
            yellow_data.append({
                '비고': label,
                '득점': gf,
                '실점': ga,
                '득실': gf - ga
            })
    
    # DataFrame 생성
    df_red = pd.DataFrame(red_data)
    df_blue = pd.DataFrame(blue_data)
    df_yellow = pd.DataFrame(yellow_data)
    
    # 3개의 컬럼으로 나란히 배치
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🔴 레드")
        st.dataframe(
            df_red.style.format(precision=0, na_rep='-'),
            use_container_width=True,
            hide_index=True,
            height=220
        )
    
    with col2:
        st.markdown("#### 🔵 블루")
        st.dataframe(
            df_blue.style.format(precision=0, na_rep='-'),
            use_container_width=True,
            hide_index=True,
            height=220
        )
    
    with col3:
        st.markdown("#### 🟡 옐로")
        st.dataframe(
            df_yellow.style.format(precision=0, na_rep='-'),
            use_container_width=True,
            hide_index=True,
            height=220
        )
    
    # 경기 결과 원본 데이터
    st.markdown("---")
    st.markdown("### 📋 경기 결과 상세")
    
    # match_result_sample.tsv를 주차별로 보기 좋게 표시
    df_match_display = df_match.copy()
    df_match_display.columns = ['주차', '라운드', '레드', '블루', '옐로']
    
    # 주차별로 그룹화하여 표시
    for week in sorted(df_match_display['주차'].unique(), reverse=True):
        with st.expander(f"**{week}주차 경기 결과**", expanded=(week == df_match_display['주차'].max())):
            week_data = df_match_display[df_match_display['주차'] == week].copy()
            
            # 각 라운드별 처리하여 승/무/패 표시
            formatted_data = []
            for _, row in week_data.iterrows():
                round_num = int(row['라운드'])
                
                # 각 팀의 득점 계산
                red_goals = count_goals(row['레드'])
                blue_goals = count_goals(row['블루'])
                yellow_goals = count_goals(row['옐로'])
                
                # 득점자 리스트 추출
                red_scorers = get_scorers_list(row['레드']) if red_goals else []
                blue_scorers = get_scorers_list(row['블루']) if blue_goals else []
                yellow_scorers = get_scorers_list(row['옐로']) if yellow_goals else []
                
                # 결과 판정 함수
                def format_result(my_goals, my_scorers, opp_goals_list):
                    if my_goals is None:
                        return '-'
                    max_opp = max([g for g in opp_goals_list if g is not None], default=0)
                    
                    scorers_text = f" ({', '.join(my_scorers)})" if my_scorers else ""
                    
                    if my_goals > max_opp:
                        return f"승{scorers_text}"
                    elif my_goals == max_opp:
                        return f"무{scorers_text}" if my_goals > 0 else "무"
                    else:
                        return f"패{scorers_text}" if my_scorers else "패"
                
                formatted_data.append({
                    '라운드': round_num,
                    '레드': format_result(red_goals, red_scorers, [blue_goals, yellow_goals]),
                    '블루': format_result(blue_goals, blue_scorers, [red_goals, yellow_goals]),
                    '옐로': format_result(yellow_goals, yellow_scorers, [red_goals, blue_goals])
                })
            
            # DataFrame 생성
            formatted_df = pd.DataFrame(formatted_data)
            
            # 주차별 승점 합계 계산
            week_points = df_history[df_history['Week'] == week].groupby('Team')['PointsGained'].sum()
            
            # 승점 합계 row 추가
            points_row = {
                '라운드': '승점 합계',
                '레드': int(week_points.get('레드', 0)),
                '블루': int(week_points.get('블루', 0)),
                '옐로': int(week_points.get('옐로', 0))
            }
            
            formatted_df = pd.concat([formatted_df, pd.DataFrame([points_row])], ignore_index=True)
            
            st.dataframe(
                formatted_df,
                use_container_width=True,
                hide_index=True
            )

# ==========================================
# 탭 2: 개인 기록
# ==========================================
with tab2:
    # 1. 득점 랭킹 (Golden Boot)
    st.subheader("👟 Golden Boot (득점왕)")
    
    # 득점자 정보에 팀 정보 Merge (출석부 기준)
    # 선수 이름 중복이 없다고 가정. 출석부에서 [선수이름, 팀이름] 가져오기
    player_team_map = df_att[['선수이름', '팀이름']].drop_duplicates().set_index('선수이름')['팀이름'].to_dict()
    df_scorers['Team'] = df_scorers['Player'].map(player_team_map)
    
    df_scorers_sorted = df_scorers.sort_values(by='Goals', ascending=False).reset_index(drop=True)
    df_scorers_sorted.index += 1
    
    # Top 10 표시
    st.dataframe(
        df_scorers_sorted[['Player', 'Team', 'Goals']].head(10).style.bar(subset=['Goals'], color='#facc15'),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # 2. 출석왕 (Attendance King) & 가성비 계산을 위한 데이터 준비
    # 선수별 총 출석 횟수
    att_counts = df_att_processed[df_att_processed['IsAttended'] == 1].groupby('선수이름')['WeekNum'].count().reset_index(name='AttendanceCount')
    
    # 3. 데이터 합치기
    df_players_all = pd.merge(att_counts, df_scorers, left_on='선수이름', right_on='Player', how='outer').fillna(0)
    df_players_all['Team'] = df_players_all['선수이름'].map(player_team_map)
    # Player 컬럼 정리
    df_players_all['Player'] = df_players_all.apply(lambda x: x['선수이름'] if pd.notna(x['선수이름']) else x['Player'], axis=1)
    
    # 가성비 스트라이커: Goals / AttendanceCount
    df_players_all['GoalsPerAtt'] = df_players_all['Goals'] / df_players_all['AttendanceCount']
    
    # 승점 요정 계산
    # (내가 출전했을 때 우리 팀 획득 승점 합계) / 출석 횟수
    # 계산이 복잡함 -> History 데이터와 출석 데이터 조인 필요
    # df_history: Week, Team, PointsGained
    # df_att_processed: WeekNum, 선수이름, Team(by map), IsAttended
    
    # 주차별 팀 획득 승점 매핑
    team_points_by_week = df_history.groupby(['Week', 'Team'])['PointsGained'].sum().reset_index()
    
    def calculate_winning_contribution(player_name):
        player_att_rows = df_att_processed[ (df_att_processed['선수이름'] == player_name) & (df_att_processed['IsAttended'] == 1) ]
        if player_att_rows.empty:
            return 0
        
        my_team = player_team_map.get(player_name)
        if not my_team:
            return 0
            
        total_points = 0
        attended_weeks = player_att_rows['WeekNum'].unique()
        
        for w in attended_weeks:
             # 해당 주차, 해당 팀의 승점 찾기
             p = team_points_by_week[ (team_points_by_week['Week'] == w) & (team_points_by_week['Team'] == my_team) ]['PointsGained'].sum()
             total_points += p
             
        return total_points / len(attended_weeks)

    df_players_all['PointsPerAtt'] = df_players_all['Player'].apply(calculate_winning_contribution)
    
    # 컬럼 정리 - 세로 배치로 변경
    st.subheader("📅 출석왕 (Top 10)")
    df_att_king = df_players_all.sort_values(by='AttendanceCount', ascending=False).head(10).reset_index(drop=True)
    df_att_king.index += 1
    st.dataframe(df_att_king[['Player', 'Team', 'AttendanceCount']], use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("⚡ 가성비 스트라이커 (Top 10)")
    st.caption("공식: 득점 / 출석 횟수")
    df_eff_striker = df_players_all[df_players_all['AttendanceCount'] > 0].sort_values(by='GoalsPerAtt', ascending=False).head(10).reset_index(drop=True)
    df_eff_striker.index += 1
    st.dataframe(df_eff_striker[['Player', 'GoalsPerAtt', 'Goals', 'AttendanceCount', 'Team']].style.format({'GoalsPerAtt': '{:.2f}', 'Goals': '{:.0f}'}), use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("🧚 승점 요정 (Top 10)")
    st.caption("공식: (출전한 주차에 우리 팀이 획득한 승점 합계) / 출전 횟수. 즉, 내가 출전하면 팀이 평균 몇 점을 버는지!")
    
    # 승점 요정을 위한 Points 컬럼 추가
    def get_team_total_points(player_name):
        player_att_rows = df_att_processed[ (df_att_processed['선수이름'] == player_name) & (df_att_processed['IsAttended'] == 1) ]
        if player_att_rows.empty:
            return 0
        my_team = player_team_map.get(player_name)
        if not my_team:
            return 0
        total_points = 0
        attended_weeks = player_att_rows['WeekNum'].unique()
        for w in attended_weeks:
            p = team_points_by_week[ (team_points_by_week['Week'] == w) & (team_points_by_week['Team'] == my_team) ]['PointsGained'].sum()
            total_points += p
        return total_points
    
    df_players_all['TotalPointsContribution'] = df_players_all['Player'].apply(get_team_total_points)
    
    df_lucky = df_players_all[df_players_all['AttendanceCount'] > 0].sort_values(by='PointsPerAtt', ascending=False).head(10).reset_index(drop=True)
    df_lucky.index += 1
    st.dataframe(
        df_lucky[['Player', 'PointsPerAtt', 'TotalPointsContribution', 'AttendanceCount', 'Team']].rename(columns={'TotalPointsContribution': 'Points'}).style.format({'PointsPerAtt': '{:.2f}', 'Points': '{:.0f}'}),
        use_container_width=True
    )

# ==========================================
# 탭 3: 트렌드 분석
# ==========================================
with tab3:
    st.subheader("주간 승점 누적 그래프")
    
    # 주차별 누적 승점 계산
    # df_history: Week, Team, PointsGained
    # 모든 주차, 모든 팀에 대한 데이터 확보 필요 (경기가 없어도 승점은 유지되므로)
    
    all_weeks = sorted(df_history['Week'].unique())
    teams_list = ['레드', '블루', '옐로']
    
    cumulative_data = []
    
    for team in teams_list:
        cum_points = 0
        for w in all_weeks:
            # 해당 주차 획득 승점
            week_p = df_history[(df_history['Week'] == w) & (df_history['Team'] == team)]['PointsGained'].sum()
            cum_points += week_p
            cumulative_data.append({'Week': w, 'Team': team, 'CumulativePoints': cum_points})
            
    df_trend = pd.DataFrame(cumulative_data)
    
    # 라인 차트
    fig_trend = px.line(
        df_trend, 
        x='Week', 
        y='CumulativePoints', 
        color='Team',
        markers=True,
        color_discrete_map={'레드': '#ef4444', '블루': '#3b82f6', '옐로': '#eab308'}
    )
    
    fig_trend.update_layout(
        xaxis=dict(tickmode='linear', dtick=1),
        yaxis=dict(showgrid=True, gridcolor='#ddd'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#212529'
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)

