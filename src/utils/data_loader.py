import pandas as pd
import os
import streamlit as st

def load_data_from_url():
    """공개된 Google Sheets URL에서 데이터를 읽어옵니다. (Raw CSV 방식)"""
    try:
        base_url = st.secrets["google_sheets"]["spreadsheet_url"]
        doc_id = base_url.split('/d/')[1].split('/')[0]
        
        # ⚠️ gviz API의 타입 추론 오류를 피하기 위해 Raw Export API 사용
        # match_result (gid=1046780866), attendance (gid=1984754051)
        match_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid=1046780866"
        att_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid=1984754051"
        
        # 모든 데이터를 문자열로 로드하여 데이터 유실 방지
        df_match = pd.read_csv(match_url, dtype=str).fillna('')
        df_att = pd.read_csv(att_url, dtype=str).fillna('')
        
        # 컬럼명 공백 제거
        df_match.columns = [c.strip() for c in df_match.columns]
        df_att.columns = [c.strip() for c in df_att.columns]
        
        # '주차' 컬럼 기준 데이터 정제
        if '주차' in df_match.columns:
            df_match = df_match[df_match['주차'].str.strip() != ''].reset_index(drop=True)
            
        return df_match, df_att
    except Exception as e:
        st.warning(f"Google Sheets 연결 실패 (로컬 데이터를 사용합니다): {e}")
        return load_data_from_local()

def load_data_from_local():
    """로컬 TSV 파일을 읽어서 DataFrame으로 반환합니다."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    match_file = os.path.join(project_root, 'data', 'match_result_sample.tsv')
    att_file = os.path.join(project_root, 'data', 'attendance_sample.tsv')
    
    df_match = pd.read_csv(match_file, sep='\t')
    df_att = pd.read_csv(att_file, sep='\t')
    
    return df_match, df_att

def load_data():
    """
    데이터 로드 메인 함수.
    1. st.secrets에 spreadsheet_url이 설정되어 있으면 구글 시트 우선 로드.
    2. 환경 변수 USE_GOOGLE_SHEETS가 true여도 구글 시트 로드.
    3. 그 외에는 로컬 데이터 로드.
    """
    use_url_env = os.getenv('USE_GOOGLE_SHEETS', 'false').lower() == 'true'
    has_url_secret = False
    
    try:
        if "google_sheets" in st.secrets and st.secrets["google_sheets"].get("spreadsheet_url"):
            has_url_secret = True
    except:
        pass

    if has_url_secret or use_url_env:
        return load_data_from_url()
    else:
        return load_data_from_local()

def count_goals(scorer_str):
    """
    득점 수 계산
    - '0' : 경기는 했으나 득점 없음 (0 반환)
    - 빈 값 ('') : 경기 참여 안 함 (None 반환)
    - 그 외 : 득점자 수 카운트
    """
    if pd.isna(scorer_str): return None
    s_str = str(scorer_str).strip()
    
    # ⚠️ 빈 값인 경우 미참여로 간주
    if s_str == '':
        return None
        
    # '0'인 경우 참여했으나 무득점으로 간주
    if s_str in ['0', '0.0']:
        return 0
        
    scorers = [s.strip() for s in s_str.split(',')]
    return len([s for s in scorers if s])

def get_scorers_list(scorer_str):
    """득점자 리스트 생성 (자살골/무의미한 데이터 제외)"""
    if pd.isna(scorer_str): return []
    s_str = str(scorer_str).strip()
    if s_str in ['0', '0.0', '']: return []
    scorers = [s.strip() for s in s_str.split(',')]
    return [s for s in scorers if s and '자살골' not in s and s not in ['0', '0.0']]

def process_match_results(df_match):
    """경기 결과 분석 (풀네임 대응)"""
    # 1. 시트에서 실제 팀 컬럼 정식 명칭 찾기 (레드, 블루, 옐로 키워드 기준)
    teams = []
    for col in df_match.columns:
        if any(keyword in str(col) for keyword in ['레드', '블루', '옐로']):
            teams.append(col)
    
    # 2. 통계 초기화
    team_stats = {t: {'Points': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Played': 0} for t in teams}
    history_records = []
    player_stats = {}

    # 3. 라운드별 처리
    for idx, row in df_match.iterrows():
        week = row['주차']
        scores = {}
        participating = []
        
        # 각 팀의 득점 파싱 (우선 데이터가 있는 팀만 분류)
        for team in teams:
            val = row[team]
            goals = count_goals(val)
            if goals is not None:
                scores[team] = goals
                participating.append(team)
        
        # ⚠️ 최소 2개 팀 이상 참여해야 유효한 경기로 인정
        if len(participating) < 2: 
            continue
            
        # 유효한 경기인 경우에만 통계 산출 시작
        for team in participating:
            goals = scores[team]
            # 팀 득점 누적
            team_stats[team]['GF'] += goals
            
            # 선수 득점 누적 (자살골 제외 리스트 사용)
            for p in get_scorers_list(row[team]):
                player_stats[p] = player_stats.get(p, 0) + 1
            
            # 승무패 및 실점 판별
            opponents = [scores[t] for t in participating if t != team]
            max_opp = max(opponents) if opponents else 0
            
            team_stats[team]['GA'] += sum(opponents)
            team_stats[team]['Played'] += 1
            
            p_gained = 0
            if goals > max_opp:
                team_stats[team]['W'] += 1
                team_stats[team]['Points'] += 3
                p_gained = 3
            elif goals == max_opp:
                team_stats[team]['D'] += 1
                team_stats[team]['Points'] += 1
                p_gained = 1
            else:
                team_stats[team]['L'] += 1
            
            history_records.append({'Week': week, 'Team': team, 'PointsGained': p_gained})

    # 4. 결과 정리
    df_teams = pd.DataFrame(team_stats).T.reset_index().rename(columns={'index': 'Team'})
    df_teams['GD'] = df_teams['GF'] - df_teams['GA']
    df_teams = df_teams.sort_values(by=['Points', 'GD', 'GF'], ascending=False).reset_index(drop=True)
    df_teams.index += 1
    
    return df_teams, pd.DataFrame(history_records), pd.DataFrame(list(player_stats.items()), columns=['Player', 'Goals'])

def process_attendance(df_att):
    """출석 데이터 분석 (원본 이름 유지)"""
    # 주차 컬럼 식별
    week_cols = [c for c in df_att.columns if '주차' in c]
    
    # 데이터 구조 변환
    df_melt = df_att.melt(id_vars=['팀이름', '선수이름'], value_vars=week_cols, var_name='WeekName', value_name='Attended')
    df_melt['Attended'] = df_melt['Attended'].fillna(0)
    
    def check_att(val):
        try:
            if float(val) > 0: return 1
        except:
            if str(val).strip() != '': return 1
        return 0
        
    df_melt['IsAttended'] = df_melt['Attended'].apply(check_att)
    df_melt['WeekNum'] = df_melt['WeekName'].str.extract(r'(\d+)').astype(int)
    return df_melt
