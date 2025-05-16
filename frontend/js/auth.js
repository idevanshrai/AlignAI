// Supabase Configuration
const supabaseUrl = 'YOUR_SUPABASE_URL';
const supabaseKey = 'YOUR_SUPABASE_ANON_KEY';
const supabase = supabase.createClient(supabaseUrl, supabaseKey);

// DOM Elements
const loginTab = document.getElementById('loginTab');
const signupTab = document.getElementById('signupTab');
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const googleLoginBtn = document.getElementById('googleLogin');
const githubLoginBtn = document.getElementById('githubLogin');
const guestLoginBtn = document.getElementById('guestLogin');
const forgotPasswordLink = document.getElementById('forgotPassword');
const showPasswordBtns = document.querySelectorAll('.show-password');
const guestModal = document.getElementById('guestModal');
const confirmGuestBtn = document.getElementById('confirmGuest');
const cancelGuestBtn = document.getElementById('cancelGuest');

// Initialize the login page
document.addEventListener('DOMContentLoaded', () => {
  initBackground();
  setupTabSwitching();
  setupPasswordToggle();
  setupFormSubmissions();
  setupGuestMode();

  // Check if user is already logged in
  checkAuthState();
});

// Create circuit board background
function initBackground() {
  const overlay = document.querySelector('.circuit-overlay');
  const circuitSVG = `
    <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
          <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(100,181,246,0.1)" stroke-width="0.5"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid)"/>
      <circle cx="20%" cy="30%" r="2" fill="rgba(100,181,246,0.5)"/>
      <circle cx="75%" cy="45%" r="3" fill="rgba(100,181,246,0.7)"/>
      <path d="M20,20 Q50,10 80,20 T140,20" stroke="rgba(100,181,246,0.3)" fill="none" stroke-width="1"/>
    </svg>
  `;
  overlay.innerHTML = circuitSVG;
}

// Tab switching between login/signup
function setupTabSwitching() {
  loginTab.addEventListener('click', () => switchTab('login'));
  signupTab.addEventListener('click', () => switchTab('signup'));
}

function switchTab(tab) {
  if (tab === 'login') {
    loginTab.classList.add('active');
    signupTab.classList.remove('active');
    loginForm.classList.add('active');
    signupForm.classList.remove('active');
  } else {
    signupTab.classList.add('active');
    loginTab.classList.remove('active');
    signupForm.classList.add('active');
    loginForm.classList.remove('active');
  }
}

// Password visibility toggle
function setupPasswordToggle() {
  showPasswordBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const input = e.currentTarget.parentElement.querySelector('input');
      const icon = e.currentTarget.querySelector('i');

      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
      } else {
        input.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
      }
    });
  });
}

// Form submissions
function setupFormSubmissions() {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    await handleLogin(email, password);
  });

  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (password !== confirmPassword) {
      showError(signupForm, "Passwords don't match");
      return;
    }

    await handleSignup(name, email, password);
  });

  googleLoginBtn.addEventListener('click', () => handleSocialLogin('google'));
  githubLoginBtn.addEventListener('click', () => handleSocialLogin('github'));

  forgotPasswordLink.addEventListener('click', (e) => {
    e.preventDefault();
    const email = prompt('Enter your email to reset password:');
    if (email) handlePasswordReset(email);
  });
}

// Guest mode functionality
function setupGuestMode() {
  guestLoginBtn.addEventListener('click', () => {
    guestModal.style.display = 'flex';
  });

  confirmGuestBtn.addEventListener('click', () => {
    sessionStorage.setItem('guestMode', 'true');
    window.location.href = 'index.html';
  });

  cancelGuestBtn.addEventListener('click', () => {
    guestModal.style.display = 'none';
    switchTab('signup');
  });

  // Close modal when clicking outside
  window.addEventListener('click', (e) => {
    if (e.target === guestModal) {
      guestModal.style.display = 'none';
    }
  });
}

// Authentication functions
async function handleLogin(email, password) {
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });

    if (error) throw error;

    // Successful login - redirect to app
    window.location.href = 'index.html';
  } catch (error) {
    showError(loginForm, error.message);
  }
}

async function handleSignup(name, email, password) {
  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: name
        }
      }
    });

    if (error) throw error;

    alert('Account created! Please check your email for verification.');
    switchTab('login');
  } catch (error) {
    showError(signupForm, error.message);
  }
}

async function handleSocialLogin(provider) {
  try {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: window.location.origin + '/index.html'
      }
    });

    if (error) throw error;
  } catch (error) {
    showError(document.querySelector('.auth-form.active'), error.message);
  }
}

async function handlePasswordReset(email) {
  try {
    const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: window.location.origin + '/update-password.html'
    });

    if (error) throw error;

    alert('Password reset link sent to your email');
  } catch (error) {
    showError(loginForm, error.message);
  }
}

function checkAuthState() {
  supabase.auth.getSession().then(({ data: { session } }) => {
    if (session) {
      window.location.href = 'index.html';
    }
  });

  supabase.auth.onAuthStateChange((event, session) => {
    if (event === 'SIGNED_IN') {
      window.location.href = 'index.html';
    }
  });
}

function showError(form, message) {
  let errorElement = form.querySelector('.error-message');
  if (!errorElement) {
    errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    form.insertBefore(errorElement, form.querySelector('button[type="submit"]'));
  }
  errorElement.textContent = message;
}