import pandas as pd


def load_data(filename):
    df = pd.read_excel(filename)
    return df

def clean_column_names(df):
    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace(' ', '_')
        .str.replace('/', '_')
        )

    return df

def filter_ukraine(df):
    ukraine_df = df[
        (df['country_iso'] == 'UKR') &
        (df['date'] >= '2022-02-24')
        ].copy()

    return ukraine_df


def clean_regions(ukraine_df):
    # Preserve raw geography and normalize text
    ukraine_df['region_clean'] = (
        ukraine_df['admin_1']
        .str.strip()
        .str.lower()
        )
    
    # QA columns
    ukraine_df['region_qa_status'] = 'ok'
    ukraine_df['region_qa_note'] = ''

    # Remember source-level unknown regions BEFORE replacement
    source_unknown_mask = (
        ukraine_df['region_clean'] == 'no information'
    )

    region_mapping = {
        'zaporizhzhia oblast': 'zaporizhia oblast',
        'oblast de kharkiv': 'kharkiv oblast',

        'khust raion': 'zakarpattia oblast',
        'zolochiv raion': 'lviv oblast',
        'beryslav raion': 'kherson oblast',
        'kherson raion': 'kherson oblast',
        'henichesk raion': 'kherson oblast',

        'pecherskyi': 'kyiv city',
        'pecherskyi district': 'kyiv city',
        'sviatoshynskyi district': 'kyiv city',
        'obolonskyi district': 'kyiv city',
        'holosiivskyi district': 'kyiv city',
        'podilskyi district': 'kyiv city',
        'darnytskyi district': 'kyiv city',
        'dniprovskyi district': 'kyiv city',
        'solomianskyi district': 'kyiv city',
        'desnianskyi district': 'kyiv city',

        'no information': 'unknown',

        'autonomous republic of crimea': 'crimea',
        'republic of crimea': 'crimea',
}
    ukraine_df['region_clean'] = (
        ukraine_df['region_clean']
        .replace(region_mapping)
        )

    
    ukraine_df.loc[
        source_unknown_mask,
        'region_qa_status'
        ] = 'review'
    ukraine_df.loc[
        source_unknown_mask,
        'region_qa_note'] = 'Region reported as No Information in source data.'

    # --------------------------------------------------------
    # Manually verified event-level corrections
    # --------------------------------------------------------

    # Incidents manually verified using external reporting, due to an ambigous Admin 1 value 
    region_corrections = {
        135045: 'kyiv city',
        134975: 'kyiv city',
        134980: 'kyiv city',
        134978: 'kyiv city',
        134977: 'kyiv city',
        134976: 'kyiv city',
        134979: 'kyiv city',
        134974: 'kyiv city',
        134973: 'kyiv city',
        134972: 'kyiv city',
        134971: 'kyiv city',
        134963: 'kyiv city',

        133301: 'kyiv city',
        133039: 'kharkiv oblast',

        124669: 'kyiv city',
        124726: 'kyiv city',
        124905: 'kyiv city',

        121116: 'kyiv city',
        120373: 'kyiv city',
        120376: 'kyiv city',

        113362: 'kyiv city',

        118835: 'kyiv city',
        118839: 'kyiv city',
        118841: 'kyiv city',

        115771: 'kharkiv oblast',
        118830: 'kharkiv oblast',

        45551: 'kyiv city',
        45552: 'kyiv city',
        45555: 'kyiv city',
        45556: 'kyiv city',
        45557: 'kyiv city',
        45559: 'kyiv city',

        84500: 'kharkiv oblast',
        39111: 'kyiv city',
        }

    ukraine_df['region_correction'] = (
        ukraine_df['sind_event_id']
        .map(region_corrections)
        )

    corrected_mask = (
        ukraine_df['region_correction'].notna()
        )

    ukraine_df.loc[
        corrected_mask,
        'region_clean'
        ] = ukraine_df.loc[
            corrected_mask,
            'region_correction'
            ]

    ukraine_df.loc[
        corrected_mask,
        'region_qa_status'
        ] = 'corrected'

    ukraine_df.loc[
        corrected_mask,
        'region_qa_note'
        ] = (
            'Region manually verified and corrected '
            'using external reporting.'
            )

    # --------------------------------------------------------
    # Handle unresolved Shevchenkivskyi District
    # --------------------------------------------------------

    ambiguous_mask = (
        ukraine_df["region_clean"]
        == "shevchenkivskyi district"
        )

    ukraine_df.loc[
        ambiguous_mask,
        "region_qa_status"
        ] = "review"

    ukraine_df.loc[
        ambiguous_mask,
        "region_qa_note"
        ] = (
            'Ambiguous Shevchenkivskyi district; '
            'city could not be reliably determined '
            'from the source data.'
            )
    
    ukraine_df.loc[
        ambiguous_mask,
        'region_clean'
        ] = 'unknown'
    
     # --------------------------------------------------------
     # Handle missing regions
     # --------------------------------------------------------

    missing_region_mask = (
        ukraine_df['region_clean'].isna()
    )

    ukraine_df.loc[
        missing_region_mask,
        'region_clean'
        ] = 'unknown'

    ukraine_df.loc[
        missing_region_mask,
        'region_qa_status'
        ] = 'review'

    ukraine_df.loc[
        missing_region_mask,
        'region_qa_note'
        ] = 'Region is missing in the source data.'

    # Temporary correction field is no longer needed
    ukraine_df = ukraine_df.drop(
        columns=['region_correction']
        )
    
    expected_regions = {
        'vinnytsia oblast',
        'volyn oblast',
        'dnipropetrovsk oblast',
        'donetsk oblast',
        'zhytomyr oblast',
        'zakarpattia oblast',
        'zaporizhia oblast',
        'ivano-frankivsk oblast',
        'kyiv oblast',
        'kirovohrad oblast',
        'luhansk oblast',
        'lviv oblast',
        'mykolaiv oblast',
        'odesa oblast',
        'poltava oblast',
        'rivne oblast',
        'sumy oblast',
        'ternopil oblast',
        'kharkiv oblast',
        'kherson oblast',
        'khmelnytskyi oblast',
        'cherkasy oblast',
        'chernivtsi oblast',
        'chernihiv oblast',
        'kyiv city',
        'crimea',
        'unknown',
        }

    actual_regions = set(
        ukraine_df['region_clean']
        .dropna()
        .unique()
        )

    unexpected_regions = (
        actual_regions - expected_regions
        )

    if unexpected_regions:
        raise ValueError(
            f'Unexpected region values found: '
            f'{unexpected_regions}'
            )
    
    return ukraine_df


def clean_weapon_types(ukraine_df):
    # Preserve raw values and create cleaned analytical field
    ukraine_df['explosive_weapon_type_clean'] = (
        ukraine_df['explosive_weapon_type']
        .str.strip()
        .str.lower()
        )

    # Normalize equivalent categories
    replace_explosive = {
        'aerial bomb, unspecified explosive': 'aerial bomb',
        'missile, unspecified explosive': 'missile',
        }

    ukraine_df['explosive_weapon_type_clean'] = (
        ukraine_df['explosive_weapon_type_clean']
        .replace(replace_explosive)
        .str.title()
    )

    # Restore correct capitalization for acronyms
    acronym_mapping = {
        'Uxo': 'UXO',
        'Rpg': 'RPG',
        'Svied': 'SVIED',
        'Unspecified Ied': 'Unspecified IED',
        }

    ukraine_df['explosive_weapon_type_clean'] = (
        ukraine_df['explosive_weapon_type_clean']
        .replace(acronym_mapping)
        )

    expected_weapon_types = {
        'Aerial Bomb',
        'Shelling',
        'Unspecified Explosive',
        'Missile',
        'Artillery',
        'Rocket',
        'Cluster Bomb',
        'Mortar',
        'Mine',
        'UXO',
        'Hand Grenade',
        'Unspecified IED',
        'RPG',
        'SVIED',
        }

    actual_weapon_types = set(
        ukraine_df['explosive_weapon_type_clean'].dropna().unique()
        )

    unexpected_weapon_types = actual_weapon_types - expected_weapon_types

    if unexpected_weapon_types:
        raise ValueError(
            f'Unexpected weapon types found: {unexpected_weapon_types}'
            )

    # Weapon type should not be missing after cleaning
    if ukraine_df['explosive_weapon_type_clean'].isna().any():
        raise ValueError(
            'Missing values found in explosive_weapon_type_clean'
        )

    return ukraine_df


def create_damage_indicators(ukraine_df):

    # A non-null value is currently treated as evidence
    # that the corresponding system was damaged.
    ukraine_df['food_systems_damage_count'] = ukraine_df['food_systems_damaged_destroyed'].notna().astype(int)

    ukraine_df['water_systems_damage_count'] = ukraine_df['water_systems_damaged_destroyed'].notna().astype(int)

    return ukraine_df


def calculate_infrastructure_total(ukraine_df):

    infrastructure_cols = [
        'food_systems_damage_count',
        'water_systems_damage_count',
        'aid_infrastructure_damaged_destroyed',
        'health_infrastructure_damaged_destroyed',
        'education_infrastructure_damaged_destroyed',
        'idp_refugee_camp_building'
        ]

    # Missing values are treated as 0 only during calculation.
    # Raw source fields remain unchanged.
    ukraine_df['infrastructure_total'] = (
        ukraine_df[infrastructure_cols]
        .fillna(0)
        .sum(axis=1)
        )

    return ukraine_df


def calculate_recorded_deaths(ukraine_df):

    # Calculate total deaths per incident
    death_cols=[
        'aid_workers_killed',
        'health_workers_killed', 
        'aid_health_workers_killed',
        'educators_killed', 
        'students_killed'
        ]

    ukraine_df['recorded_deaths'] = (
        ukraine_df[death_cols]
        .fillna(0)
        .sum(axis=1)
        )

    return ukraine_df


def create_sector_table(ukraine_df):
    # Split sectors and make a new table
    sector_df = ukraine_df[
        ['sind_event_id', 
        'sector_affected']
        ].copy()

    # Convert multi-sector strings into lists
    sector_df['sector_clean']= (
        sector_df['sector_affected']
        .fillna('Unknown')
        .str.strip()
        .str.split(', ')
        )

    # One row per incident-sector combination
    sector_df = sector_df.explode('sector_clean')

    # Remove extra spaces after splitting
    sector_df['sector_clean'] = sector_df['sector_clean'].str.strip()

    # Keep only bridge-table columns
    sector_df = sector_df[
        ['sind_event_id', 'sector_clean']
    ]

    sector_df['sector_clean'].value_counts(dropna=False)

    return sector_df


def validate_data(ukraine_df, sector_df):
    # Main table must not be empty
    if ukraine_df.empty:
        raise ValueError('Main table is empty')

    # Each incident must have a unique SiND Event ID
    if ukraine_df['sind_event_id'].duplicated().any():
        raise ValueError(
            'Duplicate SiND Event IDs found in main table'
        )

    # Important columns must not be missing
    required_columns = [
        'date',
        'sind_event_id',
        'region_clean',
        'explosive_weapon_type_clean',
        'recorded_deaths',
        'infrastructure_total'
    ]

    missing_values = (ukraine_df[required_columns].isna().sum())

    if missing_values.any():
        raise ValueError (
            'Missing values found:{missing_values}'
        )

    # Sector table must contain all incidents
    if (
        sector_df['sind_event_id'].nunique() 
        != ukraine_df['sind_event_id'].nunique()
    ):
        raise ValueError(
            'Some incidents are missing from sector table'
        )

    #One incident-sector pair should appear only once
    duplicate_sectors = sector_df.duplicated(
        subset=['sind_event_id', 'sector_clean']
    )

    if duplicate_sectors.any():
        raise ValueError(
            'Duplicate incident-sector pairs found'
        )

    # Sector_clean should not contain missing values
    if sector_df['sector_clean'].isna().any():
        raise ValueError(
            'Missing sector values found'
        )

    print('Data validation passed successfully')


def save_data(ukraine_df, sector_df):

    ukraine_df.to_csv(
        'processed_incidents.csv',
        index=False
    )

    sector_df.to_csv(
        'processed_sectors.csv',
        index=False
    )

    print('Processed files saved successfully')

def main():

    # Load
    df = load_data(
        'explosive_weapon_raw.xlsx'
    )

    # Basic cleaning
    df = clean_column_names(df)

    # Scope
    ukraine_df = filter_ukraine(df)

    # Geography
    ukraine_df = clean_regions(ukraine_df)

    # Weapon types
    ukraine_df = clean_weapon_types(ukraine_df)

    # Infrastructure metrics
    ukraine_df = create_damage_indicators(
        ukraine_df
    )

    ukraine_df = calculate_infrastructure_total(
        ukraine_df
    )

    # Casualty metrics
    ukraine_df = calculate_recorded_deaths(
        ukraine_df
    )

    # Separate sector table
    sector_df = create_sector_table(
        ukraine_df
    )

    # Final QA
    validate_data(
        ukraine_df,
        sector_df
    )

    # Export
    save_data(
        ukraine_df,
        sector_df
    )

    print('Transform completed successfully')


if __name__ == '__main__':
    main()