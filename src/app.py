
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

# --- 모든 선수 지표 통합 계산 ---
# 1. 선수-팀 매핑
player_team_map = df_att[['선수이름', '팀이름']].drop_duplicates().set_index('선수이름')['팀이름'].to_dict()

# 2. 기본 지표 (출석, 득점)
att_counts = df_att_processed[df_att_processed['IsAttended'] == 1].groupby('선수이름')['WeekNum'].count().reset_index(name='출석횟수')
df_players_all = pd.merge(att_counts, df_scorers.rename(columns={'Goals': '득점'}), left_on='선수이름', right_on='Player', how='outer').fillna(0)
df_players_all['Team'] = df_players_all['선수이름'].map(player_team_map)
df_players_all['Player'] = df_players_all.apply(lambda x: x['선수이름'] if pd.notna(x['선수이름']) else x['Player'], axis=1)
df_players_all = df_players_all.drop(columns=['선수이름'])

# 3. 주차별 팀 성적 데이터 가공
df_history['Week'] = df_history['Week'].astype(int)
team_points_by_week = df_history.groupby(['Week', 'Team'])['PointsGained'].sum().reset_index()
df_match['주차'] = df_match['주차'].astype(int)

# 득점/실점 주차별 데이터
weekly_stats_temp = []
for idx, row in df_match.iterrows():
    w = row['주차']
    for t in all_teams_raw:
        if t in df_match.columns:
            g = count_goals(row[t])
            if g is not None:
                weekly_stats_temp.append({'Week': w, 'Team': t, 'GF': g})

df_weekly_gf = pd.DataFrame(weekly_stats_temp).groupby(['Week', 'Team'])['GF'].sum().reset_index()

# 실점 계산용
weekly_ga_temp = []
for w in df_match['주차'].unique():
    w_data = df_match[df_match['주차'] == w]
    for t in all_teams_raw:
        ga = 0
        for _, row in w_data.iterrows():
            if t in row and count_goals(row[t]) is not None:
                for opp in all_teams_raw:
                    if opp != t and opp in row:
                        og = count_goals(row[opp])
                        if og is not None: ga += og
        weekly_ga_temp.append({'Week': w, 'Team': t, 'GA': ga})
df_weekly_ga = pd.DataFrame(weekly_ga_temp)

# 4. 복합 지표 계산 함수
def calculate_player_metrics(player_name):
    att_rows = df_att_processed[(df_att_processed['선수이름'] == player_name) & (df_att_processed['IsAttended'] == 1)]
    if att_rows.empty: return pd.Series([0]*8)
    
    my_team = player_team_map.get(player_name)
    if not my_team: return pd.Series([0]*8)
    
    weeks = att_rows['WeekNum'].unique().astype(int)
    
    # 승점 관련
    pts_rows = team_points_by_week[(team_points_by_week['Week'].isin(weeks)) & (team_points_by_week['Team'] == my_team)]
    total_pts = pts_rows['PointsGained'].sum()
    
    # 팀 득점 관련
    gf_rows = df_weekly_gf[(df_weekly_gf['Week'].isin(weeks)) & (df_weekly_gf['Team'] == my_team)]
    total_tg = gf_rows['GF'].sum()
    
    # 팀 실점 관련
    ga_rows = df_weekly_ga[(df_weekly_ga['Week'].isin(weeks)) & (df_weekly_ga['Team'] == my_team)]
    total_ga = ga_rows['GA'].sum()
    
    count = len(weeks)
    return pd.Series([
        total_pts,          # 승점
        total_ga,           # 실점
        total_tg,           # 팀 득점 합계
        total_pts / count,   # 경기당 승점
        total_ga / count,    # 경기당 평균 실점
        total_tg / count     # 경기당 팀 득점
    ])

df_players_all[['승점', '실점', '팀득점합계', '경기당 승점', '경기당 평균 실점', '경기당 팀 득점']] = df_players_all['Player'].apply(calculate_player_metrics)
df_players_all['경기당 득점'] = df_players_all['득점'] / df_players_all['출석횟수'].replace(0, 1)

tab1, tab2, tab3, tab4 = st.tabs(["🏆 종합 순위", "🏃 개인 기록", "📈 트렌드 분석", "📊 선수 상세 데이터"])

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
    
    df_scorers_display = df_players_all.sort_values(by='득점', ascending=False).head(10).copy()
    df_scorers_display['Team'] = df_scorers_display['Team'].map(display_team_map)
    df_scorers_display = df_scorers_display.rename(columns={'Player': '선수', 'Team': '팀'})
    st.markdown(df_to_html_table(df_scorers_display[['선수', '팀', '득점']].reset_index(drop=True)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 2. 아이언 맨 (출석왕)
    st.subheader("🦸 아이언 맨 (Top 10)")
    st.caption("리그의 기둥! 성실함의 상징, 철의 체력으로 모든 경기를 함께합니다.")
    df_att_king = df_players_all.sort_values(by='출석횟수', ascending=False).head(10).copy()
    df_att_king['Team'] = df_att_king['Team'].map(display_team_map)
    st.markdown(df_to_html_table(df_att_king[['Player', 'Team', '출석횟수']].rename(columns={'Player': '선수', 'Team': '팀'}).reset_index(drop=True)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 3. 가성비 스트라이커
    st.subheader("⚡ 가성비 스트라이커 (Top 10)")
    st.caption("최강의 효율! 적은 기회도 놓치지 않고 득점으로 연결하는 해결사입니다. (득점/출석횟수)")
    df_eff = df_players_all[df_players_all['출석횟수'] > 0].sort_values(by=['경기당 득점', '득점'], ascending=[False, False]).head(10).copy()
    df_eff['Team'] = df_eff['Team'].map(display_team_map)
    df_eff['경기당 득점'] = df_eff['경기당 득점'].apply(lambda x: f'{x:.2f}')
    st.markdown(df_to_html_table(df_eff[['Player', '경기당 득점', '득점', '출석횟수', 'Team']].rename(columns={'Player': '선수', 'Team': '팀', '경기당 득점': '가성비(경기당 득점)'}).reset_index(drop=True)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 4. 승리 요정
    st.subheader("🧚 승리 요정 (Top 10)")
    st.caption("승리의 부적! 내가 경기에 나서는 것만으로도 팀의 승리 확률이 올라갑니다. (나올 때 팀 평균 승점)")
    df_lucky = df_players_all[df_players_all['출석횟수'] > 0].sort_values(by=['경기당 승점', '승점'], ascending=[False, False]).head(10).copy()
    df_lucky['Team'] = df_lucky['Team'].map(display_team_map)
    df_lucky['경기당 승점'] = df_lucky['경기당 승점'].apply(lambda x: f'{x:.2f}')
    df_lucky['승점'] = df_lucky['승점'].astype(int)
    st.markdown(df_to_html_table(df_lucky[['Player', '경기당 승점', '승점', '출석횟수', 'Team']].rename(columns={'Player': '선수', 'Team': '팀', '경기당 승점': '기여 승점(평균)'}).reset_index(drop=True)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 5. 득점 폭격기
    st.subheader("🚀 득점 폭격기 (Top 10)")
    st.caption("공격의 불씨! 내가 그라운드에 있으면 팀 전체의 화력이 불을 뿜습니다. (나올 때 팀 평균 득점)")
    df_gf = df_players_all[df_players_all['출석횟수'] > 0].sort_values(by=['경기당 팀 득점', '팀득점합계'], ascending=[False, False]).head(10).copy()
    df_gf['Team'] = df_gf['Team'].map(display_team_map)
    df_gf['경기당 팀 득점'] = df_gf['경기당 팀 득점'].apply(lambda x: f'{x:.2f}')
    st.markdown(df_to_html_table(df_gf[['Player', '경기당 팀 득점', '팀득점합계', '출석횟수', 'Team']].rename(columns={'Player': '선수', 'Team': '팀', '경기당 팀 득점': '팀 평균 득점', '팀득점합계': '누적 팀 득점'}).reset_index(drop=True)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 6. 통곡의 벽
    st.subheader("🧱 통곡의 벽 (Bottom 10)")
    st.caption("철통 보안! 상대 공격수들을 절망에 빠뜨리는 든든한 수비의 핵심입니다. (나올 때 팀 평균 실점)")
    df_shield = df_players_all[df_players_all['출석횟수'] > 0].sort_values(by=['경기당 평균 실점', '출석횟수'], ascending=[True, False]).head(10).copy()
    df_shield['Team'] = df_shield['Team'].map(display_team_map)
    df_shield['경기당 평균 실점'] = df_shield['경기당 평균 실점'].apply(lambda x: f'{x:.2f}')
    st.markdown(df_to_html_table(df_shield[['Player', '경기당 평균 실점', '실점', '출석횟수', 'Team']].rename(columns={'Player': '선수', 'Team': '팀', '경기당 평균 실점': '팀 평균 실점'}).reset_index(drop=True)), unsafe_allow_html=True)

# ==========================================
# 탭 3: 트렌드 분석
# ==========================================
with tab3:
    st.subheader("📊 주차별 추이 분석")
    
    all_weeks = sorted(df_history['Week'].unique())
    teams_list = all_teams_raw
    
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
        display_name = display_team_map.get(team, team)
        fig_points.add_trace(
            go.Bar(
                x=team_data['Week'],
                y=team_data['Points'],
                name=f'{display_name} (주차별)',
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
        display_name = display_team_map.get(team, team)
        fig_points.add_trace(
            go.Scatter(
                x=team_data['Week'],
                y=team_data['CumulativePoints'],
                name=f'{display_name} (누적)',
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
        display_name = display_team_map.get(team, team)
        fig_goals.add_trace(
            go.Bar(
                x=team_data['Week'],
                y=team_data['Goals'],
                name=f'{display_name} (주차별)',
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
        display_name = display_team_map.get(team, team)
        fig_goals.add_trace(
            go.Scatter(
                x=team_data['Week'],
                y=team_data['CumulativeGoals'],
                name=f'{display_name} (누적)',
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
        display_name = display_team_map.get(team, team)
        fig_conceded.add_trace(
            go.Bar(
                x=team_data['Week'],
                y=team_data['Conceded'],
                name=f'{display_name} (주차별)',
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
        display_name = display_team_map.get(team, team)
        fig_conceded.add_trace(
            go.Scatter(
                x=team_data['Week'],
                y=team_data['CumulativeConceded'],
                name=f'{display_name} (누적)',
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
        display_name = display_team_map.get(team, team)
        fig_gd.add_trace(
            go.Bar(
                x=team_data['Week'],
                y=team_data['GD'],
                name=f'{display_name} (주차별)',
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
        display_name = display_team_map.get(team, team)
        fig_gd.add_trace(
            go.Scatter(
                x=team_data['Week'],
                y=team_data['CumulativeGD'],
                name=f'{display_name} (누적)',
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

# ==========================================
# 탭 4: 선수 상세 데이터
# ==========================================
with tab4:
    st.subheader("📊 팀별 선수 상세 기록")
    st.markdown("모든 지표를 한눈에 확인할 수 있는 통합 테이블입니다.")
    
    for t_raw in all_teams_raw:
        display_name = display_team_map.get(t_raw, t_raw)
        st.markdown(f"### {display_name}")
        
        df_team_players = df_players_all[df_players_all['Team'] == t_raw].copy()
        
        # 컬럼 포맷팅
        df_team_players = df_team_players.rename(columns={
            'Player': '선수이름',
            '출석횟수': '🦸 아이언맨(출석)',
            '득점': '🎯 개인 득점',
            '경기당 득점': '⚡ 가성비(G/A)',
            '경기당 승점': '🧚 승리요정(P/A)',
            '경기당 팀 득점': '🚀 폭격기(TG/A)',
            '경기당 평균 실점': '🧱 통곡의벽(TA/A)',
            '승점': '팀 승점 합계',
            '실점': '팀 실점 합계'
        })
        
        # 숫자 형식 정리
        cols_to_format = ['⚡ 가성비(G/A)', '🧚 승리요정(P/A)', '🚀 폭격기(TG/A)', '🧱 통곡의벽(TA/A)']
        for col in cols_to_format:
            df_team_players[col] = df_team_players[col].apply(lambda x: f'{x:.2f}')
            
        int_cols = ['🦸 아이언맨(출석)', '팀 승점 합계', '🎯 개인 득점', '팀 실점 합계']
        for col in int_cols:
            df_team_players[col] = df_team_players[col].astype(int)
            
        display_cols = ['선수이름', '🦸 아이언맨(출석)', '🎯 개인 득점', '⚡ 가성비(G/A)', '🧚 승리요정(P/A)', '🚀 폭격기(TG/A)', '🧱 통곡의벽(TA/A)', '팀 승점 합계', '팀 실점 합계']
        st.markdown(df_to_html_table(df_team_players[display_cols].sort_values(by='🦸 아이언맨(출석)', ascending=False).reset_index(drop=True)), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
