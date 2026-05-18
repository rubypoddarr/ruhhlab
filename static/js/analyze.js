const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const previewArea = document.getElementById('previewArea');
const previewImg = document.getElementById('previewImg');
const removeBtn = document.getElementById('removeBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsPlaceholder = document.getElementById('resultsPlaceholder');
const loadingState = document.getElementById('loadingState');
const resultsContent = document.getElementById('resultsContent');
const errorState = document.getElementById('errorState');
const resetBtn = document.getElementById('resetBtn');
const retryBtn = document.getElementById('retryBtn');

let selectedFile = null;

uploadZone.addEventListener('click', () => fileInput.click());
uploadZone.addEventListener('dragover', (e) => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
});
fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

function handleFile(file) {
    const allowed = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/bmp'];
    if (!allowed.includes(file.type)) {
        showError('Invalid file type. Please upload PNG, JPG, JPEG, WEBP, or BMP.');
        return;
    }
    if (file.size > 10 * 1024 * 1024) {
        showError('File is too large. Maximum size is 10MB.');
        return;
    }
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        uploadZone.style.display = 'none';
        previewArea.style.display = 'block';
        analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

removeBtn.addEventListener('click', () => {
    selectedFile = null;
    fileInput.value = '';
    previewImg.src = '';
    previewArea.style.display = 'none';
    uploadZone.style.display = 'flex';
    analyzeBtn.disabled = true;
    resetResults();
});

function resetResults() {
    resultsPlaceholder.style.display = 'flex';
    loadingState.style.display = 'none';
    resultsContent.style.display = 'none';
    errorState.style.display = 'none';
}

function showError(msg) {
    resultsPlaceholder.style.display = 'none';
    loadingState.style.display = 'none';
    resultsContent.style.display = 'none';
    errorState.style.display = 'flex';
    document.getElementById('errorText').textContent = msg;
}

retryBtn.addEventListener('click', resetResults);
resetBtn.addEventListener('click', () => {
    removeBtn.click();
});

const steps = ['step1', 'step2', 'step3', 'step4'];
let stepInterval = null;

function animateSteps() {
    let i = 0;
    steps.forEach(id => document.getElementById(id).classList.remove('active'));
    document.getElementById(steps[0]).classList.add('active');
    stepInterval = setInterval(() => {
        i++;
        if (i < steps.length) {
            document.getElementById(steps[i]).classList.add('active');
        } else {
            clearInterval(stepInterval);
        }
    }, 900);
}

analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    analyzeBtn.disabled = true;
    resultsPlaceholder.style.display = 'none';
    loadingState.style.display = 'flex';
    resultsContent.style.display = 'none';
    errorState.style.display = 'none';
    animateSteps();

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
        const res = await fetch('/analyze', { method: 'POST', body: formData });
        const data = await res.json();
        clearInterval(stepInterval);

        if (!res.ok || data.error && !data.success) {
            showError(data.error || 'Analysis failed. Please try again.');
            analyzeBtn.disabled = false;
            return;
        }

        renderResults(data);
    } catch (err) {
        clearInterval(stepInterval);
        showError('Network error. Please check your connection and try again.');
        analyzeBtn.disabled = false;
    }
});

function renderResults(data) {
    loadingState.style.display = 'none';
    resultsContent.style.display = 'flex';
    analyzeBtn.disabled = false;

    if (data.input_image) document.getElementById('inputImgResult').src = data.input_image;
    if (data.output_image) {
        document.getElementById('outputImgResult').src = data.output_image;
    } else if (data.input_image) {
        document.getElementById('outputImgResult').src = data.input_image;
    }

    const objectsList = document.getElementById('objectsList');
    objectsList.innerHTML = '';
    if (data.objects && data.objects.length > 0) {
        data.objects.forEach(obj => {
            const item = document.createElement('div');
            item.className = 'object-item';
            const pct = Math.round(obj.confidence * 100);
            item.innerHTML = `
                <span class="obj-label">${obj.label}</span>
                <div class="obj-bar-wrap"><div class="obj-bar" style="width:${pct}%"></div></div>
                <span class="obj-conf">${obj.confidence.toFixed(2)}</span>
            `;
            objectsList.appendChild(item);
        });
    } else {
        objectsList.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">No objects detected above threshold.</p>';
    }

    document.getElementById('sceneText').textContent = data.scene || 'No scene interpretation available.';

    const relationsList = document.getElementById('relationsList');
    const relationsBlock = document.getElementById('relationsBlock');
    relationsList.innerHTML = '';
    if (data.relationships && data.relationships.length > 0) {
        relationsBlock.style.display = 'block';
        data.relationships.forEach(r => {
            const li = document.createElement('li');
            li.textContent = r;
            relationsList.appendChild(li);
        });
    } else {
        relationsBlock.style.display = 'none';
    }

    document.getElementById('insightText').textContent = data.insight || '';
}
