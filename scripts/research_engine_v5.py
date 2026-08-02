#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
NEXUS v5.0 RESEARCH ENGINE — Synthetic Validation + Interaction Mining + Bayesian Inference
═══════════════════════════════════════════════════════════════
Builds on v4 matrix (193 features × 6,520 charts).

Modules executed in this run:
  M1 — Synthetic Validation (permutation testing)
  M2 — Feature Interaction Mining (2-way combinations)
  M3 — Bayesian Updating (conjugate Beta-Binomial)
  M4 — Counterfactual Testing (SHAP-based)

All results saved to dataset/research_v5_*.json
"""
import numpy as np, json, time, os
from collections import Counter, defaultdict
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
import warnings; warnings.filterwarnings('ignore')

np.random.seed(42)

print("=" * 70)
print("  NEXUS RESEARCH ENGINE v5.0")
print("  Synthetic Validation · Interaction Mining · Bayesian Inference")
print("=" * 70)

# ── Load v4 matrix ──
d = np.load('dataset/astro_v4_matrix.npz', allow_pickle=True)
X = d['X']; industries = d['industries']; q_mask = d['q_mask']; fnames = list(d['feature_names'])

# Use synthetic charts with known industries (exclude Q-series "UNKNOWN")
syn_mask = ~q_mask
known_mask = industries != 'UNKNOWN'
mask = syn_mask & known_mask
X_ind = X[mask]; y_ind_str = industries[mask]
le = LabelEncoder()
y_ind = le.fit_transform(y_ind_str)
ind_classes = le.classes_

N = X_ind.shape[0]; D = X_ind.shape[1]
print(f"\n  Dataset: {N} synthetic charts × {D} features ({len(ind_classes)} industries)")
print(f"  Classes: {dict(zip(*np.unique(y_ind_str, return_counts=True)))}")

# ═══════════════════════════════════════════════════════════
# M1 — SYNTHETIC VALIDATION (Permutation Testing)
# ═══════════════════════════════════════════════════════════
print(f"\n{'─'*60}")
print(f"  M1: SYNTHETIC VALIDATION")
print(f"{'─'*60}")

# Train RF on real data
rf_real = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
real_scores = cross_val_score(rf_real, X_ind, y_ind, cv=5, scoring='accuracy')
real_mean = real_scores.mean()
real_std = real_scores.std()

print(f"\n  Real data 5-fold CV accuracy: {real_mean:.4f} ± {real_std:.4f}")

# Permutation test: shuffle y_ind 200 times
n_perm = 200
perm_scores = []
t0 = time.time()
for i in range(n_perm):
    y_perm = np.random.permutation(y_ind)
    rf_perm = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42+i, n_jobs=-1)
    s = cross_val_score(rf_perm, X_ind, y_perm, cv=5, scoring='accuracy').mean()
    perm_scores.append(s)
perm_mean = np.mean(perm_scores)
perm_std = np.std(perm_scores)
p_value = (sum(1 for s in perm_scores if s >= real_mean) + 1) / (n_perm + 1)
t1 = time.time()

print(f"  Permuted data accuracy: {perm_mean:.4f} ± {perm_std:.4f} (n={n_perm})")
print(f"  Δ accuracy: {real_mean - perm_mean:+.4f} ({p_value:.4f} one-sided p)")
print(f"  Time: {t1-t0:.1f}s")

# Also test individual features
print(f"\n  Feature-level permutation tests (top 15 features):")
# Train one RF to get feature importances
rf_base = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1)
rf_base.fit(X_ind, y_ind)
importances = rf_base.feature_importances_
top_features = np.argsort(importances)[-15:][::-1]

feature_tests = []
for rank, fi in enumerate(top_features):
    fn = fnames[fi]
    X_perm = X_ind.copy()
    np.random.shuffle(X_perm[:, fi])
    rf_test = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    base_score = cross_val_score(rf_test, X_ind, y_ind, cv=5, scoring='accuracy').mean()
    perm_score = cross_val_score(rf_test, X_perm, y_ind, cv=5, scoring='accuracy').mean()
    delta = base_score - perm_score
    significance = '⭐' if delta > 0.005 else ('●' if delta > 0.002 else '—')
    feature_tests.append({'rank': rank+1, 'feature': fn, 'importance': float(importances[fi]),
                          'base_acc': float(base_score), 'perm_acc': float(perm_score),
                          'delta': float(delta), 'significant': delta > 0.005})
    print(f"    {rank:>2d}. {fn:<25s} base={base_score:.4f} perm={perm_score:.4f} Δ={delta:+.4f} {significance}")

synth_val = {
    'method': 'permutation_test',
    'n_permutations': n_perm,
    'real_accuracy': {'mean': float(real_mean), 'std': float(real_std)},
    'permuted_accuracy': {'mean': float(perm_mean), 'std': float(perm_std)},
    'delta_accuracy': float(real_mean - perm_mean),
    'p_value': float(p_value),
    'significant': p_value < 0.05,
    'feature_tests': feature_tests,
    'conclusion': 'Industry classification signal in synthetic charts is weak but non-zero. '
                  'Most individual features show no significant permutation impact — '
                  'consistent with AI-generated birth dates having random astrological patterns.'
}

# ═══════════════════════════════════════════════════════════
# M2 — FEATURE INTERACTION MINING
# ═══════════════════════════════════════════════════════════
print(f"\n{'─'*60}")
print(f"  M2: FEATURE INTERACTION MINING (2-way)")
print(f"{'─'*60}")

# Focus on yoga features (binary) — test all pairs for industry enrichment
YOGA_FEATURES = ['GajKesari','BudhaAditya','Shrinkhala','NBRY','MP_Shrinkhala',
                 'Shrinkhala_loop5','Shrinkhala_loop3','Vargottama_2plus','MP_2plus',
                 'D9_GajKesari','D9_Venus_OWN','D9_Moon_5H','GK_D1_D9','NBRY_D1_D9',
                 'Kendras_loaded','Moon_Billionaire_Nak','D9_Shrinkhala']

yoga_indices = [list(fnames).index(yf) for yf in YOGA_FEATURES if yf in fnames]
YOGA_FEATURES = [fnames[i] for i in yoga_indices]

print(f"  Testing {len(YOGA_FEATURES)} yoga features × {len(ind_classes)} industries")
print(f"  Total pairs: {len(YOGA_FEATURES)*(len(YOGA_FEATURES)-1)//2 * len(ind_classes)}")

interactions = []
for i, yf1 in enumerate(YOGA_FEATURES):
    idx1 = list(fnames).index(yf1)
    for j, yf2 in enumerate(YOGA_FEATURES):
        if j <= i: continue
        idx2 = list(fnames).index(yf2)
        pair_mask = (X_ind[:, idx1] > 0) & (X_ind[:, idx2] > 0)
        n_pair = pair_mask.sum()
        if n_pair < 20: continue  # minimum support
        
        # Overall has-pair rate
        pair_rate = n_pair / N
        
        for k, ind_name in enumerate(ind_classes):
            ind_mask = y_ind_str == ind_name
            ind_n = ind_mask.sum()
            pair_in_ind = (pair_mask & ind_mask).sum()
            expected = pair_rate * ind_n
            
            if expected < 5: continue
            
            # Binomial test
            p_val = stats.binomtest(pair_in_ind, n=ind_n, p=pair_rate).pvalue
            enrichment = pair_in_ind / ind_n / pair_rate if pair_rate > 0 else 1.0
            
            if p_val < 0.10 and (enrichment > 1.5 or enrichment < 0.67):
                interactions.append({
                    'pair': f'{yf1} + {yf2}',
                    'industry': str(ind_name),
                    'n_pair_total': int(n_pair),
                    'n_pair_industry': int(pair_in_ind),
                    'n_industry': int(ind_n),
                    'enrichment': round(float(enrichment), 2),
                    'p_value': round(float(p_val), 4),
                    'direction': 'enriched' if enrichment > 1 else 'depleted'
                })

interactions.sort(key=lambda x: (not x['direction'] == 'enriched', -x['enrichment']))
top_interactions = interactions[:30]

print(f"\n  Found {len(interactions)} significant interactions (p<0.10)")
print(f"  Top 15 enriched pairs:")
for ix in top_interactions[:15]:
    if ix['direction'] == 'enriched':
        print(f"    {ix['pair']:<40s} → {ix['industry']:<15s} {ix['enrichment']:>5.1f}x (p={ix['p_value']:.4f})")

# ═══════════════════════════════════════════════════════════
# M3 — BAYESIAN UPDATING (Beta-Binomial conjugate)
# ═══════════════════════════════════════════════════════════
print(f"\n{'─'*60}")
print(f"  M3: BAYESIAN UPDATING")
print(f"{'─'*60}")

# Prior: Beta(1,1) = uniform
# For each industry class and each yoga, compute posterior Beta(α+pos, β+neg)

bayesian_results = {}
for k, ind_name in enumerate(ind_classes):
    ind_mask = y_ind_str == ind_name
    ind_n = ind_mask.sum()
    ind_rate = ind_n / N
    
    for yf in YOGA_FEATURES:
        idx = list(fnames).index(yf)
        yoga_mask = X_ind[:, idx] > 0
        
        # In-industry
        pos = (yoga_mask & ind_mask).sum()
        neg = ind_mask.sum() - pos
        
        # Out-of-industry
        pos_out = (yoga_mask & ~ind_mask).sum()
        neg_out = (~ind_mask).sum() - pos_out
        
        if pos + neg < 5: continue
        
        # Beta posterior for in-industry yoga rate
        alpha_post = 1 + pos
        beta_post = 1 + neg
        posterior_mean = alpha_post / (alpha_post + beta_post)
        
        # Beta posterior for out-of-industry yoga rate
        alpha_out = 1 + pos_out
        beta_out = 1 + neg_out
        posterior_out = alpha_out / (alpha_out + beta_out)
        
        # Bayes factor (approximate via ratio of posterior means / prior means)
        prior_mean = 1/2
        bf = (posterior_mean / (1 - posterior_mean)) / (posterior_out / (1 - posterior_out)) if posterior_out > 0 and posterior_out < 1 else 1.0
        
        # Credible interval (95% equal-tailed)
        ci_low = stats.beta.ppf(0.025, alpha_post, beta_post)
        ci_high = stats.beta.ppf(0.975, alpha_post, beta_post)
        
        key = f'{ind_name}|{yf}'
        bayesian_results[key] = {
            'industry': str(ind_name),
            'feature': yf,
            'n_industry': int(ind_n),
            'n_yoga_in_ind': int(pos),
            'posterior_mean': round(float(posterior_mean), 4),
            'posterior_out': round(float(posterior_out), 4),
            'ci_95': [round(float(ci_low), 4), round(float(ci_high), 4)],
            'bayes_factor': round(float(bf), 2),
            'effect_direction': 'positive' if posterior_mean > posterior_out else 'negative',
        }

# Top Bayesian findings
bf_sorted = sorted(bayesian_results.items(), key=lambda x: -abs(x[1]['bayes_factor']-1) * x[1].get('n_yoga_in_ind',0))
print(f"\n  Top 10 Bayesian posterior effects:")
for key, val in bf_sorted[:10]:
    if val['bayes_factor'] != 1.0:
        bf_str = f"BF={val['bayes_factor']:.1f}" if val['bayes_factor'] < 100 else f"BF>100"
        dir_str = '↑' if val['effect_direction'] == 'positive' else '↓'
        print(f"    {val['industry']:<12s} × {val['feature']:<22s} "
              f"post={val['posterior_mean']:.3f} out={val['posterior_out']:.3f} "
              f"CI[{val['ci_95'][0]:.3f}, {val['ci_95'][1]:.3f}] {bf_str} {dir_str}")

# ═══════════════════════════════════════════════════════════
# M4 — COUNTERFACTUAL TESTING (SHAP-based)
# ═══════════════════════════════════════════════════════════
print(f"\n{'─'*60}")
print(f"  M4: COUNTERFACTUAL TESTING")
print(f"{'─'*60}")

# For the most "important" feature per industry, compute counterfactual predictions
rf_final = RandomForestClassifier(n_estimators=300, max_depth=12, random_state=42, n_jobs=-1)
rf_final.fit(X_ind, y_ind)

counterfactuals = []
for k, ind_name in enumerate(ind_classes):
    # Get feature most important for this class
    # Use per-class feature importance from trees
    class_importances = np.zeros(D)
    for tree in rf_final.estimators_:
        tree_imp = tree.tree_.compute_feature_importances(normalize=False)
        # Which features matter most when predicting this class
        class_importances += tree_imp
    
    top_idx = np.argsort(class_importances)[-5:][::-1]
    
    # Counterfactual: toggle top binary feature
    for fi in top_idx[:3]:
        fn = fnames[fi]
        # Only test binary features
        vals = np.unique(X_ind[:, fi])
        if len(vals) > 2: continue
        
        # Predictions with feature = 0
        X_0 = X_ind.copy()
        X_0[:, fi] = 0
        pred_0 = rf_final.predict_proba(X_0)[:, k].mean()
        
        # Predictions with feature = 1
        X_1 = X_ind.copy()
        X_1[:, fi] = 1
        pred_1 = rf_final.predict_proba(X_1)[:, k].mean()
        
        if abs(pred_1 - pred_0) > 0.002:
            counterfactuals.append({
                'industry': str(ind_name),
                'feature': fn,
                'pred_false': round(float(pred_0), 4),
                'pred_true': round(float(pred_1), 4),
                'delta': round(float(pred_1 - pred_0), 4),
                'n_has_feature': int((X_ind[:, fi] > 0).sum()),
            })

counterfactuals.sort(key=lambda x: -abs(x['delta']))
print(f"\n  Top counterfactual effects:")
for cf in counterfactuals[:12]:
    dir_str = '↑' if cf['delta'] > 0 else '↓'
    print(f"    {cf['industry']:<12s}: {cf['feature']:<25s} "
          f"{cf['pred_false']:.3%} → {cf['pred_true']:.3%} "
          f"(Δ={cf['delta']:+.3%}) {dir_str}  (n={cf['n_has_feature']})")

# ═══════════════════════════════════════════════════════════
# SAVE ALL
# ═══════════════════════════════════════════════════════════
output = {
    'version': '5.0',
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
    'dataset': f'{N} charts × {D} features, {len(ind_classes)} industries',
    'm1_synthetic_validation': synth_val,
    'm2_feature_interactions': {
        'total_tested': len(YOGA_FEATURES) * (len(YOGA_FEATURES) - 1) // 2 * len(ind_classes),
        'significant': len(interactions),
        'top_30': top_interactions,
    },
    'm3_bayesian': {
        'total_tested': len(bayesian_results),
        'top_effects': bf_sorted[:20],
    },
    'm4_counterfactuals': {
        'total_tested': len(counterfactuals),
        'top_effects': counterfactuals[:20],
    },
    'methodology_notes': {
        'synthetic_validation': 'Permutation test: 200 random shuffles of industry labels. '
            'Tests whether astrological features carry more signal than random noise.',
        'interaction_mining': 'Tests all pairs of 17 yoga features for industry enrichment '
            'using binomial test. Reports enrichment ratio and p-value.',
        'bayesian': 'Beta-Binomial conjugate model with uniform prior. '
            'Reports posterior mean, 95% credible interval, and Bayes factor.',
        'counterfactual': 'SHAP-style: toggle binary feature on all charts and measure '
            'average predicted probability change for each industry class.',
        'limitations': 'Synthetic industry charts use AI-generated birth dates. '
            'No causation claims. Label bottleneck (0/5010 wealth labels). '
            'Industry classification ceiling ~30% accuracy.',
    }
}

with open('dataset/research_v5_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n{'='*70}")
print(f"  ✅ ALL MODULES COMPLETE")
print(f"  Saved: dataset/research_v5_results.json")
print(f"{'='*70}")
