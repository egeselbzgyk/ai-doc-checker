class DocChecker {
    constructor() {
        this.referenceFiles = [];
        this.submissionFile = null;
        this.useDatabase = false;
        this.maxFileSize = 10 * 1024 * 1024; // 10MB
        this.maxImages = 5;
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Checkbox für Database usage
        const databaseCheckbox = document.getElementById('useDatabase');
        databaseCheckbox.addEventListener('change', (e) => {
            this.toggleDatabaseMode(e.target.checked);
        });

        // Reference files
        const referenceFiles = document.getElementById('referenceFiles');
        referenceFiles.addEventListener('change', (e) => {
            this.handleReferenceFiles(e.target.files);
        });

        // Submission file
        const submissionFile = document.getElementById('submissionFile');
        submissionFile.addEventListener('change', (e) => {
            this.handleSubmissionFile(e.target.files[0]);
        });

        // Drag & Drop
        this.setupDragAndDrop();

        // Evaluate button
        const evaluateBtn = document.getElementById('evaluateBtn');
        evaluateBtn.addEventListener('click', () => {
            this.startEvaluation();
        });
    }

    setupDragAndDrop() {
        const dropZones = ['referenceDropZone', 'submissionDropZone'];
        
        dropZones.forEach(zoneId => {
            const zone = document.getElementById(zoneId);
            
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.classList.add('drag-over');
            });

            zone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                zone.classList.remove('drag-over');
            });

            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                zone.classList.remove('drag-over');
                
                const files = Array.from(e.dataTransfer.files);
                
                if (zoneId === 'referenceDropZone' && !this.useDatabase) {
                    this.handleReferenceFiles(files);
                } else if (zoneId === 'submissionDropZone') {
                    this.handleSubmissionFile(files[0]);
                }
            });
        });
    }

    toggleDatabaseMode(useDb) {
        this.useDatabase = useDb;
        const referenceUpload = document.getElementById('referenceUpload');
        const databaseInfo = document.getElementById('databaseInfo');

        if (useDb) {
            referenceUpload.style.display = 'none';
            databaseInfo.style.display = 'block';
            this.referenceFiles = [];
            this.updateReferenceFileList();
        } else {
            referenceUpload.style.display = 'block';
            databaseInfo.style.display = 'none';
        }
        
        this.updateEvaluateButton();
    }

    handleReferenceFiles(files) {
        if (this.useDatabase) return;

        const newFiles = Array.from(files);
        
        // Validierung
        for (const file of newFiles) {
            if (!this.validateFile(file, ['zip', 'pdf', 'jpg', 'jpeg', 'png'])) {
                this.showError(`Ungültiger Dateityp: ${file.name}`);
                continue;
            }

            if (file.size > this.maxFileSize) {
                this.showError(`Datei zu groß: ${file.name} (max. 10MB)`);
                continue;
            }

            // Bild-Limit prüfen
            const imageTypes = ['jpg', 'jpeg', 'png'];
            const currentImages = this.referenceFiles.filter(f => 
                imageTypes.includes(f.name.split('.').pop().toLowerCase())
            ).length;
            
            const newImages = newFiles.filter(f => 
                imageTypes.includes(f.name.split('.').pop().toLowerCase())
            ).length;

            if (currentImages + newImages > this.maxImages) {
                this.showError(`Maximal ${this.maxImages} Bilder erlaubt`);
                continue;
            }

            // ZIP/PDF Limit (nur eines)
            const archiveTypes = ['zip', 'pdf'];
            const hasArchive = this.referenceFiles.some(f => 
                archiveTypes.includes(f.name.split('.').pop().toLowerCase())
            );
            
            const isArchive = archiveTypes.includes(file.name.split('.').pop().toLowerCase());
            
            if (hasArchive && isArchive) {
                this.showError('Nur eine ZIP- oder PDF-Datei erlaubt');
                continue;
            }

            this.referenceFiles.push(file);
        }

        this.updateReferenceFileList();
        this.updateEvaluateButton();
    }

    handleSubmissionFile(file) {
        if (!file) return;

        if (!this.validateFile(file, ['zip'])) {
            this.showError('Nur ZIP-Dateien für Abgaben erlaubt');
            return;
        }

        if (file.size > this.maxFileSize) {
            this.showError(`Datei zu groß: ${file.name} (max. 10MB)`);
            return;
        }

        this.submissionFile = file;
        this.updateSubmissionFileList();
        this.updateEvaluateButton();
    }

    validateFile(file, allowedExtensions) {
        const extension = file.name.split('.').pop().toLowerCase();
        return allowedExtensions.includes(extension);
    }

    updateReferenceFileList() {
        const container = document.getElementById('referenceFileList');
        container.innerHTML = '';

        this.referenceFiles.forEach((file, index) => {
            const fileItem = this.createFileItem(file, () => {
                this.referenceFiles.splice(index, 1);
                this.updateReferenceFileList();
                this.updateEvaluateButton();
            });
            container.appendChild(fileItem);
        });
    }

    updateSubmissionFileList() {
        const container = document.getElementById('submissionFileList');
        container.innerHTML = '';

        if (this.submissionFile) {
            const fileItem = this.createFileItem(this.submissionFile, () => {
                this.submissionFile = null;
                this.updateSubmissionFileList();
                this.updateEvaluateButton();
            });
            container.appendChild(fileItem);
        }
    }

    createFileItem(file, onRemove) {
        const item = document.createElement('div');
        item.className = 'file-item';

        const fileIcon = this.getFileIcon(file.name);
        const fileSize = this.formatFileSize(file.size);

        item.innerHTML = `
            <div class="file-info">
                <div class="file-icon">${fileIcon}</div>
                <div class="file-details">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${fileSize}</div>
                </div>
            </div>
            <button class="remove-file">✕</button>
        `;

        item.querySelector('.remove-file').addEventListener('click', onRemove);
        return item;
    }

    getFileIcon(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        const icons = {
            'zip': '📦',
            'pdf': '📄',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'png': '🖼️'
        };
        return icons[extension] || '📁';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    updateEvaluateButton() {
        const btn = document.getElementById('evaluateBtn');
        const hasReference = this.useDatabase || this.referenceFiles.length > 0;
        const hasSubmission = this.submissionFile !== null;
        
        btn.disabled = !(hasReference && hasSubmission);
    }

    async startEvaluation() {
        const btn = document.getElementById('evaluateBtn');
        const btnText = btn.querySelector('.btn-text');
        const spinner = btn.querySelector('.loading-spinner');
        
        // Loading state
        btn.classList.add('loading');
        btn.disabled = true;
        btnText.textContent = 'Bewertung läuft...';
        spinner.style.display = 'inline-block';

        try {
            const formData = new FormData();
            
            // Submission file
            formData.append('submission', this.submissionFile);
            
            // Reference mode
            formData.append('use_database', this.useDatabase);
            
            // Reference files if not using database
            if (!this.useDatabase) {
                this.referenceFiles.forEach((file, index) => {
                    formData.append(`reference_${index}`, file);
                });
            }

            const response = await fetch('/api/evaluate', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            this.displayResults(result);

        } catch (error) {
            console.error('Bewertungsfehler:', error);
            this.showError(`Bewertungsfehler: ${error.message}`);
        } finally {
            // Reset button
            btn.classList.remove('loading');
            btn.disabled = false;
            btnText.textContent = 'Bewertung starten';
            spinner.style.display = 'none';
            this.updateEvaluateButton();
        }
    }

    displayResults(result) {
        const resultsSection = document.getElementById('resultsSection');
        const scoreValue = document.getElementById('scoreValue');
        const scoreStatus = document.getElementById('scoreStatus');
        const detailedResults = document.getElementById('detailedResults');



        // Overall score
        scoreValue.textContent = Math.round(result.overall_score || 0);
        
        const statusText = scoreStatus.querySelector('.status-text');
        const passed = result.passed || false;
        
        statusText.textContent = passed ? 'BESTANDEN' : 'NICHT BESTANDEN';
        statusText.className = `status-text ${passed ? 'status-passed' : 'status-failed'}`;

        // Detailed results
        detailedResults.innerHTML = '';
        
        if (result.evaluations && result.evaluations.length > 0) {
            result.evaluations.forEach((evaluation, index) => {
                    const resultItem = this.createResultItem(evaluation);
                    detailedResults.appendChild(resultItem);
            });
        }

        // Show results
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    createResultItem(evaluation) {
        const item = document.createElement('div');
        item.className = 'result-item';

        const category = evaluation.category || 'Unbekannt';
        const score = evaluation.score || 0;
        const evalData = evaluation.evaluation || {};
        
        // Feedback bilgileri detailed_comparisons içinde
        let details = {};
        if (evalData.detailed_comparisons && evalData.detailed_comparisons.length > 0) {
            const firstComparison = evalData.detailed_comparisons[0];
            if (firstComparison.evaluation && firstComparison.evaluation.gesamt_bewertung) {
                details = firstComparison.evaluation.gesamt_bewertung;
            } else {
                details = firstComparison.evaluation || {};
            }
        } else {
            details = evalData.gesamt_bewertung || evalData;
        }

        const scoreClass = score >= 70 ? 'good' : score >= 50 ? 'medium' : 'bad';





        item.innerHTML = `
            <div class="result-header">
                <div class="result-category">${category}</div>
                <div class="result-score ${scoreClass}">${score}/100</div>
            </div>
            <div class="result-feedback">
                <div class="feedback-text">
                    <strong>Bewertung:</strong><br>
                    ${details.feedback || 'Kein spezifisches Feedback verfügbar'}
                </div>
                
                <div class="feedback-lists">
                    <div class="feedback-section strengths">
                        <h4>Stärken</h4>
                        <ul class="feedback-list">
                            ${(details.staerken || ['Keine spezifischen Stärken angegeben']).map(item => `<li>${item}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="feedback-section improvements">
                        <h4>Verbesserungen</h4>
                        <ul class="feedback-list">
                            ${(details.verbesserungen || ['Keine spezifischen Verbesserungen angegeben']).map(item => `<li>${item}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;

        return item;
    }

    formatSectionName(key) {
        const names = {
            'struktur_vergleich': 'Struktur & Aufbau',
            'visueller_vergleich': 'Visuelle Qualität',
            'funktionale_elemente': 'Funktionalität',
            'sap_kontext': 'SAP-Kontext',
            'diagramm_vergleich': 'Diagramm-Struktur',
            'technische_umsetzung': 'Technische Umsetzung',
            'sap_bw_korrektheit': 'SAP BW Korrektheit',
            'verstaendlichkeit': 'Verständlichkeit',
            'prozess_vergleich': 'Prozess-Vergleich',
            'konfiguration': 'Konfiguration',
            'monitoring': 'Monitoring',
            'sap_standard': 'SAP Standard',
            'mapping_vergleich': 'Mapping',
            'business_logik': 'Business-Logik',
            'dokumentation': 'Dokumentation',
            'technische_definition': 'Definition',
            'metadaten': 'Metadaten',
            'integration': 'Integration',
            'query_struktur': 'Query-Struktur',
            'darstellung': 'Darstellung',
            'fachliche_korrektheit': 'Fachliche Korrektheit'
        };
        return names[key] || key;
    }

    formatCriterionName(key) {
        const names = {
            'tabellenstruktur_korrekt': 'Struktur OK',
            'spalten_angemessen': 'Spalten OK',
            'header_vorhanden': 'Header OK',
            'formatierung_angemessen': 'Format OK',
            'lesbarkeit_gut': 'Lesbar',
            'professionell': 'Professionell',
            'formeln_korrekt': 'Formeln OK',
            'berechnungen_richtig': 'Berechnungen OK',
            'vollstaendig': 'Vollständig',
            'kontext_korrekt': 'Kontext OK',
            'business_sinnvoll': 'Business OK',
            'integration_erkennbar': 'Integration OK'
        };
        return names[key] || key.replace(/_/g, ' ');
    }

    showError(message) {
        // Einfache Fehleranzeige
        alert(message);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DocChecker();
}); 