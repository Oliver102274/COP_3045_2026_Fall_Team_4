import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    """Simple loader with fallbacks for different directory locations."""
    paths = ["clean_data.csv", "03_Data_Cleaning/clean_data.csv", "../03_Data_Cleaning/clean_data.csv", "04_EDA/clean_data.csv"]
    for path in paths:
        try:
            return pd.read_csv(path)
        except FileNotFoundError:
            continue
    raise FileNotFoundError("Could not find clean_data.csv in any standard directory.")

def plot_salary_range_by_experience(df, save_path=None):
    """Plot 1: Min vs. Max Salary Across Experience Levels."""
    plt.figure(figsize=(10, 6))
    df_melted = df.melt(
        id_vars=['experience_level'], 
        value_vars=['salary_min_usd', 'salary_max_usd'],
        var_name='Salary Type', 
        value_name='Salary (USD)'
    )
    df_melted['Salary Type'] = df_melted['Salary Type'].replace({
        'salary_min_usd': 'Min Salary', 
        'salary_max_usd': 'Max Salary'
    })
    sns.boxplot(
        data=df_melted, x='experience_level', y='Salary (USD)',
        hue='Salary Type', order=['Entry', 'Mid', 'Senior'], palette='Set2'
    )
    plt.title('Salary Range (Min vs. Max) Across Experience Levels', fontsize=14, pad=15)
    plt.xlabel('Experience Level', fontsize=12)
    plt.ylabel('Salary (USD)', fontsize=12)
    plt.legend(title='Metric')
    sns.despine()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
    plt.show()

def plot_salary_by_years_experience(df, save_path=None):
    """Plot 2: Salary Distribution by Required Years of Experience."""
    plt.figure(figsize=(10, 6))
    sns.boxplot(
        data=df, x='min_experience_years', y='salary_min_usd', 
        hue='min_experience_years', palette='Set2', legend=False
    )
    plt.title('Salary Distribution by Required Years of Experience', fontsize=14, pad=15)
    plt.xlabel('Minimum Experience Required (Years)', fontsize=12)
    plt.ylabel('Minimum Salary (USD)', fontsize=12)
    sns.despine()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
    plt.show()
    

def plot_overall_salary_distribution(df, save_path=None):
    """Plot 3: Overall Min vs. Max Salary Frequency and KDE Distribution."""
    plt.figure(figsize=(11, 6))
    sns.histplot(data=df, x='salary_min_usd', color='teal', label='Min Salary', kde=True, bins=30, alpha=0.5)
    sns.histplot(data=df, x='salary_max_usd', color='coral', label='Max Salary', kde=True, bins=30, alpha=0.4)
    plt.title('Overall Salary Distribution (Min vs. Max USD)', fontsize=14, pad=15)
    plt.xlabel('Salary (USD)', fontsize=12)
    plt.ylabel('Frequency / Count', fontsize=12)
    plt.legend()
    sns.despine()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    df = load_data()
    plot_salary_range_by_experience(df)
    plot_salary_by_years_experience(df)
    plot_overall_salary_distribution(df)