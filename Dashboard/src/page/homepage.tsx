import { useEffect, useState } from "react";
import { initializeApp } from "firebase/app";
import {
  getFirestore,
  collection,
  getDocs,
  onSnapshot,
  deleteDoc,
  doc,
} from "firebase/firestore";

const firebaseConfig = {
  apiKey: "fillhere",
  authDomain: "fillhere",
  projectId: "fillhere",
  storageBucket: "fillhere",
  messagingSenderId: "fillhere",
  appId: "fillhere",
  measurementId: "fillhere",
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

export default function HomePage() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const unsubscribe = onSnapshot(collection(db, "alerts"), (snapshot) => {
      const data = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }));
      console.log("Fetched data:", data);
      setAlerts(data);
    });
    return () => unsubscribe();
  }, []);

  async function clearLogs() {
    try {
      const collectionRef = collection(db, "alerts");
      const querySnapshot = await getDocs(collectionRef);
      const deletePromises = querySnapshot.docs.map((document) =>
        deleteDoc(doc(db, "alerts", document.id)),
      );
      await Promise.all(deletePromises);
      console.log("Collection cleared.");
    } catch (error) {
      console.log("Error clearing collection: ", error);
    }
  }

  return (
    <div className="h-full w-full justify-center items-center flex flex-col">
      <div className="my-[5vh]">
        <p className="text-5xl">Dashboard</p>
      </div>
      <div className="my-[2vh]">
        <p className="text-2xl">Logs</p>
      </div>
      <div className="my-[2vh] h-[60vh] w-[75vw] overflow-scroll border-2 border-[#9ca3af] pt-4">
        {alerts.map((alert) => (
          <div key={alert.id} className="grid grid-cols-3 w-full gap-[4vw]">
            <p className="text-xl">
              {alert.duration > 2.0 ? "❗ Critical Warning: " : "⚠️ Warning: "}
              {alert.message}
            </p>
            <p className="text-xl">Time: {alert.time}</p>
            <p className="text-xl">Duration: {alert.duration}s</p>
          </div>
        ))}
      </div>
      <div className="my-[2vh]">
      <button
        onClick={clearLogs}
        className="rounded-2xl bg-red-900 w-25 h-10 hover:bg-gray-500 cursor-pointer"
      >
        Reset Logs
      </button>
      </div>
    </div>
  );
}
