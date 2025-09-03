<script type="module">
  // Import the functions you need from the SDKs you need
  import { initializeApp } from "https://www.gstatic.com/firebasejs/12.2.1/firebase-app.js";
  import { getAnalytics } from "https://www.gstatic.com/firebasejs/12.2.1/firebase-analytics.js";
  // TODO: Add SDKs for Firebase products that you want to use
  // https://firebase.google.com/docs/web/setup#available-libraries

  // Your web app's Firebase configuration
  // For Firebase JS SDK v7.20.0 and later, measurementId is optional
  const firebaseConfig = {
    apiKey: "AIzaSyDGl0vRx0Zo9rrUfeuMvZwXoHgUWpHV8Sg",
    authDomain: "aie-cpa-project-3.firebaseapp.com",
    projectId: "aie-cpa-project-3",
    storageBucket: "aie-cpa-project-3.firebasestorage.app",
    messagingSenderId: "1047061534699",
    appId: "1:1047061534699:web:4a9d2aee01bd9fe4ed2bae",
    measurementId: "G-2KQXRFYG6B"
  };

  // Initialize Firebase
  const app = initializeApp(firebaseConfig);
  const analytics = getAnalytics(app);
</script>