// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const uploadArea = document.getElementById('uploadArea');
const analyzeBtn = document.getElementById('analyzeBtn');
const errorMsg = document.getElementById('errorMsg');
const resultsContainer = document.getElementById('results');
const insightsCard = document.getElementById('insightsCard');
const historyBtn = document.getElementById('historyBtn');
const historyModal = new bootstrap.Modal(document.getElementById('historyModal'));
const historyList = document.getElementById('historyList');

// State
let currentUser = {
  name: "Guest", // This would come from your auth system
  history: [] // This would be loaded from your backend
};

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
  // Set username in navbar
  document.getElementById('username').textContent = currentUser.name;

  // Set up file upload area
  setupFileUpload();

  // Load history (in a real app, this would be from your backend)
  loadHistory();
});

// File Upload Handling
function setupFileUpload() {
  const fileInput = document.querySelector('input[type="file"]');

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      const fileName = e.target.files[0].name;
      uploadArea.innerHTML = `
        <i class="bi bi-file-earmark-pdf"></i>
        <p>${fileName}</p>
        <small class="text-muted">Click to change file</small>
      `;
    }
  });

  // Drag and drop functionality
  uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#64b5f6';
    uploadArea.style.backgroundColor = 'rgba(100, 181, 246, 0.1)';
  });

  uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = 'rgba(100, 181, 246, 0.3)';
    uploadArea.style.backgroundColor = 'rgba(10, 14, 33, 0.3)';
  });

  uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'rgba(100, 181, 246, 0.3)';
    uploadArea.style.backgroundColor = 'rgba(10, 14, 33, 0.3)';

    if (e.dataTransfer.files.length > 0) {
      fileInput.files = e.dataTransfer.files;
      const fileName = e.dataTransfer.files[0].name;
      uploadArea.innerHTML = `
        <i class="bi bi-file-earmark-pdf"></i>
        <p>${fileName}</p>
        <small class="text-muted">Click to change file</small>
      `;
    }
  });
}

// Form Submission
uploadForm.addEventListener('submit', async function(e) {
  e.preventDefault();

  // Reset UI
  errorMsg.style.display = 'none';
  resultsContainer.style.display = 'none';
  insightsCard.style.display = 'none';

  // Show loading state
  analyzeBtn.disabled = true;
  const btnText = analyzeBtn.querySelector('.btn-text');
  const originalText = btnText.textContent;
  btnText.textContent = 'Analyzing...';

  try {
    const formData = new FormData();
    formData.append('resume', document.getElementById('resume').files[0]);
    formData.append('jobdesc', document.getElementById('jobdesc').value);

    const response = await fetch('https://alignai.onrender.com/analyze', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Analysis failed');
    }

    // Display results
    displayResults(data);

    // Add to history (in a real app, this would be saved to your backend)
    addToHistory(data);

  } catch (err) {
    errorMsg.textContent = 'Error: ' + err.message;
    errorMsg.style.display = 'block';
  } finally {
    analyzeBtn.disabled = false;
    const btnText = analyzeBtn.querySelector('.btn-text');
    btnText.textContent = originalText;
  }
});

// Display Results
function displayResults(data) {
  // Basic scores
  document.getElementById('finalScore').textContent = data.final_score;
  document.getElementById('tfidfScore').textContent = data.tfidf_score;
  document.getElementById('bertScore').textContent = data.bert_score;
  document.getElementById('skillScore').textContent = data.skill_score;
  document.getElementById('atisScore').textContent = data.atis_score;

  // Progress bar
  const scoreBar = document.getElementById('scoreBar');
  scoreBar.style.width = `${data.final_score}%`;

  // Color coding
  let feedbackText = '';
  if (data.final_score > 75) {
    scoreBar.style.background = 'linear-gradient(90deg, var(--primary), var(--success))';
    feedbackText = 'Excellent match! Your resume aligns well with this position.';
  } else if (data.final_score > 50) {
    scoreBar.style.background = 'linear-gradient(90deg, var(--primary), var(--warning))';
    feedbackText = 'Good match, but could use some improvements.';
  } else {
    scoreBar.style.background = 'linear-gradient(90deg, var(--primary), var(--danger))';
    feedbackText = 'Needs significant improvements to match this job.';
  }
  document.getElementById('scoreFeedback').textContent = feedbackText;

  // Skills display
  const matchedSkillsDiv = document.getElementById('matchedSkills');
  matchedSkillsDiv.innerHTML = data.matched_skills.length > 0 ?
    data.matched_skills.map(skill => `
      <span class="skill-badge matched-skill">
        <i class="bi bi-check-circle"></i> ${skill}
      </span>
    `).join('') :
    '<span class="text-muted">No skills matched</span>';

  const missingSkillsDiv = document.getElementById('missingSkills');
  missingSkillsDiv.innerHTML = data.missing_skills.length > 0 ?
    data.missing_skills.map(skill => `
      <span class="skill-badge missing-skill">
        <i class="bi bi-exclamation-circle"></i> ${skill}
      </span>
    `).join('') :
    '<span class="text-muted">No missing skills</span>';

  // Resume length
  const resumeLength = data.resume_length || 0;
  document.getElementById('resumeLengthText').textContent = `${resumeLength} words`;
  document.getElementById('resumeLengthBar').style.width = `${Math.min(100, resumeLength/5)}%`;

  // Gemini Insights
  if (data.improvements || data.suggested_keywords) {
    const improvements = data.improvements || ['Focus on matching keywords from the job description'];
    const missingQualifications = data.missing_qualifications || ['Review the job description for required qualifications'];
    const suggestedKeywords = data.suggested_keywords || [];
    const formattingSuggestions = data.formatting_suggestions || 'Ensure your resume has clear sections and proper formatting';

    const insightsHtml = `
      <div class="suggestion-item">
        <h5><i class="bi bi-check-circle"></i> Key Improvements</h5>
        <ul>
          ${improvements.map(i => `<li>${i}</li>`).join('')}
        </ul>
      </div>
      
      <div class="suggestion-item">
        <h5><i class="bi bi-exclamation-triangle"></i> Missing Qualifications</h5>
        <ul>
          ${missingQualifications.map(m => `<li>${m}</li>`).join('')}
        </ul>
      </div>
      
      <div class="suggestion-item">
        <h5><i class="bi bi-tags"></i> Suggested Keywords</h5>
        <div>
          ${suggestedKeywords.map(k => `<span class="keyword-badge">${k}</span>`).join('')}
        </div>
      </div>
      
      <div class="suggestion-item">
        <h5><i class="bi bi-file-earmark-text"></i> Formatting Tips</h5>
        <p>${formattingSuggestions}</p>
      </div>
    `;

    document.getElementById('geminiInsights').innerHTML = insightsHtml;
    insightsCard.style.display = 'block';
  }

  // Show results
  resultsContainer.style.display = 'block';
}

// History Functions
function loadHistory() {
  // In a real app, this would load from your backend
  currentUser.history = [
    {
      id: 1,
      title: "Senior Software Engineer at TechCorp",
      date: "2023-05-15",
      score: 82,
      matched: ["Python", "AWS", "Docker"],
      missing: ["Kubernetes", "TensorFlow"]
    },
    {
      id: 2,
      title: "Full Stack Developer at WebSolutions",
      date: "2023-04-28",
      score: 65,
      matched: ["JavaScript", "React", "Node.js"],
      missing: ["GraphQL", "TypeScript"]
    }
  ];

  renderHistory();
}

function renderHistory() {
  if (currentUser.history.length === 0) {
    historyList.innerHTML = `
      <div class="empty-state">
        <i class="bi bi-folder-x"></i>
        <p>No analysis history yet</p>
      </div>
    `;
    return;
  }

  historyList.innerHTML = currentUser.history.map(item => `
    <div class="history-item" data-id="${item.id}">
      <div class="history-item-header">
        <span class="history-item-title">${item.title}</span>
        <span class="history-item-date">${item.date}</span>
      </div>
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <span class="me-3">Score: <span class="history-item-score">${item.score}%</span></span>
          <span class="text-success me-2">
            <i class="bi bi-check-circle"></i> ${item.matched.length} matched
          </span>
          <span class="text-danger">
            <i class="bi bi-exclamation-circle"></i> ${item.missing.length} missing
          </span>
        </div>
        <button class="btn btn-sm btn-outline-secondary">View</button>
      </div>
    </div>
  `).join('');
}

function addToHistory(data) {
  // Create a history item from the analysis data
  const jobTitle = document.getElementById('jobdesc').value
    .split('\n')[0]
    .substring(0, 50) + (document.getElementById('jobdesc').value.length > 50 ? '...' : '');

  const historyItem = {
    id: Date.now(),
    title: jobTitle || "Job Application Analysis",
    date: new Date().toISOString().split('T')[0],
    score: data.final_score,
    matched: data.matched_skills || [],
    missing: data.missing_skills || []
  };

  currentUser.history.unshift(historyItem);
  renderHistory();
}

// Event Listeners
historyBtn.addEventListener('click', (e) => {
  e.preventDefault();
  historyModal.show();
});

// In a real app, you would have more event listeners for:
// - User authentication
// - Viewing history items in detail
// - Saving/exporting results
// - etc.