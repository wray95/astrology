#!/usr/bin/env python3
"""ASTRO-ML v1.1 — SHAP Analysis + Class Balancing + Full Model Comparison"""
import numpy as np, json
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import shap, warnings; warnings.filterwarnings('ignore')

# Load feature matrix
data = np.load('dataset/astro_ml_feature_matrix.npz')
X = data['X']; y_w = data['y_wealth']; y_c = data['y_children']
feature_names = data['feature_names']; names = data['names']

# Q-series only
q_mask = np.array([1 if not n.startswith('SYNTH') else 0 for n in names])
X_q = X[q_mask == 1]; y_cq = y_c[q_mask == 1]; y_wq = y_w[q_mask == 1]

print('='*65)
print('  ASTRO-ML v1.1 — SHAP + Balanced Models')
print(f'  Charts: {len(X_q)} | Features: {len(feature_names)}')
print(f'  Children+ : {int(y_cq.sum())} ({y_cq.sum()/len(y_cq)*100:.1f}%)')
print(f'  Wealth+   : {int(y_wq.sum())} ({y_wq.sum()/len(y_wq)*100:.1f}%)')
print('='*65)

# ━━━ PIPELINE: SMOTE + RandomForest ━━━
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
results = {}

for label_name, y_data in [('CHILDREN', y_cq), ('WEALTH', y_wq)]:
    print(f'\n{"─"*65}')
    print(f'  {label_name} — SMOTE + RandomForest + SHAP')
    print(f'{"─"*65}')
    
    # Pipeline
    pipe = ImbPipeline([
        ('smote', SMOTE(random_state=42)),
        ('scaler', StandardScaler()),
        ('clf', RandomForestClassifier(n_estimators=200, max_depth=10, class_weight='balanced', random_state=42, n_jobs=1))
    ])
    
    # Train on full data for SHAP
    pipe.fit(X_q, y_data)
    
    # Cross-validation
    cv_results = cross_validate(pipe, X_q, y_data, cv=skf, scoring=['accuracy','roc_auc','f1'], n_jobs=1)
    
    print(f'  Accuracy : {cv_results["test_accuracy"].mean():.3f} (±{cv_results["test_accuracy"].std():.3f})')
    print(f'  AUC-ROC  : {cv_results["test_roc_auc"].mean():.3f} (±{cv_results["test_roc_auc"].std():.3f})')
    print(f'  F1-score : {cv_results["test_f1"].mean():.3f} (±{cv_results["test_f1"].std():.3f})')
    
    # ━━━ SHAP ANALYSIS ━━━
    rf = pipe.named_steps['clf']
    # Use a sample for SHAP (faster)
    sample_idx = np.random.choice(len(X_q), min(500, len(X_q)), replace=False)
    X_sample = pipe.named_steps['scaler'].transform(X_q[sample_idx])
    
    explainer = shap.TreeExplainer(rf)
    shap_values = explainer.shap_values(X_sample)
    
    # Handle multiclass vs binary
    if isinstance(shap_values, list):
        shap_vals = np.array(shap_values[1])
    else:
        shap_vals = np.array(shap_values)
    
    # Squeeze any extra dimensions
    if len(shap_vals.shape) > 2:
        shap_vals = shap_vals[:, :, 0]  # take first class dimension
    
    # Mean |SHAP| per feature
    mean_shap = np.abs(shap_vals).mean(axis=0)
    top_idx = np.argsort(mean_shap)[::-1]
    
    print(f'\n  SHAP TOP 15 — {label_name}:')
    print(f'  {"Rk":<4} {"Feature":<40} {"|SHAP|":>10} {"Direction":>10}')
    print(f'  {"-"*4} {"-"*40} {"-"*10} {"-"*10}')
    
    top_features = []
    for i in range(min(15, len(top_idx))):
        idx = top_idx[i]
        if float(mean_shap[idx]) > 0.001:
            feat_name = feature_names[idx]
            direction = 'POSITIVE' if shap_vals[:, idx].mean() > 0 else 'NEGATIVE'
            top_features.append((feat_name, mean_shap[idx], direction))
            print(f'  {i+1:<4} {feat_name[:39]:<40} {mean_shap[idx]:>10.4f} {direction:>10}')
    
    results[label_name] = {
        'cv_accuracy': float(cv_results['test_accuracy'].mean()),
        'cv_auc': float(cv_results['test_roc_auc'].mean()),
        'cv_f1': float(cv_results['test_f1'].mean()),
        'shap_top': [(f, float(s), d) for f,s,d in top_features],
    }

# ━━━ SAVE ━━━
with open('dataset/astro_ml_shap_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f'\n{"="*65}')
print('  ASTRO-ML v1.1 — COMPLETE')
print(f'{"="*65}')
print(f'  scikit-learn {__import__("sklearn").__version__} | SHAP {shap.__version__} | SMOTE ✓')
print(f'  Earlier AUC-ROC ~0.50 → Now: Children={results["CHILDREN"]["cv_auc"]:.3f}, Wealth={results["WEALTH"]["cv_auc"]:.3f}')
print(f'  Saved: dataset/astro_ml_shap_results.json')
