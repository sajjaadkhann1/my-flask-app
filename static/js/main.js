document.addEventListener('DOMContentLoaded', () => {
    // ─── Global State ────────────────────────────────────────────────────────
    let currentFile = null;
    let numericCols = [];
    let allCols = [];

    // ─── DOM Elements ────────────────────────────────────────────────────────
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('csv-file-input');
    const uploadSection = document.getElementById('upload-section');
    const uploadProgressContainer = document.getElementById('upload-progress-container');
    const uploadProgressBar = document.getElementById('upload-progress-bar');
    const uploadStatusText = document.getElementById('upload-status-text');
    const dashboardContent = document.getElementById('dashboard-content');
    const btnUploadDifferent = document.getElementById('btn-upload-different');

    // Meta elements
    const metaFilename = document.getElementById('meta-filename');
    const metaRows = document.getElementById('meta-rows');
    const metaCols = document.getElementById('meta-cols');
    const dtypesTbody = document.getElementById('dtypes-tbody');

    // Plots
    const imgOverviewPlot = document.getElementById('img-overview-plot');
    const imgCorrPlot = document.getElementById('img-corr-plot');
    const noCorrMsg = document.getElementById('no-corr-msg');

    // Tables
    const btnTablePreview = document.getElementById('btn-table-preview');
    const btnTableStats = document.getElementById('btn-table-stats');
    const tablePreviewHead = document.getElementById('table-preview-head');
    const tablePreviewStats = document.getElementById('table-preview-stats');

    // Tab buttons & panes
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    // ML - Regression
    const regTargetSelect = document.getElementById('reg-target-select');
    const regFeaturesContainer = document.getElementById('reg-features-container');
    const btnRegSelectAll = document.getElementById('btn-reg-select-all');
    const btnRegClearAll = document.getElementById('btn-reg-clear-all');
    const btnRunRegression = document.getElementById('btn-run-regression');
    const regLoader = document.getElementById('regression-loader');
    const regEmptyState = document.getElementById('regression-empty-state');
    const regResults = document.getElementById('regression-results');
    const regValR2 = document.getElementById('reg-val-r2');
    const regValRmse = document.getElementById('reg-val-rmse');
    const regValMae = document.getElementById('reg-val-mae');
    const regValMse = document.getElementById('reg-val-mse');
    const imgRegPlot = document.getElementById('img-reg-plot');
    const regCoefTbody = document.getElementById('reg-coef-tbody');

    // ML - K-Means
    const kmeansKSlider = document.getElementById('kmeans-k-slider');
    const kmeansKVal = document.getElementById('kmeans-k-val');
    const btnRunKmeans = document.getElementById('btn-run-kmeans');
    const kmeansLoader = document.getElementById('kmeans-loader');
    const kmeansEmptyState = document.getElementById('kmeans-empty-state');
    const kmeansResults = document.getElementById('kmeans-results');
    const kmValInertia = document.getElementById('km-val-inertia');
    const kmValVariance = document.getElementById('km-val-variance');
    const kmValK = document.getElementById('km-val-k');
    const imgKmeansPlot = document.getElementById('img-kmeans-plot');
    const kmeansSizesTbody = document.getElementById('kmeans-sizes-tbody');

    // ML - DBSCAN
    const dbscanEpsSlider = document.getElementById('dbscan-eps-slider');
    const dbscanEpsVal = document.getElementById('dbscan-eps-val');
    const dbscanSamplesSlider = document.getElementById('dbscan-samples-slider');
    const dbscanSamplesVal = document.getElementById('dbscan-samples-val');
    const btnRunDbscan = document.getElementById('btn-run-dbscan');
    const dbscanLoader = document.getElementById('dbscan-loader');
    const dbscanEmptyState = document.getElementById('dbscan-empty-state');
    const dbscanResults = document.getElementById('dbscan-results');
    const dbValClusters = document.getElementById('db-val-clusters');
    const dbValCore = document.getElementById('db-val-core');
    const dbValNoise = document.getElementById('db-val-noise');
    const dbValTotal = document.getElementById('db-val-total');
    const imgDbscanPlot = document.getElementById('img-dbscan-plot');

    // ─── Drag & Drop Event Listeners ──────────────────────────────────────────
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) {
            handleFileUpload(files[0]);
        }
    });

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFileUpload(fileInput.files[0]);
        }
    });

    // ─── Tab Switching Logic ──────────────────────────────────────────────────
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            
            // Deactivate all
            tabButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));

            // Activate current
            btn.classList.add('active');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // Table view toggle (Head vs Stats)
    const toggleTableView = (showHead) => {
        if (showHead) {
            btnTablePreview.classList.add('active');
            btnTableStats.classList.remove('active');
            tablePreviewHead.classList.add('active');
            tablePreviewStats.classList.remove('active');
        } else {
            btnTablePreview.classList.remove('active');
            btnTableStats.classList.add('active');
            tablePreviewHead.classList.remove('active');
            tablePreviewStats.classList.add('active');
        }
    };

    btnTablePreview.addEventListener('click', () => toggleTableView(true));
    btnTableStats.addEventListener('click', () => toggleTableView(false));

    // Slider display updates
    kmeansKSlider.addEventListener('input', () => {
        kmeansKVal.textContent = kmeansKSlider.value;
    });

    dbscanEpsSlider.addEventListener('input', () => {
        dbscanEpsVal.textContent = dbscanEpsSlider.value;
    });

    dbscanSamplesSlider.addEventListener('input', () => {
        dbscanSamplesVal.textContent = dbscanSamplesSlider.value;
    });

    // ─── File Upload Handler ──────────────────────────────────────────────────
    function handleFileUpload(file) {
        if (!file.name.endsWith('.csv')) {
            alert('Please select a valid CSV file.');
            return;
        }

        currentFile = file;

        // Reset UI progress states
        uploadProgressContainer.classList.remove('hidden');
        uploadProgressBar.style.width = '0%';
        uploadStatusText.textContent = 'Uploading dataset...';

        // Fake progressive loading feel
        let progress = 0;
        const interval = setInterval(() => {
            if (progress < 85) {
                progress += Math.random() * 15;
                uploadProgressBar.style.width = `${Math.min(progress, 85)}%`;
            }
        }, 120);

        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            clearInterval(interval);
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Server error during upload'); });
            }
            return response.json();
        })
        .then(data => {
            uploadProgressBar.style.width = '100%';
            uploadStatusText.textContent = 'Successfully processed!';
            
            setTimeout(() => {
                initializeDashboard(data);
            }, 400);
        })
        .catch(error => {
            clearInterval(interval);
            uploadProgressContainer.classList.add('hidden');
            alert(`Error: ${error.message}`);
        });
    }

    // Initialize Dashboard UI with uploaded dataset details
    function initializeDashboard(data) {
        // Save references
        currentFile = data.file;
        numericCols = data.numeric_cols;
        allCols = data.all_cols;

        // Populate side panel metadata
        metaFilename.textContent = fileInput.files[0]?.name || "Dataset";
        metaRows.textContent = data.rows.toLocaleString();
        metaCols.textContent = data.cols.toLocaleString();

        // Populate column types table
        dtypesTbody.innerHTML = '';
        Object.entries(data.dtypes).forEach(([col, dtype]) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td><strong>${col}</strong></td><td><span class="file-limits">${dtype}</span></td>`;
            dtypesTbody.appendChild(tr);
        });

        // Set plots
        imgOverviewPlot.src = `data:image/png;base64,${data.overview_plot}`;
        if (data.corr_plot) {
            imgCorrPlot.classList.remove('hidden');
            noCorrMsg.classList.add('hidden');
            imgCorrPlot.src = `data:image/png;base64,${data.corr_plot}`;
        } else {
            imgCorrPlot.classList.add('hidden');
            noCorrMsg.classList.remove('hidden');
        }

        // Set raw head & stats HTML tables
        tablePreviewHead.innerHTML = data.head;
        tablePreviewStats.innerHTML = data.describe;
        toggleTableView(true);

        // Populate Machine Learning configs
        setupMLConfigs();

        // Transition UI state
        uploadSection.classList.add('hidden');
        uploadProgressContainer.classList.add('hidden');
        dashboardContent.classList.remove('hidden');

        // Reset any leftover results states
        resetMLResults();
    }

    // Set up checkboxes & selectors in settings panel
    function setupMLConfigs() {
        // Target dropdown for regression
        regTargetSelect.innerHTML = '';
        numericCols.forEach(col => {
            const opt = document.createElement('option');
            opt.value = col;
            opt.textContent = col;
            regTargetSelect.appendChild(opt);
        });

        // Feature checkboxes for regression
        regFeaturesContainer.innerHTML = '';
        numericCols.forEach(col => {
            const div = document.createElement('div');
            div.className = 'checkbox-wrapper';
            div.innerHTML = `
                <label class="checkbox-label">
                    <input type="checkbox" name="reg-feature" value="${col}" checked>
                    <span>${col}</span>
                </label>
            `;
            regFeaturesContainer.appendChild(div);
        });

        // Automatically update options when target changes (should not be in features)
        regTargetSelect.addEventListener('change', () => {
            const selectedTarget = regTargetSelect.value;
            const checkboxes = regFeaturesContainer.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(chk => {
                if (chk.value === selectedTarget) {
                    chk.checked = false;
                    chk.disabled = true;
                    chk.closest('.checkbox-label').style.opacity = '0.4';
                } else {
                    chk.disabled = false;
                    chk.closest('.checkbox-label').style.opacity = '1.0';
                }
            });
        });
        
        // Initial trigger
        regTargetSelect.dispatchEvent(new Event('change'));
    }

    btnRegSelectAll.addEventListener('click', () => {
        const target = regTargetSelect.value;
        const checkboxes = regFeaturesContainer.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(chk => {
            if (chk.value !== target) {
                chk.checked = true;
            }
        });
    });

    btnRegClearAll.addEventListener('click', () => {
        const checkboxes = regFeaturesContainer.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(chk => {
            chk.checked = false;
        });
    });

    function resetMLResults() {
        // Regression reset
        regEmptyState.classList.remove('hidden');
        regResults.classList.remove('show');
        regResults.classList.add('hidden');
        regLoader.classList.add('hidden');

        // K-Means reset
        kmeansEmptyState.classList.remove('hidden');
        kmeansResults.classList.remove('show');
        kmeansResults.classList.add('hidden');
        kmeansLoader.classList.add('hidden');

        // DBSCAN reset
        dbscanEmptyState.classList.remove('hidden');
        dbscanResults.classList.remove('show');
        dbscanResults.classList.add('hidden');
        dbscanLoader.classList.add('hidden');
    }

    btnUploadDifferent.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';
        dashboardContent.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        uploadProgressBar.style.width = '0%';
    });

    // ─── Run Linear Regression ──────────────────────────────────────────────
    btnRunRegression.addEventListener('click', () => {
        if (!currentFile) return;

        const target = regTargetSelect.value;
        const selectedFeatures = [];
        const checkboxes = regFeaturesContainer.querySelectorAll('input[type="checkbox"]:checked');
        checkboxes.forEach(chk => {
            selectedFeatures.push(chk.value);
        });

        if (selectedFeatures.length === 0) {
            alert('Please select at least one predictor feature.');
            return;
        }

        // Toggle state
        regEmptyState.classList.add('hidden');
        regResults.classList.remove('show');
        regResults.classList.add('hidden');
        regLoader.classList.remove('hidden');

        fetch('/linear_regression', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file: currentFile,
                target: target,
                features: selectedFeatures
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Linear Regression failed'); });
            }
            return response.json();
        })
        .then(data => {
            // Update UI metrics
            regValR2.textContent = data.metrics['R² Score'].toFixed(4);
            regValRmse.textContent = data.metrics['RMSE'].toFixed(4);
            regValMae.textContent = data.metrics['MAE'].toFixed(4);
            regValMse.textContent = data.metrics['MSE'].toFixed(4);

            // Set base64 plot
            imgRegPlot.src = `data:image/png;base64,${data.plot}`;

            // Populate coefficients table
            regCoefTbody.innerHTML = '';
            
            // Sort coefficients by absolute value descending
            const sortedCoefs = Object.entries(data.coefficients).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));
            sortedCoefs.forEach(([feat, val]) => {
                const tr = document.createElement('tr');
                const badgeClass = val >= 0 ? 'text-indigo' : 'text-red';
                tr.innerHTML = `<td><strong>${feat}</strong></td><td><span class="${badgeClass}">${val.toFixed(5)}</span></td>`;
                regCoefTbody.appendChild(tr);
            });

            // Transition results cards
            regLoader.classList.add('hidden');
            regResults.classList.remove('hidden');
            setTimeout(() => {
                regResults.classList.add('show');
            }, 50);
        })
        .catch(err => {
            regLoader.classList.add('hidden');
            regEmptyState.classList.remove('hidden');
            alert(`Error: ${err.message}`);
        });
    });

    // ─── Run K-Means Clustering ─────────────────────────────────────────────
    btnRunKmeans.addEventListener('click', () => {
        if (!currentFile) return;

        const k = kmeansKSlider.value;

        // Toggle state
        kmeansEmptyState.classList.add('hidden');
        kmeansResults.classList.remove('show');
        kmeansResults.classList.add('hidden');
        kmeansLoader.classList.remove('hidden');

        fetch('/kmeans', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file: currentFile,
                k: parseInt(k)
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'K-Means failed'); });
            }
            return response.json();
        })
        .then(data => {
            // Update metrics
            kmValInertia.textContent = data.inertia.toLocaleString(undefined, {maximumFractionDigits: 2});
            kmValVariance.textContent = `${data.variance_explained.toFixed(2)}%`;
            kmValK.textContent = data.k;

            // Update Plot
            imgKmeansPlot.src = `data:image/png;base64,${data.plot}`;

            // Populate cluster sizes table
            kmeansSizesTbody.innerHTML = '';
            Object.entries(data.cluster_sizes).forEach(([clusterId, count]) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td><i class="fa-solid fa-circle" style="color: ${getClusterColor(parseInt(clusterId))}; margin-right: 5px;"></i> Cluster ${clusterId}</td><td><strong>${count.toLocaleString()}</strong></td>`;
                kmeansSizesTbody.appendChild(tr);
            });

            // Transition UI
            kmeansLoader.classList.add('hidden');
            kmeansResults.classList.remove('hidden');
            setTimeout(() => {
                kmeansResults.classList.add('show');
            }, 50);
        })
        .catch(err => {
            kmeansLoader.classList.add('hidden');
            kmeansEmptyState.classList.remove('hidden');
            alert(`Error: ${err.message}`);
        });
    });

    // Color palette mapping to match matplotlib styling
    function getClusterColor(idx) {
        const palette = ['#6366f1', '#22d3ee', '#f59e0b', '#f43f5e', '#a3e635', '#fb923c',
                         '#c084fc', '#34d399', '#f472b6', '#60a5fa'];
        return palette[idx % palette.length];
    }

    // ─── Run DBSCAN Clustering ──────────────────────────────────────────────
    btnRunDbscan.addEventListener('click', () => {
        if (!currentFile) return;

        const eps = dbscanEpsSlider.value;
        const minSamples = dbscanSamplesSlider.value;

        // Toggle state
        dbscanEmptyState.classList.add('hidden');
        dbscanResults.classList.remove('show');
        dbscanResults.classList.add('hidden');
        dbscanLoader.classList.remove('hidden');

        fetch('/dbscan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file: currentFile,
                eps: parseFloat(eps),
                min_samples: parseInt(minSamples)
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'DBSCAN failed'); });
            }
            return response.json();
        })
        .then(data => {
            // Update metrics
            dbValClusters.textContent = data.n_clusters;
            dbValCore.textContent = data.n_core_points.toLocaleString();
            dbValNoise.textContent = data.n_noise.toLocaleString();
            dbValTotal.textContent = data.total_points.toLocaleString();

            // Update Plot
            imgDbscanPlot.src = `data:image/png;base64,${data.plot}`;

            // Transition UI
            dbscanLoader.classList.add('hidden');
            dbscanResults.classList.remove('hidden');
            setTimeout(() => {
                dbscanResults.classList.add('show');
            }, 50);
        })
        .catch(err => {
            dbscanLoader.classList.add('hidden');
            dbscanEmptyState.classList.remove('hidden');
            alert(`Error: ${err.message}`);
        });
    });

});
