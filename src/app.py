
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
        match_result: True면 경기 결과 테이블 (텍스트 중앙 정렬)
    """
    # 스타일 설정
    if match_result:
        # 경기 결과: 모두 중앙 정렬
        cell_style = 'text-align: center; padding: 8px 12px;'
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
    table_class = "match-result-table" if match_result else "standard-table"
    html = f'<div class="table-container">'
    html += f'<table class="{table_class}" style="width: 100%; border-collapse: collapse; color: #212529; table-layout: fixed;">'
    
    # 경기 결과 테이블의 경우 각 컬럼 너비 강제 고정
    if match_result:
        col_count = len(df.columns)
        # 인덱스(라운드)는 80px, 나머지는 균등 분할
        html += '<colgroup>'
        html += '<col style="width: 80px;">'
        for _ in range(col_count):
            html += f'<col style="width: calc((100% - 80px) / {col_count});">'
        html += '</colgroup>'

    # 헤더
    html += '<thead><tr>'
    if df.index.name or not all(isinstance(i, int) for i in df.index):
        # 라운드(인덱스) 컬럼 스타일
        html += f'<th style="{header_style}">{df.index.name if df.index.name else ""}</th>'
    
    # 데이터 컬럼
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
    html += '</div>'
    
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
        gap: 4px;
        background-color: #ffffff !important;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        padding-bottom: 5px !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: nowrap;
        background-color: #f8f9fa !important;
        border-radius: 4px;
        color: #495057 !important;
        padding: 8px 10px;
        font-size: 13px;
        border: 1px solid #e9ecef !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0d6efd !important;
        color: white !important;
        border-color: #0d6efd !important;
    }
    
    /* 메트릭 박스 */
    div[data-testid="stMetricValue"] {
        font-size: 20px !important;
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
    
    /* 테이블 컨테이너 가로 스크롤 강제 */
    .table-container {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin-bottom: 1rem;
    }
    
    table {
        color: #212529 !important;
        background-color: #ffffff !important;
        width: 100% !important;
        min-width: 400px; /* 너무 쪼그라들지 않게 */
        border-collapse: collapse;
        font-size: 14px;
    }
    
    /* 테이블 헤더 - 굵게, 가운데 정렬 */
    th {
        background-color: #f1f3f5 !important;
        color: #495057 !important;
        font-weight: 700 !important;
        text-align: center !important;
        padding: 10px 6px !important;
        border: 1px solid #dee2e6 !important;
        white-space: nowrap;
    }
    
    /* 테이블 데이터 셀 - 가운데 정렬 */
    td {
        background-color: #ffffff !important;
        color: #212529 !important;
        text-align: center !important;
        padding: 10px 6px !important;
        border: 1px solid #dee2e6 !important;
    }
    
    /* 인덱스 컬럼 스타일 */
    .row_heading {
        font-weight: 700 !important;
        text-align: center !important;
    }
    
    /* 컬럼 너비 설정 */
    table {
        table-layout: auto;
    }
    
    .match-result-table {
        table-layout: fixed !important;
        width: 100% !important;
    }
    
    /* 경기 결과 테이블 내의 셀 텍스트 줄바꿈 허용 */
    .match-result-table td {
        word-break: break-all !important;
        white-space: normal !important;
    }
    
    /* Expander 내부 테이블 - 경기 결과용 (중앙 정렬) */
    details table td {
        text-align: center !important;
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

# --- 팀 범례 (모바일 최적화용) ---
st.markdown("""
<div style="display: flex; gap: 15px; justify-content: center; align-items: center; background-color: #f8f9fa; padding: 12px; border-radius: 10px; margin: 5px 0 20px 0; border: 1px solid #e9ecef; flex-wrap: wrap;">
    <div style="display: flex; align-items: center; gap: 6px;"><span style="font-size: 1.1rem;">🔴</span> <span style="font-weight: 700; color: #ef4444;">타르가르옌</span></div>
    <div style="display: flex; align-items: center; gap: 6px;"><span style="font-size: 1.1rem;">🔵</span> <span style="font-weight: 700; color: #3b82f6;">스타크</span></div>
    <div style="display: flex; align-items: center; gap: 6px;"><span style="font-size: 1.1rem;">🟡</span> <span style="font-weight: 700; color: #eab308;">라니스터</span></div>
</div>
""", unsafe_allow_html=True)

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

# 표 내부용 짧은 팀 이름 매핑 (이모지만 표시)
team_short_map = {
    t: ('🔴' if '레드' in t else '🔵' if '블루' in t else '🟡') 
    for t in all_teams_raw
}

# --- 데이터 전처리를 위한 기본 정보 구성 ---
df_history['Week'] = df_history['Week'].astype(int)
team_points_by_week = df_history.groupby(['Week', 'Team'])['PointsGained'].sum().reset_index()
df_match['주차'] = df_match['주차'].astype(int)

# 득점/실점 주차별 데이터 (임팩트 분석 등에서 재사용)
weekly_stats_temp = []
for idx, row in df_match.iterrows():
    w = row['주차']
    for t in all_teams_raw:
        if t in df_match.columns:
            g = count_goals(row[t])
            if g is not None:
                weekly_stats_temp.append({'Week': w, 'Team': t, 'GF': g})

df_weekly_gf = pd.DataFrame(weekly_stats_temp).groupby(['Week', 'Team'])['GF'].sum().reset_index()

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

# --- 모든 선수 지표 통합 계산 (임팩트 포함) ---
# 1. 선수-팀 매핑 정보 확보
player_team_map = df_att[['선수이름', '팀이름']].drop_duplicates().set_index('선수이름')['팀이름'].to_dict()

# 2. 기초 데이터 병합 (출석 + 득점)
att_counts = df_att_processed[df_att_processed['IsAttended'] == 1].groupby('선수이름')['WeekNum'].count().reset_index(name='출석횟수')
df_players_base = pd.merge(att_counts, df_scorers.rename(columns={'Goals': '득점'}), left_on='선수이름', right_on='Player', how='outer').fillna(0)
df_players_base['Player'] = df_players_base.apply(lambda x: x['선수이름'] if pd.notna(x['선수이름']) and x['선수이름'] != 0 else x['Player'], axis=1)
df_players_base['Team'] = df_players_base['Player'].map(player_team_map)
df_players_base = df_players_base[['Player', 'Team', '출석횟수', '득점']].reset_index(drop=True)

# 3. 상세 지표 계산 함수
def calculate_full_player_metrics(player_name):
    # 항상 14개의 요소를 반환해야 함 (순서 중요)
    default_vals = [0.0] * 14
    
    my_team = player_team_map.get(player_name)
    att_rows = df_att_processed[(df_att_processed['선수이름'] == player_name) & (df_att_processed['IsAttended'] == 1)]
    
    if att_rows.empty or not my_team:
        return pd.Series(default_vals)
    
    present_weeks = att_rows['WeekNum'].unique().astype(int)
    all_weeks = sorted(df_history['Week'].unique())
    absent_weeks = [w for w in all_weeks if w not in present_weeks]
    
    # 출전 시 성적
    p_pts_df = team_points_by_week[(team_points_by_week['Week'].isin(present_weeks)) & (team_points_by_week['Team'] == my_team)]['PointsGained']
    p_gf_df = df_weekly_gf[(df_weekly_gf['Week'].isin(present_weeks)) & (df_weekly_gf['Team'] == my_team)]['GF']
    p_ga_df = df_weekly_ga[(df_weekly_ga['Week'].isin(present_weeks)) & (df_weekly_ga['Team'] == my_team)]['GA']
    
    avg_p_pts = p_pts_df.mean() if not p_pts_df.empty else 0.0
    avg_p_gf = p_gf_df.mean() if not p_gf_df.empty else 0.0
    avg_p_ga = p_ga_df.mean() if not p_ga_df.empty else 0.0
    
    # 결장 시 성적
    a_pts_df = team_points_by_week[(team_points_by_week['Week'].isin(absent_weeks)) & (team_points_by_week['Team'] == my_team)]['PointsGained']
    a_gf_df = df_weekly_gf[(df_weekly_gf['Week'].isin(absent_weeks)) & (df_weekly_gf['Team'] == my_team)]['GF']
    a_ga_df = df_weekly_ga[(df_weekly_ga['Week'].isin(absent_weeks)) & (df_weekly_ga['Team'] == my_team)]['GA']
    
    avg_a_pts = a_pts_df.mean() if not a_pts_df.empty else 0.0
    avg_a_gf = a_gf_df.mean() if not a_gf_df.empty else 0.0
    avg_a_ga = a_ga_df.mean() if not a_ga_df.empty else 0.0
    
    return pd.Series([
        p_pts_df.sum(), p_ga_df.sum(), p_gf_df.sum(), # 누적 합계 (3)
        avg_p_pts, avg_p_ga, avg_p_gf,             # 출전 평균 (3)
        avg_a_pts, avg_a_ga, avg_a_gf,             # 결장 평균 (3)
        avg_p_pts - avg_a_pts, avg_p_gf - avg_a_gf, avg_p_ga - avg_a_ga, # 임팩트 (3)
        float(len(present_weeks)), float(len(absent_weeks)) # 주차수 (2)
    ])

# 4. 전체 선수에 대해 지표 적용 (인덱스 정렬 유지)
metrics_data = []
for p_name in df_players_base['Player']:
    metrics_data.append(calculate_full_player_metrics(p_name))

metrics_df = pd.DataFrame(metrics_data)
metrics_df.columns = [
    '팀승점합계', '팀실점합계', '팀득점합계',
    '출전_평균승점', '출전_평균실점', '출전_평균득점',
    '결장_평균승점', '결장_평균실점', '결장_평균득점',
    '임팩트_승점', '임팩트_득점', '임팩트_실점',
    '출석주차수', '결장주차수'
]

# 인덱스를 기준으로 완벽하게 합침
df_players_all = pd.concat([df_players_base, metrics_df], axis=1)
df_players_all['경기당 득점'] = (df_players_all['득점'] / df_players_all['출석횟수'].replace(0, 1)).fillna(0)

tab1, tab2, tab5, tab3, tab4, tab6 = st.tabs(["🏆 종합 순위", "🏃 개인 기록", "🌟 개인 임팩트", "📈 팀 트렌드", "📊 개인 상세", "📅 주차별 출석표"])

# ==========================================
# 탭 1: 종합 순위
# ==========================================
with tab1:
    st.subheader("종합 순위")
    
    # 순위표 표시
    df_teams_display = df_teams.copy()
    df_teams_display['Team'] = df_teams_display['Team'].map(team_short_map)
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
                    # 표 헤더용 짧은 이름 사용
                    short_name = team_short_map.get(team, team)
                    if team in row:
                        my_goals = team_scores[team]
                        if my_goals is None:
                            res_row[short_name] = '-'
                            continue
                            
                        my_scorers = get_scorers_list(row[team])
                        opp_scores = [v for k, v in team_scores.items() if k != team and v is not None]
                        max_opp = max(opp_scores) if opp_scores else 0
                        
                        scorers_text = f" ({', '.join(my_scorers)})" if my_scorers else ""
                        
                        if my_goals > max_opp:
                            res_row[short_name] = f"승{scorers_text}"
                        elif my_goals == max_opp:
                            res_row[short_name] = f"무{scorers_text}" if my_goals > 0 else "무"
                        else:
                            res_row[short_name] = f"패{scorers_text}" if my_scorers else "패"
                    else:
                        res_row[short_name] = '-'
                
                formatted_data.append(res_row)
            
            # DataFrame 생성
            formatted_df = pd.DataFrame(formatted_data)
            
            # 주차별 승점 합계 계산
            week_points = df_history[df_history['Week'] == week].groupby('Team')['PointsGained'].sum()
            
            # 승점 합계 row 추가
            points_row = {'라운드': '승점 합계'}
            for team in all_teams_raw:
                # 합계 행에서도 짧은 이름 사용
                short_name = team_short_map.get(team, team)
                points_row[short_name] = int(week_points.get(team, 0))
            
            formatted_df = pd.concat([formatted_df, pd.DataFrame([points_row])], ignore_index=True)
            
            # 경기 결과 테이블 - 헤더는 중앙, 값은 왼쪽 정렬
            st.markdown(df_to_html_table(formatted_df.set_index('라운드'), match_result=True), unsafe_allow_html=True)

# ==========================================
# 탭 2: 개인 기록
# ==========================================
with tab2:
    # 랭킹 표시 공통 헬퍼 함수
    def display_personal_rankings(df, sort_col, title, caption, rename_map, display_cols, is_ascending=False, teams=all_teams_raw):
        st.subheader(title)
        st.caption(caption)
        
        # 1. 전체 TOP 10
        df_overall = df.sort_values(by=sort_col, ascending=is_ascending).head(10).reset_index(drop=True)
        df_overall.index += 1
        df_overall_disp = df_overall.copy()
        df_overall_disp['Team'] = df_overall_disp['Team'].map(team_short_map)
        st.markdown(f"**전체 순위**")
        st.markdown(df_to_html_table(df_overall_disp[display_cols].rename(columns=rename_map)), unsafe_allow_html=True)
        
        # 2. 팀별 TOP 5
        st.markdown(f"**팀별 순위 (Top 5)**")
        t_cols = st.columns(len(teams))
        for i, t_raw in enumerate(teams):
            with t_cols[i]:
                st.markdown(f"**{display_team_map.get(t_raw)}**")
                t_df = df[df['Team'] == t_raw].sort_values(by=sort_col, ascending=is_ascending).head(5).reset_index(drop=True)
                t_df.index += 1
                # 팀별 표에는 팀 이름을 뺌
                t_disp_cols = [c for c in display_cols if c != 'Team']
                t_rename_map = {k: v for k, v in rename_map.items() if k != 'Team'}
                st.markdown(df_to_html_table(t_df[t_disp_cols].rename(columns=t_rename_map)), unsafe_allow_html=True)
        st.markdown("---")

    # 1. Golden Boot
    display_personal_rankings(
        df_players_all, 
        sort_col='득점', 
        title="👟 Golden Boot (득점왕)", 
        caption="리그 최고의 득점 기계! 가장 많은 골을 터뜨린 주인공입니다.",
        rename_map={'Player': '선수', 'Team': '팀', '득점': '득점'},
        display_cols=['Player', '득점', 'Team']
    )
    
    # 2. 아이언 맨
    display_personal_rankings(
        df_players_all, 
        sort_col='출석횟수', 
        title="🦸 아이언 맨 (출석왕)", 
        caption="리그의 기둥! 성실함의 상징, 철의 체력으로 모든 경기를 함께합니다.",
        rename_map={'Player': '선수', 'Team': '팀', '출석횟수': '출석횟수'},
        display_cols=['Player', '출석횟수', 'Team']
    )

    # 3. 가성비 스트라이커
    df_eff_base = df_players_all[df_players_all['출석횟수'] > 0].copy()
    df_eff_base['출석 당 득점_disp'] = df_eff_base['경기당 득점'].apply(lambda x: f'{x:.2f}')
    display_personal_rankings(
        df_eff_base, 
        sort_col='경기당 득점', 
        title="⚡ 가성비 스트라이커 (Top 10)", 
        caption="최강의 효율! 적은 기회도 놓치지 않고 득점으로 연결하는 해결사입니다. (득점/출석횟수)",
        rename_map={'Player': '선수', 'Team': '팀', '출석 당 득점_disp': '출석 당 득점', '득점': '개인득점', '출석횟수': '출석'},
        display_cols=['Player', '출석 당 득점_disp', '득점', '출석횟수', 'Team']
    )
    
    # 4. 승리 요정
    df_lucky_base = df_players_all[df_players_all['출석횟수'] > 0].copy()
    df_lucky_base['출석 당 팀승점_disp'] = df_lucky_base['출전_평균승점'].apply(lambda x: f'{x:.2f}')
    display_personal_rankings(
        df_lucky_base, 
        sort_col='출전_평균승점', 
        title="🧚 승리 요정 (Top 10)", 
        caption="승리의 부적! 내가 경기에 나서는 것만으로도 팀의 승리 확률이 올라갑니다. (나올 때 팀 평균 승점)",
        rename_map={'Player': '선수', 'Team': '팀', '출석 당 팀승점_disp': '출석 당 팀승점', '팀승점합계': '누적 팀승점', '출석횟수': '출석'},
        display_cols=['Player', '출석 당 팀승점_disp', '팀승점합계', '출석횟수', 'Team']
    )
    
    # 5. 득점 폭격기
    df_gf_base = df_players_all[df_players_all['출석횟수'] > 0].copy()
    df_gf_base['출석 당 팀득점_disp'] = df_gf_base['출전_평균득점'].apply(lambda x: f'{x:.2f}')
    display_personal_rankings(
        df_gf_base, 
        sort_col='출전_평균득점', 
        title="🚀 득점 폭격기 (Top 10)", 
        caption="공격의 불씨! 내가 그라운드에 있으면 팀 전체의 화력이 불을 뿜습니다. (나올 때 팀 평균 득점)",
        rename_map={'Player': '선수', 'Team': '팀', '출석 당 팀득점_disp': '출석 당 팀득점', '팀득점합계': '누적 팀 득점', '출석횟수': '출석'},
        display_cols=['Player', '출석 당 팀득점_disp', '팀득점합계', '출석횟수', 'Team']
    )
    
    # 6. 통곡의 벽
    df_shield_base = df_players_all[df_players_all['출석횟수'] > 0].copy()
    df_shield_base['출석 당 팀실점_disp'] = df_shield_base['출전_평균실점'].apply(lambda x: f'{x:.2f}')
    display_personal_rankings(
        df_shield_base, 
        sort_col='출전_평균실점', 
        title="🧱 통곡의 벽 (Bottom 10)", 
        caption="철통 보안! 상대 공격수들을 절망에 빠뜨리는 든든한 수비의 핵심입니다. (나올 때 팀 평균 실점)",
        rename_map={'Player': '선수', 'Team': '팀', '출석 당 팀실점_disp': '출석 당 팀실점', '팀실점합계': '누적 팀실점', '출석횟수': '출석'},
        display_cols=['Player', '출석 당 팀실점_disp', '팀실점합계', '출석횟수', 'Team'],
        is_ascending=True # 실점은 낮은게 좋은 순위
    )

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
            '경기당 득점': '⚡ 출석 당 득점',
            '출전_평균승점': '🧚 출석 당 팀승점',
            '출전_평균득점': '🚀 출석 당 팀득점',
            '출전_평균실점': '🧱 출석 당 팀실점',
            '임팩트_승점': '🔥 승점 임팩트',
            '임팩트_득점': '🚀 득점 임팩트',
            '임팩트_실점': '🛡️ 실점 임팩트',
            '팀승점합계': '팀 승점 합계',
            '팀득점합계': '팀 득점 합계',
            '팀실점합계': '팀 실점 합계'
        })
        
        # 숫자 형식 정리
        cols_to_format = ['⚡ 출석 당 득점', '🧚 출석 당 팀승점', '🚀 출석 당 팀득점', '🧱 출석 당 팀실점', '🔥 승점 임팩트', '🚀 득점 임팩트', '🛡️ 실점 임팩트']
        for col in cols_to_format:
            df_team_players[col] = df_team_players[col].apply(lambda x: f'{x:+.2f}')
            
        int_cols = ['🦸 아이언맨(출석)', '팀 승점 합계', '팀 득점 합계', '🎯 개인 득점', '팀 실점 합계']
        for col in int_cols:
            df_team_players[col] = df_team_players[col].fillna(0).astype(int)
            
        display_cols = [
            '선수이름', '🦸 아이언맨(출석)', '팀 승점 합계', '팀 득점 합계', '팀 실점 합계',
            '🎯 개인 득점', '⚡ 출석 당 득점', 
            '🧚 출석 당 팀승점', '🚀 출석 당 팀득점', '🧱 출석 당 팀실점',
            '🔥 승점 임팩트', '🚀 득점 임팩트', '🛡️ 실점 임팩트'
        ]
        
        # 표 내부의 팀명은 이모지로 (이미 팀별 섹션이지만 컬럼이 남아있을 경우를 대비하거나 명시적 표시 시 사용)
        if 'Team' in df_team_players.columns:
            df_team_players['Team'] = df_team_players['Team'].map(team_short_map)

        st.markdown(df_to_html_table(df_team_players[display_cols].sort_values(by='🦸 아이언맨(출석)', ascending=False).reset_index(drop=True)), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
# ==========================================
# 탭 5: 임팩트 분석
# ==========================================
with tab5:
    st.subheader("🌟 임팩트 분석 (Game Changer)")
    st.markdown("임팩트 = (내가 출전했을 때 팀 평균) - (내가 결장했을 때 팀 평균)")
    
    impact_data = df_players_all[(df_players_all['출석주차수'] > 0) & (df_players_all['결장주차수'] > 0)].copy()
    
    if impact_data.empty:
        st.warning("아직 분석을 위한 충분한 데이터(출전 및 결장 기록)가 쌓이지 않았습니다.")
    else:
        # 공통 스타일 함수
        def display_impact_rankings(df, target_col, title, caption, is_ascending=False, value_suffix=""):
            st.markdown(f"### {title}")
            st.caption(caption)
            
            # 1. 전체 랭킹 조회
            top_n = 10
            sorted_df = df.sort_values(by=target_col, ascending=is_ascending).head(top_n).reset_index(drop=True)
            sorted_df.index += 1
            
            # 표시 컬럼 설정
            # target_col 이 '임팩트_승점' 인 경우, '출전_평균승점', '결장_평균승점' 매칭
            baseline = target_col.replace('임팩트_', '')
            disp_cols = ['Player', target_col, f'출전_평균{baseline}', f'결장_평균{baseline}', 'Team']
            disp_df = sorted_df[disp_cols].copy()
            disp_df['Team'] = disp_df['Team'].map(team_short_map)
            
            # 컬럼명 정리
            col_map = {
                'Player': '선수', 'Team': '팀',
                target_col: '🔥 임팩트',
                f'출전_평균{baseline}': '출전 시(A)',
                f'결장_평균{baseline}': '결장 시(B)'
            }
            disp_df = disp_df.rename(columns=col_map)
            
            # 포맷팅
            format_cols = ['🔥 임팩트', '출전 시(A)', '결장 시(B)']
            for c in format_cols:
                disp_df[c] = disp_df[c].apply(lambda x: f'{x:+.2f}{value_suffix}')
            
            st.markdown(f"**전체 순위**")
            st.markdown(df_to_html_table(disp_df), unsafe_allow_html=True)
            
            # 2. 팀별 랭킹 (Top 5)
            st.markdown(f"**팀별 순위 (Top 5)**")
            t_cols = st.columns(len(all_teams_raw))
            for i, t_raw in enumerate(all_teams_raw):
                with t_cols[i]:
                    st.markdown(f"**{display_team_map.get(t_raw)}**")
                    t_df = df[df['Team'] == t_raw].sort_values(by=target_col, ascending=is_ascending).head(5).reset_index(drop=True)
                    t_df.index += 1
                    
                    baseline = target_col.replace('임팩트_', '')
                    t_disp = t_df[['Player', target_col, f'출전_평균{baseline}', f'결장_평균{baseline}']].copy()
                    
                    col_map_t = {
                        'Player': '선수',
                        target_col: '🔥 임팩트',
                        f'출전_평균{baseline}': '출전(A)',
                        f'결장_평균{baseline}': '결장(B)'
                    }
                    t_disp = t_disp.rename(columns=col_map_t)
                    
                    # 소수점 포맷
                    for c in ['🔥 임팩트', '출전(A)', '결장(B)']:
                        t_disp[c] = t_disp[c].apply(lambda x: f'{x:+.2f}' if pd.notna(x) else '0.00')
                        
                    st.markdown(df_to_html_table(t_disp), unsafe_allow_html=True)
            st.markdown("---")

        # 1. 승점 임팩트
        display_impact_rankings(impact_data, '임팩트_승점', "🏆 승점 임팩트 (승리 유전자)", "진정한 승리 전문가! 내가 경기에 나서는 것만으로도 팀의 승점 기대치가 이만큼 상승합니다.")
        
        # 2. 득점 임팩트
        display_impact_rankings(impact_data, '임팩트_득점', "⚽ 득점 임팩트 (공격의 핵)", "팀 화력의 기폭제! 내가 그라운드에 있을 때 우리 팀은 더 많은 골을 터뜨리게 됩니다.")
        
        # 3. 실점 임팩트 (Bottom 10/5)
        display_impact_rankings(impact_data, '임팩트_실점', "🛡️ 실점 임팩트 (통곡의 벽)", "골문 최후의 보루! 내가 수비 중심을 잡으면 상대 팀의 득점 확률이 눈에 띄게 줄어듭니다.", is_ascending=True)


# ==========================================
# 탭 6: 주차별 출석표
# ==========================================
with tab6:
    st.subheader("📅 주차별 출석표")
    st.markdown("전체 선수의 주차별 출석 현황입니다. (✅: 출석, ❌: 결장)")
    
    # 주차 컬럼들 추출 (컬럼명에 '주차'가 포함된 것들)
    week_cols = [c for c in df_att.columns if '주차' in c]
    # 주차 숫자로 정렬 (1주차, 2주차, ..., 10주차 순서 보장)
    import re
    def extract_week_num(col_name):
        match = re.search(r'(\d+)', col_name)
        return int(match.group(1)) if match else 999
    
    week_cols = sorted(week_cols, key=extract_week_num)
    
    # 출석 인정 기준 값들
    POSITIVE_VALS = ['1', '1.0', 'o', 'O', 'v', 'V', '참석', '출석', 'true', 'True']
    NEGATIVE_VALS = ['0', '0.0', 'x', 'X', '불참', '결장', 'false', 'False']
    
    for t_raw in all_teams_raw:
        display_name = display_team_map.get(t_raw, t_raw)
        st.markdown(f"### {display_name}")
        
        # 해당 팀 데이터 필터링 (팀이름이 다를 수 있으므로 포함 여부로 체크하거나 strip)
        df_team_att = df_att[df_att['팀이름'].str.strip() == t_raw.strip()].copy()
        
        if df_team_att.empty:
            # 혹시나 팀명이 정확히 안 맞을 경우를 대비해 키워드 검색
            short_keyword = '레드' if '레드' in t_raw else '블루' if '블루' in t_raw else '옐로' if '옐로' in t_raw else t_raw
            df_team_att = df_att[df_att['팀이름'].str.contains(short_keyword)].copy()
            
        if df_team_att.empty:
            st.info(f"{display_name} 팀의 출석 데이터가 없습니다.")
            continue
            
        # 출석 데이터 시각화 보정
        plot_df = df_team_att.copy()
        
        # 누적 출석 횟수 계산 함수
        def is_attended(val):
            v = str(val).strip().lower()
            if v in [pv.lower() for pv in POSITIVE_VALS]: return True
            try:
                if float(v) > 0: return True
            except: pass
            return False

        # 각 행(선수)별로 누적 출석 계산
        plot_df['누적 출석'] = df_team_att[week_cols].apply(lambda row: sum(is_attended(v) for v in row), axis=1)
        
        for col in week_cols:
            def format_att(val):
                if is_attended(val):
                    return '✅'
                v = str(val).strip().lower()
                if v in [nv.lower() for nv in NEGATIVE_VALS]:
                    return '❌'
                if v == '' or v == 'nan':
                    return '-'
                return '❌' if v.isdigit() else v

            plot_df[col] = plot_df[col].apply(format_att)
        
        # 표시할 컬럼 (선수이름 + 누적 출석 + 모든 주차)
        display_cols = ['선수이름', '누적 출석'] + [c for c in week_cols if c in plot_df.columns]
        
        # 테이블 출력
        st.markdown(df_to_html_table(plot_df[display_cols].reset_index(drop=True)), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
