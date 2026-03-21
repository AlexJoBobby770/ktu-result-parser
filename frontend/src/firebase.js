import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyCaXzGKAUcVGzn79SRXST9nzL8D29VF3fk",
  authDomain: "ktu-result-parser.firebaseapp.com",
  projectId: "ktu-result-parser",
  storageBucket: "ktu-result-parser.firebasestorage.app",
  messagingSenderId: "811486921268",
  appId: "1:811486921268:web:d07262efc9d0998388c061",
  measurementId: "G-4FDP0KJFWE"
};


const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();