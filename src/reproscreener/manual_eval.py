from pathlib import Path
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple, Union
import numpy as np

log = logging.getLogger(__name__)

class ManualEvaluationParser:
    """Parser for manual evaluation CSV files with standardized format."""
    
    def __init__(self, base_dir: str = "manual_evaluations"):
        self.base_dir = Path(base_dir)
        self.standardized_metrics = {
            # Binary metrics (0/1 or True/False)
            'problem': 'problem_identified',
            'objective': 'objective_identified', 
            'research_method': 'research_method_identified',
            'research_questions': 'research_questions_identified',
            'pseudocode': 'pseudocode_identified',
            'dataset': 'dataset_identified',
            'hypothesis': 'hypothesis_identified',
            'prediction': 'prediction_identified',
            'code_avail': 'code_available',
            'software_dependencies': 'software_dependencies_identified',
            'experiment_setup': 'experiment_setup_identified',
            
            # Manuscript specific metrics
            'empirical_dataset': 'empirical_dataset_used',
            'code_avail_article': 'code_available_in_article',
            'pwc_link_avail': 'papers_with_code_link_available',
            'pwc_link_match': 'papers_with_code_link_matches',
            'result_replication_code_avail': 'result_replication_code_available',
            'package': 'is_package',
            'wrapper_scripts': 'has_wrapper_scripts',
            'hardware_specifications': 'hardware_specifications_provided',
            'will_it_reproduce': 'likely_to_reproduce',
            'parsed_readme': 'readme_parsed_successfully'
        }
        
    def _clean_paper_id(self, paper_id: str) -> str:
        """Clean and standardize paper IDs."""
        if pd.isna(paper_id) or paper_id == "Paper":
            return None
        return str(paper_id).strip()
    
    def _parse_binary_value(self, value: Union[str, int, float]) -> Optional[bool]:
        """Parse various formats of binary values to boolean.

        The function now also understands decimal strings (e.g. "0.67") and
        converts every numeric input to a binary value using a 0.5 threshold.
        """
        if pd.isna(value):
            return None

        if isinstance(value, (int, float)):
            if value == 1 or value == 1.0:
                return True
            if value == 0 or value == 0.0:
                return False
            return value > 0.5

        str_val = str(value).strip()

        # Interpret the string as a float (works for "0.83", "1", etc.)
        try:
            num_val = float(str_val)
            return num_val > 0.5
        except ValueError:
            pass

        str_val = str_val.lower()
        if str_val in {'1', 'true', 'yes', 'y'}:
            return True
        if str_val in {'0', 'false', 'no', 'n'}:
            return False

        return None
    
    def _extract_description(self, text: str) -> str:
        """Clean and extract description text."""
        if pd.isna(text) or text == "":
            return ""
        return str(text).strip()
    
    def parse_abstract_evaluation(self, filename: str = "abstract_manual_evaluation.csv") -> pd.DataFrame:
        """Parse the abstract evaluation CSV file."""
        file_path = self.base_dir / filename
        
        if not file_path.exists():
            log.error(f"File not found: {file_path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path)
            df = df.iloc[1:] # remove header rows
            df = df.iloc[:-1] # remove totals row

            standardized_data = []
            
            for _, row in df.iterrows():
                paper_id = self._clean_paper_id(row['paper'])
                if not paper_id:
                    continue
                    
                record = {
                    'paper_id': paper_id,
                    'evaluation_type': 'abstract',
                    'source_file': filename
                }
                
                metrics = ['problem', 'objective', 'research_method', 'research_questions', 
                          'pseudocode', 'dataset', 'hypothesis', 'prediction', 'code_avail', 
                          'software_dependencies', 'experiment_setup']
                
                for metric in metrics:
                    binary_col = metric
                    phrase_col = f"{metric}_phrase"
                    
                    if binary_col in row:
                        record[self.standardized_metrics[metric]] = self._parse_binary_value(row[binary_col])
                    
                    if phrase_col in row:
                        record[f"{self.standardized_metrics[metric]}_description"] = self._extract_description(row[phrase_col])
                
                standardized_data.append(record)
            
            df = pd.DataFrame(standardized_data)
            return self._finalize_dataframe(df)
            
        except Exception as e:
            log.error(f"Error parsing abstract evaluation file: {e}")
            return pd.DataFrame()
    
    def parse_agreement_evaluation(self, filename: str = "abstract_gpt_agreement_with_manual.csv") -> pd.DataFrame:
        """Parse the GPT agreement evaluation CSV file."""
        file_path = self.base_dir / filename
        
        if not file_path.exists():
            log.error(f"File not found: {file_path}")
            return pd.DataFrame()
        
        try:
            # Skip the first row (note) and use the second row as headers
            df = pd.read_csv(file_path, skiprows=1)
            
            # Remove header rows and totals
            df = df[~df['paper'].isin(['Paper', 'Totals']) & df['paper'].notna()]
            
            standardized_data = []
            
            for _, row in df.iterrows():
                paper_id = self._clean_paper_id(row['paper'])
                if not paper_id:
                    continue
                    
                record = {
                    'paper_id': paper_id,
                    'evaluation_type': 'agreement_gpt',
                    'source_file': filename
                }
                
                # Parse GPT evaluations and comparisons
                metrics = ['problem', 'objective', 'research_method', 'research_questions', 
                          'pseudocode', 'dataset', 'hypothesis', 'prediction', 'code_avail', 
                          'software_dependencies', 'experiment_setup']
                
                for metric in metrics:
                    gpt_col = metric
                    phrase_col = f"{metric}_phrase"
                    comparison_col = f"{metric}_phrase_comparision"
                    
                    if gpt_col in row:
                        record[f"gpt_{self.standardized_metrics[metric]}"] = self._parse_binary_value(row[gpt_col])
                    
                    if phrase_col in row:
                        record[f"gpt_{self.standardized_metrics[metric]}_description"] = self._extract_description(row[phrase_col])
                    
                    if comparison_col in row:
                        record[f"{self.standardized_metrics[metric]}_agreement"] = self._parse_binary_value(row[comparison_col])
                
                standardized_data.append(record)
            
            df = pd.DataFrame(standardized_data)
            return self._finalize_dataframe(df)
            
        except Exception as e:
            log.error(f"Error parsing agreement evaluation file: {e}")
            return pd.DataFrame()
    
    def parse_manuscript_evaluation(self, filename: str = "full_manuscript_manual_evaluation.csv") -> pd.DataFrame:
        """Parse the manuscript evaluation CSV file."""
        file_path = self.base_dir / filename
        
        if not file_path.exists():
            log.error(f"File not found: {file_path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path)
            
            # Remove header description row and totals row
            df = df[~df['paper'].isin(['Paper', 'Totals']) & df['paper'].notna()]
            
            standardized_data = []
            
            for _, row in df.iterrows():
                paper_id = self._clean_paper_id(row['paper'])
                if not paper_id:
                    continue
                    
                record = {
                    'paper_id': paper_id,
                    'evaluation_type': 'manuscript',
                    'source_file': filename
                }
                
                # Parse URLs and basic info
                if 'paper_url' in row:
                    record['paper_url'] = self._extract_description(row['paper_url'])
                if 'notes' in row:
                    record['notes'] = self._extract_description(row['notes'])
                
                # Parse binary metrics directly from column names
                binary_cols = [
                    'empirical_dataset', 'code_avail_article', 'pwc_link_avail', 'pwc_link_match',
                    'result_replication_code_avail', 'package', 'wrapper_scripts',
                    'hardware_specifications', 'software_dependencies', 'will_it_reproduce', 'parsed_readme'
                ]
                
                for col in binary_cols:
                    if col in row and col in self.standardized_metrics:
                        record[self.standardized_metrics[col]] = self._parse_binary_value(row[col])
                
                # Parse text fields directly from column names
                text_cols = [
                    'code_avail_url', 'pwc_link_desc', 'code_language', 'wrapper_scripts_desc',
                    'software_dependencies_desc', 'will_it_reproduce_desc'
                ]
                
                for col in text_cols:
                    if col in row:
                        record[col] = self._extract_description(row[col])
                
                # Parse reproducibility metrics with descriptions
                repro_metrics = ['problem', 'objective', 'research_method', 'research_questions', 
                               'pseudocode', 'dataset', 'hypothesis', 'prediction', 'experiment_setup']
                
                for metric in repro_metrics:
                    # Check for both capitalized and lowercase versions
                    metric_col = metric.title() if metric.title() in row else metric
                    desc_col = f"{metric}_desc"
                    
                    if metric_col in row and metric in self.standardized_metrics:
                        record[self.standardized_metrics[metric]] = self._parse_binary_value(row[metric_col])
                    
                    if desc_col in row and metric in self.standardized_metrics:
                        record[f"{self.standardized_metrics[metric]}_description"] = self._extract_description(row[desc_col])
                
                standardized_data.append(record)
            
            df = pd.DataFrame(standardized_data)
            return self._finalize_dataframe(df)
            
        except Exception as e:
            log.error(f"Error parsing manuscript evaluation file: {e}")
            return pd.DataFrame()
    
    def load_all_evaluations(self) -> Dict[str, pd.DataFrame]:
        """Load all manual evaluation files and return as a dictionary of DataFrames."""
        evaluations = {}
        
        evaluations['abstract'] = self.parse_abstract_evaluation()
        evaluations['agreement_gpt'] = self.parse_agreement_evaluation()
        evaluations['manuscript'] = self.parse_manuscript_evaluation()
        evaluations['combined_abstract'] = self.create_combined_abstract_evaluation()
        
        return evaluations
    
    def create_combined_abstract_evaluation(self) -> pd.DataFrame:
        """Create a combined dataset merging abstract evaluation with GPT agreement data."""
        abstract_df = self.parse_abstract_evaluation()
        gpt_agreement_df = self.parse_agreement_evaluation()
        
        if abstract_df.empty or gpt_agreement_df.empty:
            log.warning("One or both abstract evaluation datasets are empty")
            return pd.DataFrame()
        
        # Merge on paper_id
        combined_data = []
        
        # Get all unique paper IDs from both datasets
        all_paper_ids = set(abstract_df['paper_id'].unique()) | set(gpt_agreement_df['paper_id'].unique())
        
        for paper_id in all_paper_ids:
            record = {'paper_id': paper_id, 'evaluation_type': 'combined_abstract'}
            
            # Get abstract evaluation data
            abstract_row = abstract_df[abstract_df['paper_id'] == paper_id]
            if not abstract_row.empty:
                abstract_data = abstract_row.iloc[0]
                # Add manual evaluation metrics with 'manual_' prefix
                for col in abstract_data.index:
                    if col not in ['paper_id', 'evaluation_type', 'source_file']:
                        record[f"manual_{col}"] = abstract_data[col]
            
            # Get GPT agreement data
            gpt_row = gpt_agreement_df[gpt_agreement_df['paper_id'] == paper_id]
            if not gpt_row.empty:
                gpt_data = gpt_row.iloc[0]
                # Add GPT evaluation metrics and agreement scores
                for col in gpt_data.index:
                    if col not in ['paper_id', 'evaluation_type', 'source_file']:
                        record[col] = gpt_data[col]
            
            # Calculate overall agreement metrics
            agreement_cols = [col for col in record.keys() if col.endswith('_agreement')]
            if agreement_cols:
                agreement_values = [record[col] for col in agreement_cols if pd.notna(record.get(col))]
                if agreement_values:
                    record['overall_agreement_rate'] = sum(agreement_values) / len(agreement_values)
                    record['total_agreements'] = sum(agreement_values)
                    record['total_comparisons'] = len(agreement_values)
            
            combined_data.append(record)
        
        df = pd.DataFrame(combined_data)
        return self._finalize_dataframe(df)
    
    def create_unified_dataset(self) -> pd.DataFrame:
        """Create a unified dataset combining all evaluation types."""
        evaluations = self.load_all_evaluations()
        
        # Combine all dataframes
        all_dfs = []
        for eval_type, df in evaluations.items():
            if not df.empty:
                all_dfs.append(self._finalize_dataframe(df.copy()))
        
        if not all_dfs:
            return pd.DataFrame()
        
        # Concatenate all evaluations
        unified_df = pd.concat(all_dfs, ignore_index=True, sort=False)
        
        return unified_df
    
    def get_comparison_metrics(self) -> pd.DataFrame:
        """Create a comparison view showing metrics across different evaluation types."""
        evaluations = self.load_all_evaluations()
        
        # Get unique papers across all evaluations
        all_papers = set()
        for df in evaluations.values():
            if not df.empty:
                all_papers.update(df['paper_id'].unique())
        
        comparison_data = []
        
        for paper_id in all_papers:
            record = {'paper_id': paper_id}
            
            for eval_type, df in evaluations.items():
                if df.empty:
                    continue
                    
                paper_data = df[df['paper_id'] == paper_id]
                if not paper_data.empty:
                    paper_row = paper_data.iloc[0]
                    
                    # Add evaluation type specific metrics
                    for col in paper_row.index:
                        if col not in ['paper_id', 'evaluation_type', 'source_file']:
                            record[f"{eval_type}_{col}"] = paper_row[col]
            
            comparison_data.append(record)
        
        return pd.DataFrame(comparison_data)
    
    def get_summary_statistics(self) -> Dict[str, Dict]:
        """Generate summary statistics for each evaluation type."""
        evaluations = self.load_all_evaluations()
        
        summary = {}
        
        for eval_type, df in evaluations.items():
            if df.empty:
                summary[eval_type] = {"error": "No data available"}
                continue
                
            stats = {
                "total_papers": len(df),
                "unique_papers": df['paper_id'].nunique(),
                "metrics_analyzed": []
            }
            
            # Count metrics with binary values
            for col in df.columns:
                if col.endswith(('_identified', '_available', '_used')):
                    metric_name = col.replace('_identified', '').replace('_available', '').replace('_used', '')
                    if df[col].notna().sum() > 0:  # Has some data
                        true_count = df[col].sum() if df[col].dtype == bool else (df[col] == True).sum()
                        total_count = df[col].notna().sum()
                        stats["metrics_analyzed"].append({
                            "metric": metric_name,
                            "positive_count": int(true_count) if not pd.isna(true_count) else 0,
                            "total_evaluated": int(total_count),
                            "percentage": round((true_count / total_count * 100), 2) if total_count > 0 else 0
                        })
            
            summary[eval_type] = stats
        
        return summary


    def _finalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        # 1) Clean column names ------------------------------------------------
        cleaned = {}
        for col in df.columns:
            new_col = col.replace("_identified", "").replace("_used", "")
            cleaned[col] = new_col
        df = df.rename(columns=cleaned)

        # 2) Set paper_id as index while keeping the column for joins ---------
        if 'paper_id' in df.columns:
            df = df.set_index('paper_id', drop=False)

        # 3) Coerce binary columns to bool ---------------------------
        for col in df.columns:
            if df[col].dtype in {np.int64, np.float64, 'object'}:
                unique_vals = set(df[col].dropna().unique())
                if unique_vals.issubset({0, 1, True, False}):
                    df[col] = df[col].astype(bool)
        return df


def load_manual_evaluations(base_dir: str = "manual_evaluations") -> ManualEvaluationParser:
    """Factory function to create and return a ManualEvaluationParser instance."""
    return ManualEvaluationParser(base_dir)


def main():
    """Example usage of the manual evaluation parser."""
    parser = load_manual_evaluations()
    
    evaluations = parser.load_all_evaluations()
    
    print("=== Manual Evaluation Summary ===")
    for eval_type, df in evaluations.items():
        print(f"\n{eval_type.upper()} Evaluation:")
        print(f"  Papers: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        if not df.empty:
            print(f"  Sample columns: {list(df.columns[:5])}")
    
    print("\n=== Summary Statistics ===")
    summary = parser.get_summary_statistics()
    for eval_type, stats in summary.items():
        print(f"\n{eval_type.upper()}:")
        if "error" in stats:
            print(f"  {stats['error']}")
        else:
            print(f"  Total papers: {stats['total_papers']}")
            print(f"  Unique papers: {stats['unique_papers']}")
            print(f"  Metrics analyzed: {len(stats['metrics_analyzed'])}")
    
    unified = parser.create_unified_dataset()
    print(f"\n=== Unified Dataset ===")
    print(f"Total records: {len(unified)}")
    print(f"Unique papers: {unified['paper_id'].nunique()}")
    print(f"Evaluation types: {unified['evaluation_type'].unique()}")
    
    return parser, evaluations, unified


if __name__ == "__main__":
    main()