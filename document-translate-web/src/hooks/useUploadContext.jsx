import { createContext, useContext, useState } from "react";

const UploadContext = createContext();

export const UploadContextProvider = ({ children }) => {
  const [isFileUploaded, setIsFileUploaded] = useState(false);

  return (
    <UploadContext.Provider value={{ isFileUploaded, setIsFileUploaded }}>
      {children}
    </UploadContext.Provider>
  );
};

export const useUploadContext = () => useContext(UploadContext);
