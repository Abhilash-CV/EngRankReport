import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="KEAM Engineering Rank Generator",
    layout="wide"
)

st.title("KEAM Engineering Rank List Generator")

# -------------------------------------------------
# Helper function to handle column name variations
# -------------------------------------------------

def get_column(df, possible_names):
    """Find a column by trying multiple possible names"""
    for name in possible_names:
        if name in df.columns:
            return name
    return None

# -------------------------------------------------
# Upload Files
# -------------------------------------------------

mark_file = st.file_uploader(
    "markinputs.xlsx",
    type=["xlsx"]
)

subject_details_file = st.file_uploader(
    "subjectdetails.xlsx (SQL Query Export)",
    type=["xlsx"]
)

entrance_file = st.file_uploader(
    "tblEnggNormCandSubMarks.xlsx",
    type=["xlsx"]
)

candidate_file = st.file_uploader(
    "candidates.xlsx",
    type=["xlsx"]
)
subject_file = st.file_uploader(
    "tblCandSubMarks.xlsx",
    type=["xlsx"]
)

# -------------------------------------------------
# Generate Ranklist
# -------------------------------------------------

if all([
    mark_file,
    subject_details_file,
    entrance_file,
    candidate_file,
    subject_file
]):

    try:
        marks = pd.read_excel(mark_file)
        subject_details = pd.read_excel(subject_details_file)
        entrance = pd.read_excel(entrance_file)
        candidates = pd.read_excel(candidate_file)
        submarks = pd.read_excel(subject_file)
        
        # Display column names for debugging
        st.subheader("Data Loaded - Column Names")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write("**Marks Columns:**", list(marks.columns))
        with col2:
            st.write("**Subject Details Columns:**", list(subject_details.columns))
        with col3:
            st.write("**Entrance Columns:**", list(entrance.columns))
        with col4:
            st.write("**Candidates Columns:**", list(candidates.columns))
        with col5:
            st.write("**Submarks Columns:**", list(submarks.columns))
        
        # Find key columns with possible name variations
        appl_no_col = get_column(marks, ['APPLNO', 'ApplicationNo', 'APPLNO', 'Application Number'])
        board_col = get_column(marks, ['BOARD', 'Board'])
        
        # Year columns - per subject
        maths_year_col = get_column(marks, ['MATHS_YEAR', 'Maths_Year'])
        phy_year_col = get_column(marks, ['PHY_YEAR', 'Phy_Year'])
        che_year_col = get_column(marks, ['CHE_YEAR', 'Che_Year'])
        
        # Mark columns
        maths_col = get_column(marks, ['MATHS_MARK', 'Maths_Mark', 'MATHS', 'Maths'])
        phy_col = get_column(marks, ['PHY_MARK', 'Phy_Mark', 'PHYSICS', 'Physics'])
        che_col = get_column(marks, ['CHE_MARK', 'Che_Mark', 'CHEMISTRY', 'Chemistry'])
        
        # Check if required columns exist
        if appl_no_col is None:
            st.error("❌ 'ApplNo' column not found in marks file. Available columns: " + ", ".join(marks.columns))
            st.stop()
        
        if board_col is None:
            st.error("❌ 'BOARD' column not found in marks file. Available columns: " + ", ".join(marks.columns))
            st.stop()
        
        if maths_col is None:
            st.error("❌ 'MATHS_MARK' column not found in marks file")
            st.stop()
        
        if phy_col is None:
            st.error("❌ 'PHY_MARK' column not found in marks file")
            st.stop()
        
        if che_col is None:
            st.error("❌ 'CHE_MARK' column not found in marks file")
            st.stop()
        
        # Rename columns to standard names
        marks = marks.rename(columns={
            appl_no_col: 'ApplNo',
            board_col: 'BOARD',
        })
        
        # Handle year columns
        if maths_year_col:
            marks = marks.rename(columns={maths_year_col: 'MATHS_YEAR'})
        if phy_year_col:
            marks = marks.rename(columns={phy_year_col: 'PHY_YEAR'})
        if che_year_col:
            marks = marks.rename(columns={che_year_col: 'CHE_YEAR'})
        
        # Handle mark columns
        if maths_col and maths_col != 'MATHS_MARK':
            marks = marks.rename(columns={maths_col: 'MATHS_MARK'})
        if phy_col and phy_col != 'PHY_MARK':
            marks = marks.rename(columns={phy_col: 'PHY_MARK'})
        if che_col and che_col != 'CHE_MARK':
            marks = marks.rename(columns={che_col: 'CHE_MARK'})
        
        # Create YEARPASS column (use the year from any subject, assuming they're the same)
        if 'MATHS_YEAR' in marks.columns:
            marks['YEARPASS'] = marks['MATHS_YEAR']
        elif 'PHY_YEAR' in marks.columns:
            marks['YEARPASS'] = marks['PHY_YEAR']
        elif 'CHE_YEAR' in marks.columns:
            marks['YEARPASS'] = marks['CHE_YEAR']
        else:
            st.error("❌ No year column found in marks file")
            st.stop()
        
        # Remove duplicate application records
        marks = marks.drop_duplicates(
            subset=["ApplNo"],
            keep="first"
        )
        
        # Find candidate columns
        cand_appl_col = get_column(candidates, ['ApplNo', 'ApplicationNo', 'APPLNO'])
        cand_roll_col = get_column(candidates, ['RollNo', 'Roll_No', 'ROLLNO'])
        cand_name_col = get_column(candidates, ['Name', 'NAME', 'CandidateName'])
        cand_dob_col = get_column(candidates, ['DOB', 'DateOfBirth', 'DOB'])
        cand_gender_col = get_column(candidates, ['Gender', 'GENDER', 'Sex'])
        cand_district_col = get_column(candidates, ['District', 'DISTRICT', 'Dist'])
        
        if cand_appl_col is None:
            st.error("❌ 'ApplNo' column not found in candidates file")
            st.stop()
        
        # Rename candidate columns
        candidates = candidates.rename(columns={cand_appl_col: 'ApplNo'})
        if cand_roll_col:
            candidates = candidates.rename(columns={cand_roll_col: 'RollNo'})
        if cand_name_col:
            candidates = candidates.rename(columns={cand_name_col: 'Name'})
        if cand_dob_col:
            candidates = candidates.rename(columns={cand_dob_col: 'DOB'})
        if cand_gender_col:
            candidates = candidates.rename(columns={cand_gender_col: 'Gender'})
        if cand_district_col:
            candidates = candidates.rename(columns={cand_district_col: 'District'})
        
        # Remove duplicate candidate records
        candidates = candidates.drop_duplicates(
            subset=["ApplNo"],
            keep="first"
        )
        
        # Find entrance columns
        ent_roll_col = get_column(entrance, ['RollNo', 'Roll_No', 'ROLLNO'])
        ent_norm_col = get_column(entrance, ['Norm_Score', 'NormScore', 'NORM_SCORE'])
        
        if ent_roll_col is None:
            st.error("❌ 'RollNo' column not found in entrance file")
            st.stop()
        
        entrance = entrance.rename(columns={ent_roll_col: 'RollNo'})
        if ent_norm_col:
            entrance = entrance.rename(columns={ent_norm_col: 'Norm_Score'})
        
        # Remove duplicate entrance records
        entrance = entrance.drop_duplicates(
            subset=["RollNo"],
            keep="first"
        )
        
        # Find submarks columns
        sub_roll_col = get_column(submarks, ['intRollNo', 'RollNo', 'ROLLNO'])
        sub_subject_col = get_column(submarks, ['intSubjectID', 'SubjectID', 'SUBJECTID'])
        sub_corr_col = get_column(submarks, ['decSubTotCorr', 'SubTotCorr', 'DECSUBTOTCORR'])
        sub_count_col = get_column(submarks, ['intCount', 'Count', 'INTCOUNT'])
        
        if sub_roll_col is None:
            st.error("❌ 'intRollNo' column not found in submarks file")
            st.stop()
        
        submarks = submarks.rename(columns={
            sub_roll_col: 'intRollNo',
            sub_subject_col: 'intSubjectID' if sub_subject_col else 'intSubjectID',
            sub_corr_col: 'decSubTotCorr' if sub_corr_col else 'decSubTotCorr',
            sub_count_col: 'intCount' if sub_count_col else 'intCount'
        })

        st.success("✅ All files loaded and validated successfully")
        
    except Exception as e:
        st.error(f"❌ Error loading files: {str(e)}")
        st.stop()
    
    # -------------------------------------------------
    # Maximum Marks from Subject Details (SQL Export)
    # -------------------------------------------------
    
    # Display the loaded subject details
    st.subheader("Subject Details (from SQL Export)")
    st.dataframe(subject_details, use_container_width=True)
    
    # Find subject details columns
    sd_board_col = get_column(subject_details, ['BOARD', 'Board'])
    sd_year_col = get_column(subject_details, ['SUBYEAR', 'Year', 'YEAR'])
    sd_subject_col = get_column(subject_details, ['SUBCODE', 'Subject', 'SUBJECT'])
    sd_max_col = get_column(subject_details, ['SUBMAXMARK', 'MaxMark', 'MAXMARK'])
    
    if sd_board_col is None or sd_year_col is None or sd_subject_col is None or sd_max_col is None:
        st.error("❌ Subject details file missing required columns")
        st.write("Required columns: BOARD, SUBYEAR, SUBCODE, SUBMAXMARK")
        st.write("Available columns:", list(subject_details.columns))
        st.stop()
    
    subject_details = subject_details.rename(columns={
        sd_board_col: 'BOARD',
        sd_year_col: 'SUBYEAR',
        sd_subject_col: 'SUBCODE',
        sd_max_col: 'SUBMAXMARK'
    })
    
    # Create a dictionary to store max marks for each board, year, and subject
    max_marks_dict = {}
    
    for _, row in subject_details.iterrows():
        board = row['BOARD']
        year = row['SUBYEAR']
        subject = row['SUBCODE']
        max_mark = row['SUBMAXMARK']
        
        if board not in max_marks_dict:
            max_marks_dict[board] = {}
        if year not in max_marks_dict[board]:
            max_marks_dict[board][year] = {}
        
        max_marks_dict[board][year][subject] = max_mark
    
    # Function to get max mark for a specific board, year, and subject
    def get_max_mark(board, year, subject):
        try:
            return max_marks_dict[board][year][subject]
        except KeyError:
            return np.nan
    
    # Apply max marks to the dataframe
    df = marks.copy()
    
    # Add columns for maximum marks
    df['MATMAXMARK'] = df.apply(
        lambda row: get_max_mark(row['BOARD'], row['YEARPASS'], 'MT'), 
        axis=1
    )
    df['PHYMAXMARK'] = df.apply(
        lambda row: get_max_mark(row['BOARD'], row['YEARPASS'], 'PH'), 
        axis=1
    )
    df['CHEMAXMARK'] = df.apply(
        lambda row: get_max_mark(row['BOARD'], row['YEARPASS'], 'CH'), 
        axis=1
    )
    
    missing_max = df[
        (df["MATMAXMARK"].isna()) | 
        (df["PHYMAXMARK"].isna()) | 
        (df["CHEMAXMARK"].isna())
    ]
    
    if len(missing_max) > 0:
        st.error(
            f"⚠️ Missing board/year maximum marks for {len(missing_max)} candidates"
        )
        st.write("**Candidates with missing maximum marks:**")
        st.dataframe(
            missing_max[
                ["ApplNo", "BOARD", "YEARPASS"]
            ],
            use_container_width=True
        )
        
        # Show available max marks for reference
        st.subheader("Available Maximum Marks in Database")
        pivot_max_marks = subject_details.pivot_table(
            index=['BOARD', 'SUBYEAR'],
            columns='SUBCODE',
            values='SUBMAXMARK'
        ).reset_index()
        st.dataframe(pivot_max_marks, use_container_width=True)
        
        # List unique board-year combinations in marks
        st.subheader("Board-Year Combinations in Candidate Data")
        marks_combos = df[['BOARD', 'YEARPASS']].drop_duplicates().sort_values(['BOARD', 'YEARPASS'])
        st.dataframe(marks_combos, use_container_width=True)
        
        # Show sample of the subject details for debugging
        st.subheader("Subject Details Data (for debugging)")
        st.dataframe(subject_details, use_container_width=True)
        
        st.stop()
    
    # Display the max marks being used
    st.subheader("Maximum Marks Configuration Applied")
    pivot_max_marks = subject_details.pivot_table(
        index=['BOARD', 'SUBYEAR'],
        columns='SUBCODE',
        values='SUBMAXMARK'
    ).reset_index()
    st.dataframe(pivot_max_marks, use_container_width=True)
    
    # -----------------------------------
    # Subject Wise Entrance Details
    # -----------------------------------

    # Check if required columns exist in submarks
    if 'intSubjectID' not in submarks.columns:
        st.error("❌ 'intSubjectID' column not found in submarks file")
        st.stop()
    
    physics = (
        submarks[submarks["intSubjectID"] == 1]
        [["intRollNo","decSubTotCorr","intCount"]]
        .rename(
            columns={
                "intRollNo":"RollNo",
                "decSubTotCorr":"PhysicsEntranceRaw",
                "intCount":"PhysicsCorrect"
            }
        )
        .groupby("RollNo", as_index=False)
        .agg({
            "PhysicsEntranceRaw":"max",
            "PhysicsCorrect":"max"
        })
    )
    
    maths = (
        submarks[submarks["intSubjectID"] == 3]
        [["intRollNo","decSubTotCorr","intCount"]]
        .rename(
            columns={
                "intRollNo":"RollNo",
                "decSubTotCorr":"MathsEntranceRaw",
                "intCount":"MathsCorrect"
            }
        )
        .groupby("RollNo", as_index=False)
        .agg({
            "MathsEntranceRaw":"max",
            "MathsCorrect":"max"
        })
    )
    
    # -------------------------------------------------
    # KEAM Normalization Formula
    # -------------------------------------------------

    df["NormMath"] = (
        100 * df["MATHS_MARK"]
    ) / df["MATMAXMARK"]

    df["NormPhy"] = (
        100 * df["PHY_MARK"]
    ) / df["PHYMAXMARK"]

    df["NormChem"] = (
        100 * df["CHE_MARK"]
    ) / df["CHEMAXMARK"]

    # -------------------------------------------------
    # Weightage 5:3:2
    # -------------------------------------------------

    df["MathWeighted"] = (
        df["NormMath"] * 150 / 100
    )

    df["PhyWeighted"] = (
        df["NormPhy"] * 90 / 100
    )

    df["ChemWeighted"] = (
        df["NormChem"] * 60 / 100
    )

    df["PlusTwoScore"] = (
        df["MathWeighted"] +
        df["PhyWeighted"] +
        df["ChemWeighted"]
    )

    # -------------------------------------------------
    # Candidate Details
    # -------------------------------------------------

    # Prepare candidate columns for merge
    candidate_cols = ["ApplNo"]
    if "RollNo" in candidates.columns:
        candidate_cols.append("RollNo")
    if "Name" in candidates.columns:
        candidate_cols.append("Name")
    if "DOB" in candidates.columns:
        candidate_cols.append("DOB")
    if "Gender" in candidates.columns:
        candidate_cols.append("Gender")
    if "District" in candidates.columns:
        candidate_cols.append("District")
    
    df = pd.merge(
        df,
        candidates[candidate_cols],
        on="ApplNo",
        how="left"
    )
    
    missing_roll = df[df["RollNo"].isna()]

    if len(missing_roll) > 0:
        st.error(
            f"{len(missing_roll)} candidates have no Roll Number"
        )
        st.dataframe(
            missing_roll[
                ["ApplNo","Name"]
            ] if "Name" in missing_roll.columns else missing_roll[["ApplNo"]]
        )
        st.stop()
    
    # Maths Tie Break
    df = pd.merge(
        df,
        maths,
        on="RollNo",
        how="left"
    )
    
    # Physics Tie Break
    df = pd.merge(
        df,
        physics,
        on="RollNo",
        how="left"
    )
    
    # Entrance Score
    df = pd.merge(
        df,
        entrance,
        on="RollNo",
        how="left"
    )
    
    missing_norm = df[
        df["Norm_Score"].isna()
    ]
    
    if len(missing_norm) > 0:
        st.warning(
            f"{len(missing_norm)} candidates missing entrance score"
        )
    
    df["Norm_Score"] = pd.to_numeric(
        df["Norm_Score"],
        errors="coerce"
    ).fillna(0)

    # -------------------------------------------------
    # Final Index Mark
    # -------------------------------------------------

    df["IndexMark"] = (
        df["PlusTwoScore"] +
        df["Norm_Score"]
    )

    # -------------------------------------------------
    # Rounding
    # -------------------------------------------------

    df["NormMath"] = df["NormMath"].round(4)
    df["NormPhy"] = df["NormPhy"].round(4)
    df["NormChem"] = df["NormChem"].round(4)

    df["PlusTwoScore"] = (
        df["PlusTwoScore"]
        .round(4)
    )

    df["IndexMark"] = (
        df["IndexMark"]
        .round(4)
    )

    # -------------------------------------------------
    # DOB
    # -------------------------------------------------

    if "DOB" in df.columns:
        df["DOB"] = pd.to_datetime(
            df["DOB"],
            errors="coerce"
        )

    # -------------------------------------------------
    # Official KEAM Tie Resolution
    # -------------------------------------------------

    required_columns = [
        "MathsEntranceRaw",
        "PhysicsEntranceRaw",
        "MathsCorrect",
        "PhysicsCorrect"
    ]

    for col in required_columns:
        if col not in df.columns:
            df[col] = 0

    st.write("Total Candidates:", len(df))

    # Sort with tie-breakers
    sort_columns = ["IndexMark", "MathsEntranceRaw", "PhysicsEntranceRaw", "NormMath", "NormPhy", "MathsCorrect", "PhysicsCorrect"]
    if "DOB" in df.columns:
        sort_columns.append("DOB")
    
    sort_ascending = [False, False, False, False, False, False, False]
    if "DOB" in df.columns:
        sort_ascending.append(True)  # Older candidate first
    
    df = df.sort_values(
        by=sort_columns,
        ascending=sort_ascending
    )
    
    df = df.drop_duplicates(
        subset=["ApplNo"],
        keep="first"
    )
    
    # -------------------------------------------------
    # Rank
    # -------------------------------------------------

    df["ERank"] = range(
        1,
        len(df) + 1
    )

    # -------------------------------------------------
    # Output - Main Rank List
    # -------------------------------------------------

    result_columns = ["ERank", "ApplNo", "RollNo", "BOARD", "YEARPASS", "NormMath", "NormPhy", "NormChem", "PlusTwoScore", "Norm_Score", "IndexMark"]
    if "Name" in df.columns:
        result_columns.insert(3, "Name")
    
    result = df[result_columns]

    st.subheader("Engineering Rank List")

    st.dataframe(
        result,
        use_container_width=True,
        height=700
    )

    st.metric(
        "Candidates Ranked",
        len(result)
    )

    # -------------------------------------------------
    # DETAILED REPORTS SECTION
    # -------------------------------------------------
    
    st.header("📊 Detailed Statistical Reports")
    
    # Create tabs for different reports
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Gender Distribution", 
        "District-wise Analysis", 
        "Board-wise Performance",
        "Tie Candidates Report",
        "Top Rank Analysis",
        "Score Distribution"
    ])
    
    # --------------------------------------------------------------------
    # TAB 1: Gender Distribution
    # --------------------------------------------------------------------
    with tab1:
        st.subheader("Gender Distribution Report")
        
        # Overall gender statistics
        gender_counts = df['Gender'].value_counts()
        gender_total = len(df)
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Update gender labels based on your data
        female_count = df[df['Gender'].str.upper().str.contains('F|FEMALE', na=False)].shape[0]
        male_count = df[df['Gender'].str.upper().str.contains('M|MALE', na=False)].shape[0]
        trans_count = df[df['Gender'].str.upper().str.contains('T|TRANS|OTHER', na=False)].shape[0]
        
        with col1:
            st.metric("Total Candidates", gender_total)
        with col2:
            st.metric("Female", female_count, f"{(female_count/gender_total*100):.1f}%")
        with col3:
            st.metric("Male", male_count, f"{(male_count/gender_total*100):.1f}%")
        with col4:
            st.metric("Transgender", trans_count, f"{(trans_count/gender_total*100):.1f}%")
        
        # Gender distribution in Top 100
        top_100 = df.head(100)
        top100_female = top_100[top_100['Gender'].str.upper().str.contains('F|FEMALE', na=False)].shape[0]
        top100_male = top_100[top_100['Gender'].str.upper().str.contains('M|MALE', na=False)].shape[0]
        top100_trans = top_100[top_100['Gender'].str.upper().str.contains('T|TRANS|OTHER', na=False)].shape[0]
        
        st.subheader("Top 100 Gender Distribution")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Female in Top 100", top100_female, f"{(top100_female/100*100):.1f}%")
        with col2:
            st.metric("Male in Top 100", top100_male, f"{(top100_male/100*100):.1f}%")
        with col3:
            st.metric("Transgender in Top 100", top100_trans, f"{(top100_trans/100*100):.1f}%")
        
        # Gender distribution in Top 1000
        top_1000 = df.head(1000)
        top1000_female = top_1000[top_1000['Gender'].str.upper().str.contains('F|FEMALE', na=False)].shape[0]
        top1000_male = top_1000[top_1000['Gender'].str.upper().str.contains('M|MALE', na=False)].shape[0]
        top1000_trans = top_1000[top_1000['Gender'].str.upper().str.contains('T|TRANS|OTHER', na=False)].shape[0]
        
        st.subheader("Top 1000 Gender Distribution")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Female in Top 1000", top1000_female, f"{(top1000_female/1000*100):.1f}%")
        with col2:
            st.metric("Male in Top 1000", top1000_male, f"{(top1000_male/1000*100):.1f}%")
        with col3:
            st.metric("Transgender in Top 1000", top1000_trans, f"{(top1000_trans/1000*100):.1f}%")
        
        # Summary table
        gender_summary = pd.DataFrame({
            'Category': ['Total', 'Top 100', 'Top 1000'],
            'Female': [female_count, top100_female, top1000_female],
            'Male': [male_count, top100_male, top1000_male],
            'Transgender': [trans_count, top100_trans, top1000_trans],
            'Total': [gender_total, 100, 1000]
        })
        st.dataframe(gender_summary, use_container_width=True)
        
        # Gender percentage chart (using simple text-based visualization)
        st.subheader("Gender Distribution Visualization")
        st.write("**Overall Distribution:**")
        st.progress(female_count/gender_total, text=f"Female: {female_count/gender_total*100:.1f}%")
        st.progress(male_count/gender_total, text=f"Male: {male_count/gender_total*100:.1f}%")
        if trans_count > 0:
            st.progress(trans_count/gender_total, text=f"Transgender: {trans_count/gender_total*100:.1f}%")
    
    # --------------------------------------------------------------------
    # TAB 2: District-wise Analysis
    # --------------------------------------------------------------------
    with tab2:
        st.subheader("District-wise Analysis Report")
        
        # Check if district column exists in candidates data
        if 'District' in candidates.columns:
            # Merge district info
            df_district = pd.merge(
                df,
                candidates[['ApplNo', 'District']],
                on='ApplNo',
                how='left'
            )
            
            # District-wise distribution
            district_stats = df_district.groupby('District').agg({
                'ERank': 'count',
                'IndexMark': 'mean'
            }).reset_index()
            district_stats.columns = ['District', 'Total Candidates', 'Avg Index Mark']
            district_stats = district_stats.sort_values('Total Candidates', ascending=False)
            
            st.dataframe(district_stats, use_container_width=True)
            
            # Top districts in Top 100
            top_100_dist = df_district.head(100)
            top_districts = top_100_dist['District'].value_counts().head(10)
            
            st.subheader("Top 10 Districts in Top 100")
            st.dataframe(
                pd.DataFrame({
                    'District': top_districts.index,
                    'Candidates in Top 100': top_districts.values,
                    'Percentage': (top_districts.values / 100 * 100).round(1)
                }),
                use_container_width=True
            )
            
            # Top districts in Top 1000
            top_1000_dist = df_district.head(1000)
            top_districts_1000 = top_1000_dist['District'].value_counts().head(10)
            
            st.subheader("Top 10 Districts in Top 1000")
            st.dataframe(
                pd.DataFrame({
                    'District': top_districts_1000.index,
                    'Candidates in Top 1000': top_districts_1000.values,
                    'Percentage': (top_districts_1000.values / 1000 * 100).round(1)
                }),
                use_container_width=True
            )
            
            # District-wise gender distribution
            st.subheader("District-wise Gender Distribution")
            district_gender = pd.crosstab(
                df_district['District'], 
                df_district['Gender']
            ).reset_index()
            st.dataframe(district_gender, use_container_width=True)
            
        else:
            st.warning("District information not available in candidate data")
    
    # --------------------------------------------------------------------
    # TAB 3: Board-wise Performance
    # --------------------------------------------------------------------
    with tab3:
        st.subheader("Board-wise Performance Report")
        
        # Board-wise distribution
        board_stats = df.groupby('BOARD').agg({
            'ERank': 'count',
            'IndexMark': ['mean', 'min', 'max'],
            'ERank': ['min', 'max']
        }).reset_index()
        
        board_stats.columns = ['Board', 'Total', 'Avg Index', 'Min Index', 'Max Index', 'Best Rank', 'Worst Rank']
        board_stats = board_stats.sort_values('Total', ascending=False)
        
        st.dataframe(board_stats, use_container_width=True)
        
        # Board-wise Top 100 representation
        top_100 = df.head(100)
        board_100 = top_100['BOARD'].value_counts().reset_index()
        board_100.columns = ['Board', 'Candidates in Top 100']
        board_100['Percentage'] = (board_100['Candidates in Top 100'] / 100 * 100).round(1)
        
        st.subheader("Board-wise Representation in Top 100")
        st.dataframe(board_100, use_container_width=True)
        
        # Board-wise Top 5000 representation
        top_5000 = df.head(5000)
        board_5000 = top_5000['BOARD'].value_counts().reset_index()
        board_5000.columns = ['Board', 'Candidates in Top 5000']
        board_5000['Percentage'] = (board_5000['Candidates in Top 5000'] / 5000 * 100).round(1)
        
        st.subheader("Board-wise Representation in Top 5000")
        st.dataframe(board_5000, use_container_width=True)
    
    # --------------------------------------------------------------------
    # TAB 4: Tie Candidates Report
    # --------------------------------------------------------------------
    with tab4:
        st.subheader("Tie Candidates Analysis Report")
        
        # Find candidates with same IndexMark
        tied_marks = df.groupby('IndexMark').filter(lambda x: len(x) > 1)
        
        if len(tied_marks) > 0:
            st.metric("Total Candidates Involved in Ties", len(tied_marks))
            
            # Group by IndexMark to show tie groups
            tie_groups = tied_marks.groupby('IndexMark').agg({
                'ERank': lambda x: list(x),
                'ApplNo': 'count',
                'Name': lambda x: ', '.join(x.head(5)) + ('...' if len(x) > 5 else '')
            }).reset_index()
            tie_groups.columns = ['Index Mark', 'Ranks', 'Count', 'Sample Candidates']
            tie_groups = tie_groups.sort_values('Count', ascending=False)
            
            st.subheader("Tie Groups by Index Mark")
            st.dataframe(tie_groups, use_container_width=True)
            
            # Show detailed tie-breaker information for the largest tie groups
            if len(tie_groups) > 0:
                st.subheader("Detailed Tie-breaker Analysis (Largest Tie Groups)")
                
                largest_tie = tie_groups.head(5)['Index Mark'].values
                for mark in largest_tie:
                    tie_candidates = df[df['IndexMark'] == mark][
                        ['ERank', 'RollNo', 'Name', 'MathsEntranceRaw', 
                         'PhysicsEntranceRaw', 'NormMath', 'NormPhy', 'DOB']
                    ].sort_values(['MathsEntranceRaw', 'PhysicsEntranceRaw'], ascending=False)
                    
                    st.write(f"**Index Mark: {mark}** ({len(tie_candidates)} candidates)")
                    st.dataframe(tie_candidates, use_container_width=True)
            
            # Summary of tie resolution
            st.subheader("Tie Resolution Summary")
            tie_summary = pd.DataFrame({
                'Metric': ['Total Candidates', 'Candidates in Ties', 'Percentage in Ties'],
                'Value': [
                    len(df),
                    len(tied_marks),
                    f"{len(tied_marks)/len(df)*100:.2f}%"
                ]
            })
            st.dataframe(tie_summary, use_container_width=True)
            
        else:
            st.info("No ties found in the rank list")
    
    # --------------------------------------------------------------------
    # TAB 5: Top Rank Analysis
    # --------------------------------------------------------------------
    with tab5:
        st.subheader("Top 100 Candidates Analysis")
        
        top_100 = df.head(100)
        
        # Top 100 statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Average Index Mark", f"{top_100['IndexMark'].mean():.2f}")
        with col2:
            st.metric("Highest Index Mark", f"{top_100['IndexMark'].max():.2f}")
        with col3:
            st.metric("Lowest Index Mark in Top 100", f"{top_100['IndexMark'].min():.2f}")
        with col4:
            st.metric("Std Dev", f"{top_100['IndexMark'].std():.2f}")
        
        # Top 100 candidates list
        st.subheader("Top 100 Candidates")
        st.dataframe(
            top_100[['ERank', 'Name', 'BOARD', 'PlusTwoScore', 'Norm_Score', 'IndexMark']],
            use_container_width=True,
            height=400
        )
        
        # Attempt distribution (if data available)
        if 'Attempt' in candidates.columns:
            attempt_counts = top_100['Attempt'].value_counts().reset_index()
            attempt_counts.columns = ['Attempt Number', 'Candidates']
            st.subheader("Attempt Distribution in Top 100")
            st.dataframe(attempt_counts, use_container_width=True)
        
        # Top district distribution in top 100
        if 'District' in candidates.columns:
            df_top100 = pd.merge(
                top_100,
                candidates[['ApplNo', 'District']],
                on='ApplNo',
                how='left'
            )
            top_districts = df_top100['District'].value_counts().head(5)
            st.subheader("Top 5 Districts in Top 100")
            st.dataframe(
                pd.DataFrame({
                    'District': top_districts.index,
                    'Count': top_districts.values
                }),
                use_container_width=True
            )
    
    # --------------------------------------------------------------------
    # TAB 6: Score Distribution
    # --------------------------------------------------------------------
    with tab6:
        st.subheader("Score Distribution Analysis")
        
        # Create score ranges
        score_ranges = pd.cut(
            df['IndexMark'], 
            bins=20,
            labels=[f"{int(i)}-{int(i+30)}" for i in range(0, 600, 30)]
        )
        score_dist = score_ranges.value_counts().reset_index()
        score_dist.columns = ['Score Range', 'Candidates']
        score_dist = score_dist.sort_values('Score Range')
        
        st.subheader("Distribution of Index Marks")
        st.dataframe(score_dist, use_container_width=True)
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mean Index Mark", f"{df['IndexMark'].mean():.2f}")
        with col2:
            st.metric("Median Index Mark", f"{df['IndexMark'].median():.2f}")
        with col3:
            st.metric("Std Deviation", f"{df['IndexMark'].std():.2f}")
        with col4:
            st.metric("Range", f"{df['IndexMark'].min():.2f} - {df['IndexMark'].max():.2f}")
        
        # Percentile distribution
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        percentile_values = df['IndexMark'].quantile([p/100 for p in percentiles])
        
        percentile_df = pd.DataFrame({
            'Percentile': [f"{p}th" for p in percentiles],
            'Index Mark': percentile_values.values
        })
        
        st.subheader("Percentile Distribution")
        st.dataframe(percentile_df, use_container_width=True)
        
        # PlusTwo vs Entrance score distribution
        st.subheader("Plus Two vs Entrance Score Distribution")
        
        # Create score categories
        df['Score_Category'] = pd.cut(
            df['IndexMark'],
            bins=[0, 200, 300, 400, 500, 600],
            labels=['0-200', '200-300', '300-400', '400-500', '500-600']
        )
        
        category_stats = df.groupby('Score_Category').agg({
            'ERank': 'count',
            'PlusTwoScore': 'mean',
            'Norm_Score': 'mean'
        }).reset_index()
        category_stats.columns = ['Score Range', 'Count', 'Avg Plus Two', 'Avg Entrance']
        
        st.dataframe(category_stats, use_container_width=True)

    # -------------------------------------------------
    # Export all reports as CSV
    # -------------------------------------------------
    
    st.subheader("📥 Export Reports")
    
    # Create a dictionary of all report dataframes
    reports = {
        'Full_Rank_List': result,
        'Gender_Distribution': gender_summary if 'gender_summary' in locals() else pd.DataFrame(),
        'Board_Statistics': board_stats if 'board_stats' in locals() else pd.DataFrame(),
        'Tie_Candidates': tied_marks[['ERank', 'RollNo', 'Name', 'IndexMark', 'MathsEntranceRaw', 'PhysicsEntranceRaw']] if 'tied_marks' in locals() and len(tied_marks) > 0 else pd.DataFrame(),
        'Top_100': top_100[['ERank', 'Name', 'BOARD', 'PlusTwoScore', 'Norm_Score', 'IndexMark']] if 'top_100' in locals() else pd.DataFrame(),
        'Score_Distribution': score_dist if 'score_dist' in locals() else pd.DataFrame()
    }
    
    # Create a zip file with all reports
    import io
    import zipfile
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for report_name, report_df in reports.items():
            if len(report_df) > 0:
                csv_data = report_df.to_csv(index=False).encode('utf-8')
                zip_file.writestr(f"{report_name}.csv", csv_data)
    
    zip_buffer.seek(0)
    
    st.download_button(
        label="📦 Download All Reports (ZIP)",
        data=zip_buffer,
        file_name="KEAM_Reports.zip",
        mime="application/zip"
    )
    
    # Individual report downloads
    st.write("**Individual Report Downloads:**")
    col1, col2 = st.columns(2)
    
    with col1:
        # Download main rank list
        csv = result.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📄 Download Rank List (CSV)",
            data=csv,
            file_name="EngineeringRankList.csv",
            mime="text/csv"
        )
    
    with col2:
        # Download tie candidates report
        if 'tied_marks' in locals() and len(tied_marks) > 0:
            tie_csv = tied_marks[['ERank', 'RollNo', 'Name', 'IndexMark', 
                                  'MathsEntranceRaw', 'PhysicsEntranceRaw']].to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📄 Download Tie Report (CSV)",
                data=tie_csv,
                file_name="Tie_Candidates_Report.csv",
                mime="text/csv"
            )
    
    # -------------------------------------------------
    # Summary Dashboard
    # -------------------------------------------------
    
    st.header("📈 Quick Summary Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Ranked Candidates", len(df))
    with col2:
        st.metric("Top 100 Average Score", f"{df.head(100)['IndexMark'].mean():.2f}")
    with col3:
        st.metric("Highest Score", f"{df['IndexMark'].max():.2f}")
    with col4:
        st.metric("Tie Candidates", len(tied_marks) if 'tied_marks' in locals() else 0)

else:
    st.info("Please upload all required files to generate the rank list and reports")
