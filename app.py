import os
import uuid
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, request, render_template, jsonify, session
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
import base64
from io import BytesIO

warnings.filterwarnings('ignore')

app = Flask(__name__)
app.secret_key = 'ml_app_secret_2024'
UPLOAD_FOLDER = 'static/uploads'
PLOT_FOLDER = 'static/plots'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PLOT_FOLDER, exist_ok=True)

# ─── Helpers ─────────────────────────────────────────────────────────────────

def fig_to_b64(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=130, facecolor='#0f172a')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return encoded

def preprocess(df):
    """Drop high-null cols, encode categoricals, impute, return numeric df."""
    df = df.copy()
    # Drop cols with >60% missing
    thresh = len(df) * 0.4
    df = df.dropna(axis=1, thresh=thresh)
    # Encode object columns
    le = LabelEncoder()
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str)
        df[col] = le.fit_transform(df[col])
    # Keep only numeric
    df = df.select_dtypes(include=[np.number])
    # Impute
    imputer = SimpleImputer(strategy='mean')
    df = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
    return df

# ─── Plot style ──────────────────────────────────────────────────────────────

DARK_BG   = '#0f172a'
CARD_BG   = '#1e293b'
ACCENT    = '#6366f1'
ACCENT2   = '#22d3ee'
ACCENT3   = '#f59e0b'
TEXT      = '#e2e8f0'
GRID      = '#334155'

PALETTE = [ACCENT, ACCENT2, ACCENT3, '#f43f5e', '#a3e635', '#fb923c',
           '#c084fc', '#34d399', '#f472b6', '#60a5fa']

def set_style(fig, ax_or_axes):
    fig.patch.set_facecolor(DARK_BG)
    axes = ax_or_axes if hasattr(ax_or_axes, '__iter__') else [ax_or_axes]
    for ax in axes:
        ax.set_facecolor(CARD_BG)
        ax.tick_params(colors=TEXT, labelsize=8)
        ax.xaxis.label.set_color(TEXT)
        ax.yaxis.label.set_color(TEXT)
        ax.title.set_color(TEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID)
        ax.grid(True, color=GRID, linewidth=0.5, alpha=0.6)

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not f.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files supported'}), 400

    fname = f'{uuid.uuid4().hex}.csv'
    path = os.path.join(UPLOAD_FOLDER, fname)
    f.save(path)

    df = pd.read_csv(path)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    all_cols = df.columns.tolist()

    # Dataset overview plot
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    set_style(fig, axes)

    # Missing values heatmap
    miss = df.isnull().sum()
    miss = miss[miss > 0]
    if not miss.empty:
        axes[0].barh(miss.index.tolist(), miss.values, color=ACCENT)
        axes[0].set_title('Missing Values per Column', fontsize=10, fontweight='bold')
        axes[0].set_xlabel('Count')
    else:
        axes[0].text(0.5, 0.5, 'No Missing Values ✓', ha='center', va='center',
                     color=ACCENT2, fontsize=13, transform=axes[0].transAxes)
        axes[0].set_title('Missing Values', fontsize=10)
        axes[0].axis('off')

    # Dtype distribution
    dtypes = df.dtypes.astype(str).value_counts()
    wedges, texts, autotexts = axes[1].pie(
        dtypes.values, labels=dtypes.index.tolist(),
        autopct='%1.0f%%', colors=PALETTE[:len(dtypes)],
        textprops={'color': TEXT, 'fontsize': 8})
    for at in autotexts:
        at.set_color(DARK_BG)
        at.set_fontweight('bold')
    axes[1].set_title('Data Types Distribution', fontsize=10, fontweight='bold')
    fig.suptitle(f'Dataset Overview  •  {len(df):,} rows × {len(df.columns)} cols',
                 color=TEXT, fontsize=11, fontweight='bold', y=1.02)
    overview_plot = fig_to_b64(fig)

    # Correlation heatmap
    corr_plot = None
    num_df = df.select_dtypes(include=[np.number])
    if len(num_df.columns) >= 2:
        corr = num_df.corr()
        fig2, ax2 = plt.subplots(figsize=(max(6, len(corr)*0.7), max(5, len(corr)*0.6)))
        set_style(fig2, ax2)
        cmap = sns.diverging_palette(240, 10, as_cmap=True)
        sns.heatmap(corr, annot=True, fmt='.2f', cmap=cmap, ax=ax2,
                    annot_kws={'size': 7}, linewidths=0.5,
                    linecolor=GRID, cbar_kws={'shrink': 0.8})
        ax2.set_title('Correlation Matrix', color=TEXT, fontsize=11, fontweight='bold')
        ax2.tick_params(colors=TEXT, labelsize=7)
        corr_plot = fig_to_b64(fig2)

    return jsonify({
        'file': fname,
        'rows': len(df),
        'cols': len(df.columns),
        'numeric_cols': numeric_cols,
        'all_cols': all_cols,
        'dtypes': df.dtypes.astype(str).to_dict(),
        'head': df.head(6).to_html(classes='data-table', border=0, index=False),
        'overview_plot': overview_plot,
        'corr_plot': corr_plot,
        'describe': df.describe().round(3).to_html(classes='data-table', border=0),
    })


@app.route('/linear_regression', methods=['POST'])
def linear_regression():
    data = request.json
    path = os.path.join(UPLOAD_FOLDER, data['file'])
    target = data['target']
    features = data.get('features', [])

    df = pd.read_csv(path)
    df_proc = preprocess(df)

    if target not in df_proc.columns:
        return jsonify({'error': f'Target column "{target}" not found after preprocessing'}), 400

    if features:
        features = [f for f in features if f in df_proc.columns and f != target]
    if not features:
        features = [c for c in df_proc.columns if c != target]
    if not features:
        return jsonify({'error': 'No usable feature columns'}), 400

    X = df_proc[features].values
    y = df_proc[target].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mse  = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae  = mean_absolute_error(y_test, y_pred)
    r2   = r2_score(y_test, y_pred)
    coef = dict(zip(features, model.coef_.tolist()))

    # ── 4-panel plot ──────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    set_style(fig, axes.flatten())

    # 1. Actual vs Predicted
    ax = axes[0, 0]
    ax.scatter(y_test, y_pred, color=ACCENT, alpha=0.6, s=22, edgecolors='none')
    mn, mx = min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())
    ax.plot([mn, mx], [mn, mx], '--', color=ACCENT2, lw=1.5, label='Perfect fit')
    ax.set_xlabel('Actual'); ax.set_ylabel('Predicted')
    ax.set_title('Actual vs Predicted', fontweight='bold')
    ax.legend(fontsize=8, labelcolor=TEXT, facecolor=CARD_BG, edgecolor=GRID)

    # 2. Residuals
    ax = axes[0, 1]
    residuals = y_test - y_pred
    ax.scatter(y_pred, residuals, color=ACCENT3, alpha=0.6, s=22, edgecolors='none')
    ax.axhline(0, color=ACCENT2, lw=1.5, linestyle='--')
    ax.set_xlabel('Predicted'); ax.set_ylabel('Residuals')
    ax.set_title('Residual Plot', fontweight='bold')

    # 3. Residuals distribution
    ax = axes[1, 0]
    ax.hist(residuals, bins=30, color=ACCENT, edgecolor=DARK_BG, alpha=0.85)
    ax.set_xlabel('Residual'); ax.set_ylabel('Frequency')
    ax.set_title('Residuals Distribution', fontweight='bold')

    # 4. Top-10 feature importances
    ax = axes[1, 1]
    sorted_coef = sorted(coef.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
    names, vals = zip(*sorted_coef)
    colors_bar = [ACCENT if v > 0 else '#f43f5e' for v in vals]
    bars = ax.barh(list(names), list(vals), color=colors_bar)
    ax.set_xlabel('Coefficient')
    ax.set_title('Feature Coefficients (Top 10)', fontweight='bold')
    ax.axvline(0, color=TEXT, lw=0.7)

    fig.suptitle(f'Linear Regression  •  Target: {target}', color=TEXT,
                 fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    plot = fig_to_b64(fig)

    return jsonify({
        'metrics': {'R² Score': round(r2, 4), 'RMSE': round(rmse, 4),
                    'MAE': round(mae, 4), 'MSE': round(mse, 4)},
        'coefficients': coef,
        'n_features': len(features),
        'n_train': len(X_train),
        'n_test': len(X_test),
        'plot': plot,
    })


@app.route('/kmeans', methods=['POST'])
def kmeans():
    data = request.json
    path = os.path.join(UPLOAD_FOLDER, data['file'])
    k = int(data.get('k', 3))
    k = max(2, min(k, 10))

    df = pd.read_csv(path)
    df_proc = preprocess(df)

    if df_proc.shape[1] < 2:
        return jsonify({'error': 'Need at least 2 numeric columns'}), 400

    scaler = StandardScaler()
    X = scaler.fit_transform(df_proc.values)

    # Elbow
    inertias = []
    k_range = range(2, min(11, len(df_proc)))
    for ki in k_range:
        km = KMeans(n_clusters=ki, random_state=42, n_init=10)
        km.fit(X)
        inertias.append(km.inertia_)

    # Fit chosen k
    km_final = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km_final.fit_predict(X)

    # PCA for visualisation
    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X)
    var_exp = pca.explained_variance_ratio_

    # Cluster sizes
    unique, counts = np.unique(labels, return_counts=True)
    cluster_sizes = dict(zip(unique.tolist(), counts.tolist()))

    # ── 4-panel plot ──────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    set_style(fig, axes.flatten())

    # 1. Elbow
    ax = axes[0, 0]
    ax.plot(list(k_range), inertias, 'o-', color=ACCENT2, lw=2, markersize=6)
    ax.axvline(k, color=ACCENT3, lw=1.5, linestyle='--', label=f'k={k}')
    ax.set_xlabel('Number of Clusters (k)'); ax.set_ylabel('Inertia')
    ax.set_title('Elbow Method', fontweight='bold')
    ax.legend(fontsize=8, labelcolor=TEXT, facecolor=CARD_BG, edgecolor=GRID)

    # 2. PCA scatter
    ax = axes[0, 1]
    for i in range(k):
        mask = labels == i
        ax.scatter(X_2d[mask, 0], X_2d[mask, 1],
                   color=PALETTE[i % len(PALETTE)], s=20, alpha=0.7,
                   edgecolors='none', label=f'Cluster {i}')
    centers_2d = pca.transform(km_final.cluster_centers_)
    ax.scatter(centers_2d[:, 0], centers_2d[:, 1], s=150, c='white',
               marker='*', zorder=5, edgecolors=DARK_BG)
    ax.set_xlabel(f'PC1 ({var_exp[0]*100:.1f}%)')
    ax.set_ylabel(f'PC2 ({var_exp[1]*100:.1f}%)')
    ax.set_title(f'K-Means Clusters (PCA 2D) — k={k}', fontweight='bold')
    ax.legend(fontsize=7, labelcolor=TEXT, facecolor=CARD_BG, edgecolor=GRID,
              markerscale=1.5, ncol=2)

    # 3. Cluster sizes bar
    ax = axes[1, 0]
    ax.bar([f'Cluster {c}' for c in cluster_sizes],
           list(cluster_sizes.values()),
           color=PALETTE[:k], edgecolor=DARK_BG)
    ax.set_ylabel('Count'); ax.set_title('Cluster Sizes', fontweight='bold')
    for i, (c, v) in enumerate(cluster_sizes.items()):
        ax.text(i, v + max(cluster_sizes.values()) * 0.01, str(v),
                ha='center', va='bottom', color=TEXT, fontsize=8)

    # 4. Cluster mean heatmap (top features)
    ax = axes[1, 1]
    df_labeled = df_proc.copy()
    df_labeled['Cluster'] = labels
    means = df_labeled.groupby('Cluster').mean()
    top_feats = means.std().nlargest(min(8, len(means.columns))).index.tolist()
    means_top = means[top_feats]
    means_norm = (means_top - means_top.mean()) / (means_top.std() + 1e-9)
    sns.heatmap(means_norm, ax=ax, cmap='coolwarm', annot=True, fmt='.2f',
                annot_kws={'size': 7}, linewidths=0.5, linecolor=GRID,
                cbar_kws={'shrink': 0.8})
    ax.set_title('Cluster Profiles (Normalised)', fontweight='bold')
    ax.tick_params(colors=TEXT, labelsize=7)

    fig.suptitle(f'K-Means Clustering  •  k={k}', color=TEXT,
                 fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    plot = fig_to_b64(fig)

    return jsonify({
        'k': k,
        'cluster_sizes': cluster_sizes,
        'inertia': round(km_final.inertia_, 4),
        'variance_explained': round(float(sum(var_exp)) * 100, 2),
        'plot': plot,
    })


@app.route('/dbscan', methods=['POST'])
def dbscan():
    data = request.json
    path = os.path.join(UPLOAD_FOLDER, data['file'])
    eps    = float(data.get('eps', 0.5))
    min_s  = int(data.get('min_samples', 5))

    df = pd.read_csv(path)
    df_proc = preprocess(df)

    if df_proc.shape[1] < 2:
        return jsonify({'error': 'Need at least 2 numeric columns'}), 400

    scaler = StandardScaler()
    X = scaler.fit_transform(df_proc.values)

    db = DBSCAN(eps=eps, min_samples=min_s)
    labels = db.fit_predict(X)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise    = int(np.sum(labels == -1))
    n_core     = int(len(db.core_sample_indices_))

    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X)
    var_exp = pca.explained_variance_ratio_

    unique_labels = sorted(set(labels))

    # ── 4-panel plot ──────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    set_style(fig, axes.flatten())

    # 1. PCA scatter
    ax = axes[0, 0]
    for lbl in unique_labels:
        mask = labels == lbl
        if lbl == -1:
            ax.scatter(X_2d[mask, 0], X_2d[mask, 1], c='#475569',
                       s=12, alpha=0.5, edgecolors='none', label='Noise')
        else:
            ax.scatter(X_2d[mask, 0], X_2d[mask, 1],
                       color=PALETTE[lbl % len(PALETTE)],
                       s=20, alpha=0.75, edgecolors='none', label=f'Cluster {lbl}')
    ax.set_xlabel(f'PC1 ({var_exp[0]*100:.1f}%)')
    ax.set_ylabel(f'PC2 ({var_exp[1]*100:.1f}%)')
    ax.set_title(f'DBSCAN Clusters (PCA 2D)\neps={eps}, min_samples={min_s}', fontweight='bold')
    ax.legend(fontsize=7, labelcolor=TEXT, facecolor=CARD_BG, edgecolor=GRID,
              markerscale=1.5, ncol=2)

    # 2. Point classification pie
    ax = axes[0, 1]
    cluster_pts = int(np.sum(labels >= 0))
    sizes = [cluster_pts, n_noise]
    lbls  = [f'Clustered ({cluster_pts})', f'Noise ({n_noise})']
    wedge_colors = [ACCENT, '#f43f5e']
    if n_noise == 0:
        sizes = [cluster_pts]
        lbls  = [f'Clustered ({cluster_pts})']
        wedge_colors = [ACCENT]
    wedges, texts, autotexts = ax.pie(sizes, labels=lbls, autopct='%1.1f%%',
                                       colors=wedge_colors,
                                       textprops={'color': TEXT, 'fontsize': 8})
    for at in autotexts:
        at.set_color(DARK_BG); at.set_fontweight('bold')
    ax.set_title('Point Classification', fontweight='bold')

    # 3. Cluster size distribution
    ax = axes[1, 0]
    real_labels = [l for l in unique_labels if l != -1]
    if real_labels:
        sizes_arr = [int(np.sum(labels == l)) for l in real_labels]
        bar_colors = [PALETTE[l % len(PALETTE)] for l in real_labels]
        ax.bar([f'C{l}' for l in real_labels], sizes_arr, color=bar_colors, edgecolor=DARK_BG)
        for i, v in enumerate(sizes_arr):
            ax.text(i, v + max(sizes_arr) * 0.01, str(v), ha='center',
                    va='bottom', color=TEXT, fontsize=8)
        ax.set_ylabel('Points'); ax.set_title('Cluster Sizes', fontweight='bold')
    else:
        ax.text(0.5, 0.5, 'All points classified as noise', ha='center',
                va='center', color='#f43f5e', fontsize=10, transform=ax.transAxes)
        ax.axis('off')

    # 4. Cluster profiles heatmap
    ax = axes[1, 1]
    if real_labels and len(real_labels) > 0:
        df_labeled = df_proc.copy()
        df_labeled['Cluster'] = labels
        df_clust = df_labeled[df_labeled['Cluster'] != -1]
        means = df_clust.groupby('Cluster').mean()
        top_feats = means.std().nlargest(min(8, len(means.columns))).index.tolist()
        means_top = means[top_feats]
        means_norm = (means_top - means_top.mean()) / (means_top.std() + 1e-9)
        sns.heatmap(means_norm, ax=ax, cmap='coolwarm', annot=True, fmt='.2f',
                    annot_kws={'size': 7}, linewidths=0.5, linecolor=GRID,
                    cbar_kws={'shrink': 0.8})
        ax.set_title('Cluster Profiles (Normalised)', fontweight='bold')
        ax.tick_params(colors=TEXT, labelsize=7)
    else:
        ax.text(0.5, 0.5, 'No clusters to profile', ha='center', va='center',
                color=TEXT, fontsize=10, transform=ax.transAxes)
        ax.axis('off')

    fig.suptitle('DBSCAN Clustering', color=TEXT, fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    plot = fig_to_b64(fig)

    return jsonify({
        'n_clusters': n_clusters,
        'n_noise': n_noise,
        'n_core_points': n_core,
        'total_points': len(labels),
        'eps': eps,
        'min_samples': min_s,
        'plot': plot,
    })


if __name__ == '__main__':
    app.run(debug=True, port=5050)
