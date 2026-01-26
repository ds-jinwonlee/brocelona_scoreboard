
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_data, process_match_results, process_attendance, count_goals, get_scorers_list


# 헬퍼 함수: DataFrame을 중앙 정렬된 HTML 테이블로 변환
def df_to_html_table(df, center_align=True, match_result=False):
    """
    DataFrame을 HTML 테이블로 변환
    
    Args:
        df: pandas DataFrame
        center_align: True면 모든 셀 중앙 정렬, False면 왼쪽 정렬
        match_result: True면 경기 결과 테이블 (헤더만 중앙, 값은 왼쪽)
    """
    # 스타일 설정
    if match_result:
        # 경기 결과: 헤더는 중앙, 값은 왼쪽
        cell_style = 'text-align: left; padding: 8px 12px;'
        header_style = 'text-align: center; padding: 8px 12px; font-weight: 700; background-color: #dee2e6;'
    elif center_align:
        # 일반 테이블: 모두 중앙
        cell_style = 'text-align: center; padding: 8px 12px;'
        header_style = 'text-align: center; padding: 8px 12px; font-weight: 700; background-color: #dee2e6;'
    else:
        # 왼쪽 정렬
        cell_style = 'text-align: left; padding: 8px 12px;'
        header_style = 'text-align: left; padding: 8px 12px; font-weight: 700; background-color: #dee2e6;'
    
    # HTML 테이블 생성
    html = '<table style="width: 100%; border-collapse: collapse; color: #212529;">'
    
    # 헤더
    html += '<thead><tr>'
    if df.index.name or not all(isinstance(i, int) for i in df.index):
        html += f'<th style="{header_style}">{df.index.name if df.index.name else ""}</th>'
    for col in df.columns:
        html += f'<th style="{header_style}">{col}</th>'
    html += '</tr></thead>'
    
    # 데이터
    html += '<tbody>'
    for idx, row in df.iterrows():
        html += '<tr>'
        if df.index.name or not all(isinstance(i, int) for i in df.index):
            html += f'<td style="{header_style}">{idx}</td>'
        for val in row:
            html += f'<td style="{cell_style}">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    
    return html


# 페이지 설정
st.set_page_config(
    page_title="26 Brocelona Iron League",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    
    /* 테이블 내 텍스트 가독성 향상 및 가운데 정렬 */
    table {
        color: #212529 !important;
        background-color: #ffffff !important;
        width: auto !important;
    }
    
    /* 테이블 헤더 - 굵게, 가운데 정렬 */
    th {
        background-color: #dee2e6 !important;
        color: #212529 !important;
        font-weight: 700 !important;
        text-align: center !important;
        padding: 8px 12px !important;
        white-space: nowrap !important;
    }
    
    /* 테이블 데이터 셀 - 가운데 정렬 */
    td {
        background-color: #ffffff !important;
        color: #212529 !important;
        text-align: center !important;
        padding: 8px 12px !important;
    }
    
    /* 인덱스 컬럼 스타일 */
    .row_heading {
        font-weight: 700 !important;
        text-align: center !important;
    }
    
    /* 컬럼 너비 자동 조정 */
    table {
        table-layout: auto !important;
    }
    
    th, td {
        width: auto !important;
        max-width: fit-content !important;
    }
    
    /* Expander 내부 테이블 - 경기 결과용 (값은 왼쪽 정렬) */
    details table td {
        text-align: left !important;
    }
    
    details table th {
        text-align: center !important;
        font-weight: 700 !important;
    }
    
    /* Expander 스타일 수정 - 모바일 가독성 */
    .streamlit-expanderHeader {
        background-color: #f8f9fa !important;
        color: #212529 !important;
    }
    
    details summary {
        background-color: #f8f9fa !important;
        color: #212529 !important;
        font-weight: 700 !important;
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
st.title("⚽ 26 Brocelona Iron League")
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
all_teams_raw = df_teams['Team'].tolist()

# 팀 이름 변환 함수 (스타크(블루) -> 🔵 스타크)
def format_team_name(name):
    if '레드' in name: return '🔴 타르가르옌'
    if '블루' in name: return '🔵 스타크'
    if '옐로' in name: return '🟡 라니스터'
    return name

# 실제 팀별 색상 딕셔너리 생성
team_colors = {}
for t in all_teams_raw:
    if '레드' in t: team_colors[t] = '#ef4444'
    elif '블루' in t: team_colors[t] = '#3b82f6'
    elif '옐로' in t: team_colors[t] = '#eab308'
    else: team_colors[t] = '#6c757d'

# 표시용 팀 이름 매핑
display_team_map = {t: format_team_name(t) for t in all_teams_raw}

tab1, tab2, tab3 = st.tabs(["🏆 종합 순위", "🏃 개인 기록", "📈 트렌드 분석"])

# ==========================================
# 탭 1: 종합 순위
# ==========================================
with tab1:
    st.subheader("종합 순위")
    
    # 순위표 표시
    df_teams_display = df_teams.copy()
    df_teams_display['Team'] = df_teams_display['Team'].map(display_team_map)
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
    st.markdown(df_to_html_table(df_teams_display[display_cols].reset_index(drop=True)), unsafe_allow_html=True)
    
    # 팀별 통합 승점 테이블
    st.subheader("Team Stats Comparison")
    st.markdown("### 주차별 및 누적 승점")
    
    # 주차별 팀 승점 계산 (데이터 타입 통일을 위해 정수 변환)
    df_history['Week'] = df_history['Week'].astype(int)
    weekly_points = df_history.pivot_table(index='Week', columns='Team', values='PointsGained', aggfunc='sum').fillna(0)
    
    # 누적 승점 계산
    total_points = df_teams.set_index('Team')['Points'].to_dict()
    
    # 통합 테이블 생성
    points_dict = {'비고': ['종합'] + [f'{w}주차' for w in sorted(weekly_points.index, reverse=True)]}
    for team in all_teams_raw:
        display_name = display_team_map.get(team, team)
        points_dict[display_name] = [total_points.get(team, 0)] + [
            int(weekly_points.loc[w, team]) if w in weekly_points.index and team in weekly_points.columns else 0 
            for w in sorted(weekly_points.index, reverse=True)
        ]
    
    points_table = pd.DataFrame(points_dict)
    
    # HTML 테이블로 렌더링
    points_table_display = points_table.set_index('비고')
    st.markdown(df_to_html_table(points_table_display), unsafe_allow_html=True)
    
    st.markdown("### 주차별 및 누적 득점/실점")
    
    # 주차별 득실 계산 (모든 숫자를 정수형으로 관리)
    df_match['주차'] = df_match['주차'].astype(int)
    weekly_stats = []
    for idx, row in df_match.iterrows():
        week = row['주차']
        for team in all_teams_raw:
            if team in df_match.columns:
                scorer_val = row[team]
                goals = count_goals(scorer_val)
                if goals is not None:
                    weekly_stats.append({
                        '주차': week,
                        '팀': team,
                        '지표': '득점',
                        '값': int(goals)
                    })
    
    # 실점 계산
    for week in df_match['주차'].unique():
        week_data = df_match[df_match['주차'] == week]
        for team in all_teams_raw:
            conceded = 0
            for _, row in week_data.iterrows():
                if team in row:
                    my_goals = count_goals(row[team])
                    if my_goals is not None:
                        for opp_team in all_teams_raw:
                            if opp_team != team and opp_team in row:
                                opp_goals = count_goals(row[opp_team])
                                if opp_goals is not None:
                                    conceded += int(opp_goals)
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
    
    # 동적으로 팀별 컬럼 생성 (표 제목 형식 통일)
    cols = st.columns(len(all_teams_raw))
    
    for i, team in enumerate(all_teams_raw):
        display_name = display_team_map.get(team, team)
        team_data = []
        for idx, label in enumerate(row_labels):
            if idx == 0:  # 종합
                team_data.append({
                    '비고': label,
                    '득점': int(total_gf.get(team, 0)),
                    '실점': int(total_ga.get(team, 0)),
                    '득실': int(total_gd.get(team, 0))
                })
            else:
                w = weeks_sorted[idx - 1]
                gf = int(df_goals_weekly.loc[w, team]) if w in df_goals_weekly.index and team in df_goals_weekly.columns else 0
                ga = int(df_conceded_weekly.loc[w, team]) if w in df_conceded_weekly.index and team in df_conceded_weekly.columns else 0
                team_data.append({
                    '비고': label,
                    '득점': gf,
                    '실점': ga,
                    '득실': gf - ga
                })
        
        df_team_display = pd.DataFrame(team_data)
        with cols[i]:
            st.markdown(f"#### {display_name}")
            st.markdown(df_to_html_table(df_team_display.set_index('비고')), unsafe_allow_html=True)
    
    # 경기 결과 원본 데이터
    st.markdown("---")
    st.markdown("### 📋 경기 결과 상세")
    
    # 경기 결과 원본 데이터 표시
    df_match_display = df_match.copy()
    
    # 주차별로 그룹화하여 표시
    for week in sorted(df_match_display['주차'].unique(), reverse=True):
        with st.expander(f"**{week}주차 경기 결과**", expanded=(week == df_match_display['주차'].max())):
            week_data = df_match_display[df_match_display['주차'] == week].copy()
            
            # 각 라운드별 처리하여 승/무/패 표시
            formatted_data = []
            for _, row in week_data.iterrows():
                round_num = int(row['라운드'])
                
                # 각 팀의 결과 정보 생성
                res_row = {'라운드': round_num}
                
                # 모든 팀의 점수 미리 계산
                team_scores = {}
                for team in all_teams_raw:
                    if team in row:
                        team_scores[team] = count_goals(row[team])
                
                for team in all_teams_raw:
                    display_name = display_team_map.get(team, team)
                    if team in row:
                        my_goals = team_scores[team]
                        if my_goals is None:
                            res_row[display_name] = '-'
                            continue
                            
                        my_scorers = get_scorers_list(row[team])
                        opp_scores = [v for k, v in team_scores.items() if k != team and v is not None]
                        max_opp = max(opp_scores) if opp_scores else 0
                        
                        scorers_text = f" ({', '.join(my_scorers)})" if my_scorers else ""
                        
                        if my_goals > max_opp:
                            res_row[display_name] = f"승{scorers_text}"
                        elif my_goals == max_opp:
                            res_row[display_name] = f"무{scorers_text}" if my_goals > 0 else "무"
                        else:
                            res_row[display_name] = f"패{scorers_text}" if my_scorers else "패"
                    else:
                        res_row[display_name] = '-'
                
                formatted_data.append(res_row)
            
            # DataFrame 생성
            formatted_df = pd.DataFrame(formatted_data)
            
            # 주차별 승점 합계 계산
            week_points = df_history[df_history['Week'] == week].groupby('Team')['PointsGained'].sum()
            
            # 승점 합계 row 추가
            points_row = {'라운드': '승점 합계'}
            for team in all_teams_raw:
                display_name = display_team_map.get(team, team)
                points_row[display_name] = int(week_points.get(team, 0))
            
            formatted_df = pd.concat([formatted_df, pd.DataFrame([points_row])], ignore_index=True)
            
            # 경기 결과 테이블 - 헤더는 중앙, 값은 왼쪽 정렬
            st.markdown(df_to_html_table(formatted_df.set_index('라운드'), match_result=True), unsafe_allow_html=True)

# ==========================================
# 탭 2: 개인 기록
# ==========================================
with tab2:
    # 1. 득점 랭킹 (Golden Boot)
    st.subheader("👟 Golden Boot (득점왕)")
    
    # 득점자 정보에 팀 정보 Merge (출석부 기준)
    player_team_map = df_att[['선수이름', '팀이름']].drop_duplicates().set_index('선수이름')['팀이름'].to_dict()
    df_scorers['Team'] = df_scorers['Player'].map(player_team_map)
    
    df_scorers_sorted = df_scorers.sort_values(by='Goals', ascending=False).reset_index(drop=True)
    df_scorers_sorted.index += 1
    
    # Top 10 표시
    df_scorers_display = df_scorers_sorted[['Player', 'Team', 'Goals']].head(10).copy()
    df_scorers_display['Team'] = df_scorers_display['Team'].map(display_team_map)
    st.markdown(df_to_html_table(df_scorers_display), unsafe_allow_html=True)
    
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
             # 해당 주차, 해당 팀의 승점 찾기 (타입 일치 확인)
             p = team_points_by_week[ (team_points_by_week['Week'] == int(w)) & (team_points_by_week['Team'] == my_team) ]['PointsGained'].sum()
             total_points += p
             
        return total_points / len(attended_weeks)

    df_players_all['PointsPerAtt'] = df_players_all['Player'].apply(calculate_winning_contribution)
    
    # 컬럼 정리 - 세로 배치로 변경
    st.subheader("📅 출석왕 (Top 10)")
    df_att_king = df_players_all.sort_values(by='AttendanceCount', ascending=False).head(10).reset_index(drop=True)
    df_att_king.index += 1
    # 표시용 데이터
    df_att_king_display = df_att_king[['Player', 'Team', 'AttendanceCount']].copy()
    df_att_king_display['Team'] = df_att_king_display['Team'].map(display_team_map)
    df_att_king_display['AttendanceCount'] = df_att_king_display['AttendanceCount'].astype(int)
    st.markdown(df_to_html_table(df_att_king_display), unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("⚡ 가성비 스트라이커 (Top 10)")
    st.caption("공식: 득점 / 출석 횟수")
    df_eff_striker = df_players_all[df_players_all['AttendanceCount'] > 0].sort_values(by='GoalsPerAtt', ascending=False).head(10).reset_index(drop=True)
    df_eff_striker.index += 1
    # 표시용 데이터
    df_eff_display = df_eff_striker[['Player', 'GoalsPerAtt', 'Goals', 'AttendanceCount', 'Team']].copy()
    df_eff_display['Team'] = df_eff_display['Team'].map(display_team_map)
    df_eff_display['GoalsPerAtt'] = df_eff_display['GoalsPerAtt'].apply(lambda x: f'{x:.2f}')
    df_eff_display['Goals'] = df_eff_display['Goals'].astype(int)
    df_eff_display['AttendanceCount'] = df_eff_display['AttendanceCount'].astype(int)
    st.markdown(df_to_html_table(df_eff_display), unsafe_allow_html=True)
    
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
            p = team_points_by_week[ (team_points_by_week['Week'] == int(w)) & (team_points_by_week['Team'] == my_team) ]['PointsGained'].sum()
            total_points += p
        return total_points
    
    df_players_all['TotalPointsContribution'] = df_players_all['Player'].apply(get_team_total_points)
    
    df_lucky = df_players_all[df_players_all['AttendanceCount'] > 0].sort_values(by='PointsPerAtt', ascending=False).head(10).reset_index(drop=True)
    df_lucky.index += 1
    # HTML 테이블로 변경
    df_lucky_display = df_lucky[['Player', 'PointsPerAtt', 'TotalPointsContribution', 'AttendanceCount', 'Team']].rename(columns={'TotalPointsContribution': 'TotalPoints'}).copy()
    df_lucky_display['Team'] = df_lucky_display['Team'].map(display_team_map)
    df_lucky_display['PointsPerAtt'] = df_lucky_display['PointsPerAtt'].apply(lambda x: f'{x:.2f}')
    df_lucky_display['TotalPoints'] = df_lucky_display['TotalPoints'].astype(int)
    df_lucky_display['AttendanceCount'] = df_lucky_display['AttendanceCount'].astype(int)
    st.markdown(df_to_html_table(df_lucky_display), unsafe_allow_html=True)

# ==========================================
# 탭 3: 트렌드 분석
# ==========================================
with tab3:
    st.subheader("📊 주차별 추이 분석")
    
    all_weeks = sorted(df_history['Week'].unique())
    teams_list = all_teams
    
    # ========== 1. 승점 복합 그래프 ==========
    st.markdown("### 🏆 승점 추이 (주차별 + 누적)")
    
    # 주차별 승점 데이터 준비
    weekly_points_data = []
    cumulative_points_data = []
    
    for team in teams_list:
        cum_points = 0
        for w in all_weeks:
            week_p = df_history[(df_history['Week'] == w) & (df_history['Team'] == team)]['PointsGained'].sum()
            cum_points += week_p
            weekly_points_data.append({'Week': w, 'Team': team, 'Points': week_p})
            cumulative_points_data.append({'Week': w, 'Team': team, 'CumulativePoints': cum_points})
    
    df_weekly_points = pd.DataFrame(weekly_points_data)
    df_cumulative_points = pd.DataFrame(cumulative_points_data)
    
    # 이중 Y축 그래프 생성
    from plotly.subplots import make_subplots
    
    fig_points = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 막대 그래프 (주차별 승점)
    for team in teams_list:
        team_data = df_weekly_points[df_weekly_points['Team'] == team]
        fig_points.add_trace(
            go.Bar(
                x=team_data['Week'],
                y=team_data['Points'],
                name=f'{team} (주차별)',
                marker_color=team_colors[team],
                opacity=0.6,
                width=0.25,
                legendgroup=team
            ),
            secondary_y=False
        )
    
    # 선 그래프 (누적 승점)
    for team in teams_list:
        team_data = df_cumulative_points[df_cumulative_points['Team'] == team]
        fig_points.add_trace(
            go.Scatter(
                x=team_data['Week'],
                y=team_data['CumulativePoints'],
                name=f'{team} (누적)',
                line=dict(color=team_colors[team], width=3),
                mode='lines+markers',
                legendgroup=team
            ),
            secondary_y=True
        )
    
    fig_points.update_xaxes(title_text="주차", tickmode='linear', dtick=1)
    fig_points.update_yaxes(title_text="주차별 승점", secondary_y=False)
    fig_points.update_yaxes(title_text="누적 승점", secondary_y=True)
    
    fig_points.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#212529',
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_points, use_container_width=True)
    
    # ========== 2. 득점 복합 그래프 ==========
    st.markdown("### ⚽ 득점 추이 (주차별 + 누적)")
    
    # 주차별 득점 계산
    weekly_goals_data = []
    cumulative_goals_data = []
    
    for team in teams_list:
        cum_goals = 0
        for w in all_weeks:
            week_data = df_match[df_match['주차'] == w]
            week_goals = 0
            for _, row in week_data.iterrows():
                goals = count_goals(row[team])
                if goals is not None:
                    week_goals += goals
            
            cum_goals += week_goals
            weekly_goals_data.append({'Week': w, 'Team': team, 'Goals': week_goals})
            cumulative_goals_data.append({'Week': w, 'Team': team, 'CumulativeGoals': cum_goals})
    
    df_weekly_goals = pd.DataFrame(weekly_goals_data)
    df_cumulative_goals = pd.DataFrame(cumulative_goals_data)
    
    fig_goals = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 막대 그래프 (주차별 득점)
    for team in teams_list:
        team_data = df_weekly_goals[df_weekly_goals['Team'] == team]
        fig_goals.add_trace(
            go.Bar(
                x=team_data['Week'],
                y=team_data['Goals'],
                name=f'{team} (주차별)',
                marker_color=team_colors[team],
                opacity=0.6,
                width=0.25,
                legendgroup=team
            ),
            secondary_y=False
        )
    
    # 선 그래프 (누적 득점)
    for team in teams_list:
        team_data = df_cumulative_goals[df_cumulative_goals['Team'] == team]
        fig_goals.add_trace(
            go.Scatter(
                x=team_data['Week'],
                y=team_data['CumulativeGoals'],
                name=f'{team} (누적)',
                line=dict(color=team_colors[team], width=3),
                mode='lines+markers',
                legendgroup=team
            ),
            secondary_y=True
        )
    
    fig_goals.update_xaxes(title_text="주차", tickmode='linear', dtick=1)
    fig_goals.update_yaxes(title_text="주차별 득점", secondary_y=False)
    fig_goals.update_yaxes(title_text="누적 득점", secondary_y=True)
    
    fig_goals.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#212529',
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_goals, use_container_width=True)
    
    # ========== 3. 실점 복합 그래프 ==========
    st.markdown("### 🛡️ 실점 추이 (주차별 + 누적)")
    
    # 주차별 실점 계산
    weekly_conceded_data = []
    cumulative_conceded_data = []
    
    for team in teams_list:
        cum_conceded = 0
        for w in all_weeks:
            week_data = df_match[df_match['주차'] == w]
            week_conceded = 0
            for _, row in week_data.iterrows():
                my_goals = count_goals(row[team])
                if my_goals is not None:
                    for opp_team in teams_list:
                        if opp_team != team:
                            opp_goals = count_goals(row[opp_team])
                            if opp_goals is not None:
                                week_conceded += opp_goals
            
            cum_conceded += week_conceded
            weekly_conceded_data.append({'Week': w, 'Team': team, 'Conceded': week_conceded})
            cumulative_conceded_data.append({'Week': w, 'Team': team, 'CumulativeConceded': cum_conceded})
    
    df_weekly_conceded = pd.DataFrame(weekly_conceded_data)
    df_cumulative_conceded = pd.DataFrame(cumulative_conceded_data)
    
    fig_conceded = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 막대 그래프 (주차별 실점)
    for team in teams_list:
        team_data = df_weekly_conceded[df_weekly_conceded['Team'] == team]
        fig_conceded.add_trace(
            go.Bar(
                x=team_data['Week'],
                y=team_data['Conceded'],
                name=f'{team} (주차별)',
                marker_color=team_colors[team],
                opacity=0.6,
                width=0.25,
                legendgroup=team
            ),
            secondary_y=False
        )
    
    # 선 그래프 (누적 실점)
    for team in teams_list:
        team_data = df_cumulative_conceded[df_cumulative_conceded['Team'] == team]
        fig_conceded.add_trace(
            go.Scatter(
                x=team_data['Week'],
                y=team_data['CumulativeConceded'],
                name=f'{team} (누적)',
                line=dict(color=team_colors[team], width=3),
                mode='lines+markers',
                legendgroup=team
            ),
            secondary_y=True
        )
    
    fig_conceded.update_xaxes(title_text="주차", tickmode='linear', dtick=1)
    fig_conceded.update_yaxes(title_text="주차별 실점", secondary_y=False)
    fig_conceded.update_yaxes(title_text="누적 실점", secondary_y=True)
    
    fig_conceded.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#212529',
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_conceded, use_container_width=True)
    
    # ========== 4. 득실차 복합 그래프 ==========
    st.markdown("### 📈 득실차 추이 (주차별 + 누적)")
    
    # 주차별 득실차 계산
    weekly_gd_data = []
    cumulative_gd_data = []
    
    for team in teams_list:
        cum_gd = 0
        for w in all_weeks:
            # 해당 주차의 득점과 실점 가져오기
            week_goals = df_weekly_goals[(df_weekly_goals['Week'] == w) & (df_weekly_goals['Team'] == team)]['Goals'].values[0]
            week_conceded = df_weekly_conceded[(df_weekly_conceded['Week'] == w) & (df_weekly_conceded['Team'] == team)]['Conceded'].values[0]
            week_gd = week_goals - week_conceded
            
            cum_gd += week_gd
            weekly_gd_data.append({'Week': w, 'Team': team, 'GD': week_gd})
            cumulative_gd_data.append({'Week': w, 'Team': team, 'CumulativeGD': cum_gd})
    
    df_weekly_gd = pd.DataFrame(weekly_gd_data)
    df_cumulative_gd = pd.DataFrame(cumulative_gd_data)
    
    fig_gd = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 막대 그래프 (주차별 득실차)
    for team in teams_list:
        team_data = df_weekly_gd[df_weekly_gd['Team'] == team]
        fig_gd.add_trace(
            go.Bar(
                x=team_data['Week'],
                y=team_data['GD'],
                name=f'{team} (주차별)',
                marker_color=team_colors[team],
                opacity=0.6,
                width=0.25,
                legendgroup=team
            ),
            secondary_y=False
        )
    
    # 선 그래프 (누적 득실차)
    for team in teams_list:
        team_data = df_cumulative_gd[df_cumulative_gd['Team'] == team]
        fig_gd.add_trace(
            go.Scatter(
                x=team_data['Week'],
                y=team_data['CumulativeGD'],
                name=f'{team} (누적)',
                line=dict(color=team_colors[team], width=3),
                mode='lines+markers',
                legendgroup=team
            ),
            secondary_y=True
        )
    
    fig_gd.update_xaxes(title_text="주차", tickmode='linear', dtick=1)
    fig_gd.update_yaxes(title_text="주차별 득실차", secondary_y=False)
    fig_gd.update_yaxes(title_text="누적 득실차", secondary_y=True)
    
    fig_gd.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#212529',
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_gd, use_container_width=True)

