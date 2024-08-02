// src/App.js
import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import "./App.css";
import UploadForm from "./components/upload-form/UploadForm";
import UploadedFiles from "./components/uploaded-files/UploadedFiles";
import Authentication from "./components/authentication/Authentication";
import { UploadContextProvider } from "./hooks/useUploadContext";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(true);

  return (
    <Router>
      <UploadContextProvider>
        <main className="flex w-full lg:w-[1000px] m-auto flex-col justify-center items-center w-full py-10">
          <Routes>
            <Route
              path="/"
              element={
                isAuthenticated ? (
                  <>
                    <div className="w-full bg-indigo-900 p-10 rounded-tr-lg rounded-tl-lg">
                      <h1 className="text-white font-semibold leading-7 text-[35px]">
                        AI-Translate
                      </h1>
                      <p className="mt-1 text-sm leading-6 text-gray-200">
                        Upload your files below to get them AI-translated
                      </p>
                    </div>
                    <div className="flex flex-col gap-10">
                      <UploadForm />
                      <UploadedFiles />
                    </div>
                  </>
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
            <Route
              path="/login"
              element={<Authentication onLogin={() => setIsAuthenticated(true)} />}
            />
          </Routes>
        </main>
        <footer className="text-center w-full pb-7">
          <p>&copy; 2024 All rights reserved.</p>
        </footer>
      </UploadContextProvider>
    </Router>
  );
}

export default App;
