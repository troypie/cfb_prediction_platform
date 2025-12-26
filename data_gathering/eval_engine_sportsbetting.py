
"""
SPORTS BETTING EVALUATION ENGINE (2025)
--------------------------------------
Purpose: 
Compare multiple predictive models (MLP, Attention, etc.) against 
real-world betting lines (Spreads).

Key Metrics:
- SU (Straight Up): Predictive winner vs Actual winner.
- ATS (Against the Spread): Does the model cover the betting line?
- MAE/RMSE: Statistical error in score differential.
"""

import torch
import numpy as np
import matplotlib.pyplot as plt


# customer imports
import experiment_coverPredict as cover_exp


# --- CORE EVALUATION LOGIC ---


def evaluate_performance(preds, y_test):
    """
    Calculates betting-specific and statistical metrics for a single model.
    Handles 'Pushes' (draws against the spread) by excluding them from accuracy.
    """
    # ensure tensor type and not np array
    if isinstance(y_test, np.ndarray):
        y_test = torch.FloatTensor(y_test)
        actuals = y_test.cpu().numpy().flatten()
        
        # 2. Straight Up (SU) Accuracy
        su_correct = preds == actuals
        su_acc = np.mean(su_correct)
        
        # Filter out where model gives no prediction
        # add not cover prediction + actuals to this
        model_predict_mask = preds != 0
        if np.any(model_predict_mask):
            # Use the actual values where the model chose to "bet"
            valid_preds = preds[model_predict_mask]
            valid_actuals = actuals[model_predict_mask]
            
            # They match if the sign is the same (both 1 or both -1)
            ats_acc = np.mean(valid_preds == valid_actuals)
            ats_mae = np.mean(np.abs(valid_preds == valid_actuals))
            ats_rmse = np.sqrt(np.mean((valid_preds - valid_actuals)**2))
        
        else:
            ats_acc = -1.0
            ats_mae = -1.0
            ats_rmse = -1.0
        
        # 4. Error Metrics
        mae = np.mean(np.abs(preds - actuals))
        rmse = np.sqrt(np.mean((preds - actuals)**2))
        
        
        return {
            "su_acc": su_acc,
            "su_mae": mae,
            "su_rmse": rmse,
            "called_acc": ats_acc,
            "called_mae": ats_mae,
            "called_rmse": ats_rmse
        }

# --- EXPERIMENT ORCHESTRATION ---

def evaluate_experiment(preds, test_y, model_name: str | None = None):
    """
    Runs a head-to-head comparison of provided models.
    'models' should be a dict: {"ModelName": model_object}
    """

    # 2. Collect Results
    results = evaluate_performance(preds, test_y) 

    # 3. Print Results Table
    print_results_table({model_name:results})
    
    # 4. Visualize
    # - TODO    
    # plot_model_comparison(results)
    
    return results

# --- HELPER UTILITIES ---

def test_set_to_args(ts):
    """Helper to unpack dictionary into positional arguments for evaluation."""
    return (ts['a'], ts['h'], ts['y'])

def print_results_table(results):
    """Prints a clean comparison table of all model metrics."""
    names = list(results.keys())
    metrics = [
        ("su_acc", "Win % (Straight)", ".2%"),
        ("su_mae", "Avg Error (Pts)", ".2f"),
        ("su_rmse", "Volatility (RMSE)", ".2f"),
        ("called_acc", "Called Accuracy", ".2%"),
        ("called_mae", "Called MAE", ".2f"),
        ("called_rmse", "Called RMSE", ".2f")
    ]
    
    header = f"{'Metric':<20} | " + " | ".join([f"{n:<12}" for n in names])
    print(f"\n{header}\n{'-' * len(header)}")
    
    for key, label, fmt in metrics:
        row = f"{label:<20} | "
        row += " | ".join([f"{results[n][key]:<12{fmt}}" for n in names])
        print(row)

def plot_model_comparison(results):
    """Generates a bar chart comparing accuracy metrics against the breakeven line."""
    names = list(results.keys())
    su_vals = [results[n]['su_acc'] for n in names]
    ats_vals = [results[n]['ats_acc'] for n in names]
    
    x = np.arange(len(names))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, su_vals, width, label='SU Accuracy', color='#3498db')
    ax.bar(x + width/2, ats_vals, width, label='ATS Accuracy', color='#e74c3c')
    
    # The 'Vegas' Line: You must win ~52.4% to profit with -110 odds
    ax.axhline(0.524, color='#2c3e50', linestyle='--', alpha=0.5, label='Breakeven (52.4%)')
    
    ax.set_ylabel('Accuracy Rate')
    ax.set_title('Model Performance: 2025 Betting Season')
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.legend()
    plt.tight_layout()
    plt.show()

# --- EXECUTION ---
if __name__ == "__main__":
    # Example usage:
    # run_betting_experiment({"MLP": mlp_model, "Attention": attn_model})
    pass