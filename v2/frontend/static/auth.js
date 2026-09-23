// Firebase Web Auth Modular Setup (v10 compat/standalone CDN import)
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { 
  getAuth, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signInWithPopup, 
  GoogleAuthProvider, 
  onAuthStateChanged, 
  signOut 
} from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { showToast, setTokenProvider } from "./utils.js";

const firebaseConfig = {
  apiKey: "AIzaSyBh1w82RAnyiSbdkPTJZLRGE7lEGbjl3Tc",
  authDomain: "qwiklabs-gcp-04-7459370ad109.firebaseapp.com",
  projectId: "qwiklabs-gcp-04-7459370ad109",
  storageBucket: "qwiklabs-gcp-04-7459370ad109.firebasestorage.app",
  messagingSenderId: "754395904178",
  appId: "1:754395904178:web:dad53b95b805d58a56b1ab"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

let currentIdToken = null;
let currentUser = null;

// Provide token dynamically to utils.api
setTokenProvider(() => currentIdToken || "demo-token-taylor_27");

export function initAuth(onAuthSuccess, onAuthRequired) {
  onAuthStateChanged(auth, async (user) => {
    if (user) {
      currentUser = user;
      currentIdToken = await user.getIdToken(true);
      // Auto-refresh token every 45 minutes
      setInterval(async () => {
        if (auth.currentUser) {
          currentIdToken = await auth.currentUser.getIdToken(true);
        }
      }, 45 * 60 * 1000);
      onAuthSuccess(user);
    } else {
      currentUser = null;
      // In local dev, allow seamless fallback or modal
      onAuthRequired();
    }
  });
}

export async function loginWithEmail(email, password) {
  try {
    const cred = await signInWithEmailAndPassword(auth, email, password);
    currentIdToken = await cred.user.getIdToken();
    showToast("Signed in successfully!", "success");
    return cred.user;
  } catch (err) {
    showToast(`Login failed: ${err.message}`, "error");
    throw err;
  }
}

export async function registerWithEmail(email, password) {
  try {
    const cred = await createUserWithEmailAndPassword(auth, email, password);
    currentIdToken = await cred.user.getIdToken();
    showToast("Account created successfully!", "success");
    return cred.user;
  } catch (err) {
    showToast(`Registration failed: ${err.message}`, "error");
    throw err;
  }
}

export async function loginWithGoogle() {
  try {
    const res = await signInWithPopup(auth, googleProvider);
    currentIdToken = await res.user.getIdToken();
    showToast("Signed in with Google!", "success");
    return res.user;
  } catch (err) {
    showToast(`Google Sign-In: ${err.message}`, "error");
    throw err;
  }
}

export async function logoutUser() {
  await signOut(auth);
  currentIdToken = null;
  showToast("Signed out", "info");
  location.reload();
}
